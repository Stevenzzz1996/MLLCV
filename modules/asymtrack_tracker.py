from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import torch

from .common import xywh_to_xyxy, xyxy_to_xywh


def _cuda_status(value):
    return value[0] if isinstance(value, tuple) else value


class AsymTrackTracker:
    def __init__(
        self,
        backend: str = "pytorch",
        model: str | None = None,
        engine: str | None = None,
        repo_root: str = "third_party/AsymTrack",
        yaml_name: str = "tiny",
        device: str = "cuda",
        max_lost_count: int = 10,
    ) -> None:
        self.backend = backend
        self.model = model or "/home/mll/Downloads/AsymTrack_ep0500.pth.tar"
        self.engine_path = engine or model
        self.repo_root = Path(repo_root).resolve()
        self.yaml_name = yaml_name
        self.device = torch.device(device if device == "cuda" and torch.cuda.is_available() else "cpu")
        self.max_lost_count = max_lost_count
        self.initialized = False
        self.lost_count = 0
        self.state_xywh: list[float] | None = None
        self.frame_id = 0

        self._load_asymtrack_helpers()
        if self.backend == "pytorch":
            self._load_pytorch_network()
        elif self.backend in {"tensorrt", "engine"}:
            self._load_trt_engine()
        else:
            raise NotImplementedError(f"unsupported AsymTrack backend: {backend}")

    def _load_asymtrack_helpers(self) -> None:
        if not self.repo_root.exists():
            raise FileNotFoundError(f"AsymTrack repo not found: {self.repo_root}")
        repo = str(self.repo_root)
        if repo not in sys.path:
            sys.path.insert(0, repo)

        old_cwd = os.getcwd()
        os.chdir(repo)
        try:
            from lib.config.AsymTrack.config import cfg, update_config_from_file
            from lib.test.tracker.vittrack_utils import Preprocessor, sample_target
            from lib.utils.box_ops import clip_box

            yaml_file = self.repo_root / "experiments" / "AsymTrack" / f"{self.yaml_name}.yaml"
            update_config_from_file(str(yaml_file))
            cfg.TEST_MODE = True
            self.cfg = cfg
            self.template_factor = cfg.TEST.TEMPLATE_FACTOR
            self.template_size = cfg.TEST.TEMPLATE_SIZE
            self.search_factor = cfg.TEST.SEARCH_FACTOR
            self.search_size = cfg.TEST.SEARCH_SIZE
            self.sample_target = sample_target
            self.clip_box = clip_box
            self.preprocessor = Preprocessor()
        finally:
            os.chdir(old_cwd)

    def _load_pytorch_network(self) -> None:
        if not Path(self.model).exists():
            raise FileNotFoundError(f"AsymTrack checkpoint not found: {self.model}")

        old_cwd = os.getcwd()
        os.chdir(self.repo_root)
        try:
            from lib.models.AsymTrack import build_asymtrack

            network = build_asymtrack(self.cfg)
            checkpoint = torch.load(self.model, map_location="cpu")
            network.load_state_dict(checkpoint["net"], strict=True)
            network.backbone.switch_to_deploy()
            self.network = network.to(self.device).eval()
        finally:
            os.chdir(old_cwd)

    def _load_trt_engine(self) -> None:
        if not self.engine_path or not Path(self.engine_path).exists():
            raise FileNotFoundError(f"AsymTrack TensorRT engine not found: {self.engine_path}")
        import tensorrt as trt
        from cuda import cudart

        self.trt = trt
        self.cudart = cudart
        self.trt_logger = trt.Logger(trt.Logger.WARNING)
        with open(self.engine_path, "rb") as f:
            runtime = trt.Runtime(self.trt_logger)
            self.trt_engine = runtime.deserialize_cuda_engine(f.read())
        self.trt_context = self.trt_engine.create_execution_context()
        err, stream = cudart.cudaStreamCreate()
        err = _cuda_status(err)
        if err != cudart.cudaError_t.cudaSuccess:
            raise RuntimeError(f"cudaStreamCreate failed: {err}")
        self.trt_stream = stream
        self.trt_bindings = {}
        self.trt_host = {}
        for i in range(self.trt_engine.num_io_tensors):
            name = self.trt_engine.get_tensor_name(i)
            shape = tuple(self.trt_engine.get_tensor_shape(name))
            dtype = trt.nptype(self.trt_engine.get_tensor_dtype(name))
            host = np.empty(shape, dtype=dtype)
            nbytes = host.nbytes
            err, ptr = cudart.cudaMalloc(nbytes)
            err = _cuda_status(err)
            if err != cudart.cudaError_t.cudaSuccess:
                raise RuntimeError(f"cudaMalloc failed for {name}: {err}")
            self.trt_bindings[name] = int(ptr)
            self.trt_host[name] = host
            self.trt_context.set_tensor_address(name, int(ptr))

    def _trt_infer(self, search, template):
        cudart = self.cudart
        search_np = search.detach().cpu().numpy().astype(np.float32, copy=False)
        template_np = template.detach().cpu().numpy().astype(np.float32, copy=False)
        inputs = {"search": search_np, "template": template_np}
        for name, arr in inputs.items():
            host = self.trt_host[name]
            np.copyto(host, arr)
            err = cudart.cudaMemcpyAsync(
                self.trt_bindings[name],
                host.ctypes.data,
                host.nbytes,
                cudart.cudaMemcpyKind.cudaMemcpyHostToDevice,
                self.trt_stream,
            )
            err = _cuda_status(err)
            if err != cudart.cudaError_t.cudaSuccess:
                raise RuntimeError(f"cudaMemcpyAsync H2D failed for {name}: {err}")
        if not self.trt_context.execute_async_v3(self.trt_stream):
            raise RuntimeError("TensorRT execute_async_v3 failed")
        out_name = "pred_boxes"
        out = self.trt_host[out_name]
        err = cudart.cudaMemcpyAsync(
            out.ctypes.data,
            self.trt_bindings[out_name],
            out.nbytes,
            cudart.cudaMemcpyKind.cudaMemcpyDeviceToHost,
            self.trt_stream,
        )
        err = _cuda_status(err)
        if err != cudart.cudaError_t.cudaSuccess:
            raise RuntimeError(f"cudaMemcpyAsync D2H failed: {err}")
        err = cudart.cudaStreamSynchronize(self.trt_stream)
        err = _cuda_status(err)
        if err != cudart.cudaError_t.cudaSuccess:
            raise RuntimeError(f"cudaStreamSynchronize failed: {err}")
        return np.array(out, copy=True)

    def init(self, frame, bbox_xyxy) -> bool:
        bbox_xywh = list(map(float, xyxy_to_xywh(bbox_xyxy)))
        if bbox_xywh[2] <= 1 or bbox_xywh[3] <= 1:
            return False
        z_patch_arr, _ = self.sample_target(frame, bbox_xywh, self.template_factor, output_sz=self.template_size)
        template = self.preprocessor.process(z_patch_arr)
        self.template = template if self.backend in {"tensorrt", "engine"} else template.to(self.device)
        self.state_xywh = bbox_xywh
        self.frame_id = 0
        self.lost_count = 0
        self.initialized = True
        return True

    def update(self, frame):
        if not self.initialized or self.state_xywh is None:
            return None, 0.0, False
        h, w = frame.shape[:2]
        self.frame_id += 1
        try:
            x_patch_arr, resize_factor = self.sample_target(
                frame, self.state_xywh, self.search_factor, output_sz=self.search_size
            )
            search = self.preprocessor.process(x_patch_arr)
            if self.backend in {"tensorrt", "engine"}:
                pred_boxes = self._trt_infer(search, self.template).reshape(-1, 4)
                if not np.all(np.isfinite(pred_boxes)):
                    raise RuntimeError("AsymTrack TensorRT output contains NaN/Inf")
                pred_box = (pred_boxes.mean(axis=0) * self.search_size / resize_factor).tolist()
            else:
                search = search.to(self.device)
                with torch.no_grad():
                    xz = self.network.forward_backbone([search, self.template], train=False)
                    out_dict, _, _ = self.network.forward_head(xz=xz)
                pred_boxes = out_dict["pred_boxes"].view(-1, 4)
                pred_box = (pred_boxes.mean(dim=0) * self.search_size / resize_factor).detach().cpu().tolist()
                if not np.all(np.isfinite(pred_box)):
                    raise RuntimeError("AsymTrack PyTorch output contains NaN/Inf")
            self.state_xywh = self._clip_box(self._map_box_back(pred_box, resize_factor), h, w)
            self.lost_count = 0
            return xywh_to_xyxy(tuple(self.state_xywh)), 1.0, True
        except Exception as exc:
            self.lost_count += 1
            print(f"WARN: AsymTrack update failed: {exc}")
            if self.lost_count >= self.max_lost_count:
                self.reset()
            return None, 0.0, False

    def _map_box_back(self, pred_box: list[float], resize_factor: float):
        assert self.state_xywh is not None
        cx_prev = self.state_xywh[0] + 0.5 * self.state_xywh[2]
        cy_prev = self.state_xywh[1] + 0.5 * self.state_xywh[3]
        cx, cy, w, h = pred_box
        half_side = 0.5 * self.search_size / resize_factor
        cx_real = cx + (cx_prev - half_side)
        cy_real = cy + (cy_prev - half_side)
        return [cx_real - 0.5 * w, cy_real - 0.5 * h, w, h]

    def _clip_box(self, box_xywh, h: int, w: int):
        return self.clip_box(box_xywh, h, w, margin=10)

    def reset(self) -> None:
        self.state_xywh = None
        self.initialized = False
        self.lost_count = 0
        if hasattr(self, "template"):
            del self.template
