from __future__ import annotations

import math
from pathlib import Path

import cv2
import numpy as np

from .common import xywh_to_xyxy, xyxy_to_xywh


def _cuda_status(value):
    return value[0] if isinstance(value, tuple) else value


class OSTrackTracker:
    def __init__(
        self,
        engine: str,
        device: str = "cuda",
        template_factor: float = 2.0,
        search_factor: float = 4.0,
        template_size: int = 128,
        search_size: int = 256,
        score_threshold: float = 0.35,
        template_update_score: float = 0.70,
        template_update_interval: int = 8,
        max_lost_count: int = 8,
        min_size_scale: float = 0.45,
        max_size_scale: float = 2.20,
        max_size_growth_per_frame: float = 0.10,
        max_size_shrink_per_frame: float = 0.18,
        max_aspect_change: float = 1.80,
        size_smooth_alpha: float = 0.70,
    ) -> None:
        if not engine or not Path(engine).exists():
            raise FileNotFoundError(f"OSTrack TensorRT engine not found: {engine}")
        self.engine_path = engine
        self.template_factor = float(template_factor)
        self.search_factor = float(search_factor)
        self.template_size = int(template_size)
        self.search_size = int(search_size)
        self.score_threshold = float(score_threshold)
        self.template_update_score = float(template_update_score)
        self.template_update_interval = max(1, int(template_update_interval))
        self.max_lost_count = max(1, int(max_lost_count))
        self.min_size_scale = max(0.05, float(min_size_scale))
        self.max_size_scale = max(self.min_size_scale, float(max_size_scale))
        self.max_size_growth_per_frame = max(0.0, float(max_size_growth_per_frame))
        self.max_size_shrink_per_frame = max(0.0, float(max_size_shrink_per_frame))
        self.max_aspect_change = max(1.0, float(max_aspect_change))
        self.size_smooth_alpha = max(0.0, min(0.98, float(size_smooth_alpha)))
        self.initialized = False
        self.state_xywh: list[float] | None = None
        self.init_xywh: list[float] | None = None
        self.lost_count = 0
        self.frame_id = 0
        self._load_engine()

    def _load_engine(self) -> None:
        import tensorrt as trt
        from cuda import cudart

        self.trt = trt
        self.cudart = cudart
        logger = trt.Logger(trt.Logger.WARNING)
        with open(self.engine_path, "rb") as f:
            runtime = trt.Runtime(logger)
            self.engine = runtime.deserialize_cuda_engine(f.read())
        if self.engine is None:
            raise RuntimeError(f"failed to load OSTrack engine: {self.engine_path}")
        self.context = self.engine.create_execution_context()
        err, stream = cudart.cudaStreamCreate()
        err = _cuda_status(err)
        if err != cudart.cudaError_t.cudaSuccess:
            raise RuntimeError(f"cudaStreamCreate failed: {err}")
        self.stream = stream
        self.device_ptrs: dict[str, int] = {}
        self.host: dict[str, np.ndarray] = {}
        for i in range(self.engine.num_io_tensors):
            name = self.engine.get_tensor_name(i)
            shape = tuple(self.engine.get_tensor_shape(name))
            dtype = trt.nptype(self.engine.get_tensor_dtype(name))
            host = np.empty(shape, dtype=dtype)
            err, ptr = cudart.cudaMalloc(host.nbytes)
            err = _cuda_status(err)
            if err != cudart.cudaError_t.cudaSuccess:
                raise RuntimeError(f"cudaMalloc failed for {name}: {err}")
            self.host[name] = host
            self.device_ptrs[name] = int(ptr)
            self.context.set_tensor_address(name, int(ptr))
        z_shape = tuple(self.host["z"].shape)
        x_shape = tuple(self.host["x"].shape)
        self.template_size = int(z_shape[-1])
        self.search_size = int(x_shape[-1])
        self.feat_sz = int(self.host["score_map"].shape[-1])
        if self.template_size >= 192:
            self.template_factor = 2.0
            self.search_factor = 5.0
        self.window = self._hann2d(self.feat_sz)

    def init(self, frame, bbox_xyxy) -> bool:
        bbox_xywh = list(map(float, xyxy_to_xywh(bbox_xyxy)))
        if bbox_xywh[2] <= 2 or bbox_xywh[3] <= 2:
            return False
        self.state_xywh = bbox_xywh
        self.init_xywh = bbox_xywh.copy()
        self.template = self._crop_and_preprocess(frame, bbox_xywh, self.template_factor, self.template_size)[0]
        self.initialized = True
        self.lost_count = 0
        self.frame_id = 0
        return True

    def update(self, frame):
        if not self.initialized or self.state_xywh is None:
            return None, 0.0, False
        self.frame_id += 1
        try:
            search, resize_factor = self._crop_and_preprocess(frame, self.state_xywh, self.search_factor, self.search_size)
            score_map, size_map, offset_map = self._infer(self.template, search)
            bbox_xywh, score = self._decode(score_map, size_map, offset_map, resize_factor, frame.shape[:2])
            bbox_xywh = self._constrain_bbox_size(bbox_xywh, frame.shape[:2])
            self.state_xywh = bbox_xywh
            ok = score >= self.score_threshold
            if ok:
                self.lost_count = 0
                if score >= self.template_update_score and self.frame_id % self.template_update_interval == 0:
                    self.template = self._crop_and_preprocess(frame, self.state_xywh, self.template_factor, self.template_size)[0]
                return xywh_to_xyxy(tuple(self.state_xywh)), float(score), True
            self.lost_count += 1
            bbox_xyxy = xywh_to_xyxy(tuple(self.state_xywh))
            if self.lost_count >= self.max_lost_count:
                self.reset()
            return bbox_xyxy, float(score), False
        except Exception as exc:
            self.lost_count += 1
            print(f"WARN: OSTrack update failed: {exc}", flush=True)
            if self.lost_count >= self.max_lost_count:
                self.reset()
            return None, 0.0, False

    def reset(self) -> None:
        self.initialized = False
        self.state_xywh = None
        self.init_xywh = None
        self.lost_count = 0
        self.frame_id = 0
        if hasattr(self, "template"):
            del self.template

    def _infer(self, template: np.ndarray, search: np.ndarray):
        cudart = self.cudart
        for name, arr in {"z": template, "x": search}.items():
            host = self.host[name]
            np.copyto(host, arr.astype(host.dtype, copy=False))
            err = cudart.cudaMemcpyAsync(
                self.device_ptrs[name],
                host.ctypes.data,
                host.nbytes,
                cudart.cudaMemcpyKind.cudaMemcpyHostToDevice,
                self.stream,
            )
            err = _cuda_status(err)
            if err != cudart.cudaError_t.cudaSuccess:
                raise RuntimeError(f"cudaMemcpyAsync H2D failed for {name}: {err}")
        if not self.context.execute_async_v3(self.stream):
            raise RuntimeError("TensorRT execute_async_v3 failed")
        outputs = []
        for name in ("score_map", "size_map", "offset_map"):
            host = self.host[name]
            err = cudart.cudaMemcpyAsync(
                host.ctypes.data,
                self.device_ptrs[name],
                host.nbytes,
                cudart.cudaMemcpyKind.cudaMemcpyDeviceToHost,
                self.stream,
            )
            err = _cuda_status(err)
            if err != cudart.cudaError_t.cudaSuccess:
                raise RuntimeError(f"cudaMemcpyAsync D2H failed for {name}: {err}")
            outputs.append(host.copy())
        err = cudart.cudaStreamSynchronize(self.stream)
        err = _cuda_status(err)
        if err != cudart.cudaError_t.cudaSuccess:
            raise RuntimeError(f"cudaStreamSynchronize failed: {err}")
        return outputs

    def _decode(self, score_map, size_map, offset_map, resize_factor: float, frame_hw):
        assert self.state_xywh is not None
        scores = score_map.reshape(-1).astype(np.float32)
        weighted = scores * self.window
        max_idx = int(np.argmax(weighted))
        score = float(scores[max_idx])
        fy = max_idx // self.feat_sz
        fx = max_idx % self.feat_sz
        offset = offset_map.reshape(1, 2, self.feat_sz, self.feat_sz)
        sizes = size_map.reshape(1, 2, self.feat_sz, self.feat_sz)
        cx = float(fx + offset[0, 0, fy, fx]) / float(self.feat_sz)
        cy = float(fy + offset[0, 1, fy, fx]) / float(self.feat_sz)
        bw = float(sizes[0, 0, fy, fx])
        bh = float(sizes[0, 1, fy, fx])
        cx = cx * self.search_size / resize_factor
        cy = cy * self.search_size / resize_factor
        bw = bw * self.search_size / resize_factor
        bh = bh * self.search_size / resize_factor
        prev_x, prev_y, prev_w, prev_h = self.state_xywh
        prev_cx = prev_x + 0.5 * prev_w
        prev_cy = prev_y + 0.5 * prev_h
        half_side = 0.5 * self.search_size / resize_factor
        cx_real = cx + (prev_cx - half_side)
        cy_real = cy + (prev_cy - half_side)
        h, w = int(frame_hw[0]), int(frame_hw[1])
        x = max(0.0, min(float(w - 5), cx_real - 0.5 * bw))
        y = max(0.0, min(float(h - 5), cy_real - 0.5 * bh))
        bw = max(5.0, min(float(w) - x, bw))
        bh = max(5.0, min(float(h) - y, bh))
        return [x, y, bw, bh], score

    def _constrain_bbox_size(self, bbox_xywh: list[float], frame_hw) -> list[float]:
        if self.state_xywh is None or self.init_xywh is None:
            return bbox_xywh
        x, y, bw, bh = map(float, bbox_xywh)
        prev_x, prev_y, prev_w, prev_h = map(float, self.state_xywh)
        init_w = max(2.0, float(self.init_xywh[2]))
        init_h = max(2.0, float(self.init_xywh[3]))
        prev_w = max(2.0, prev_w)
        prev_h = max(2.0, prev_h)

        min_w = max(5.0, init_w * self.min_size_scale, prev_w * (1.0 - self.max_size_shrink_per_frame))
        min_h = max(5.0, init_h * self.min_size_scale, prev_h * (1.0 - self.max_size_shrink_per_frame))
        max_w = min(init_w * self.max_size_scale, prev_w * (1.0 + self.max_size_growth_per_frame))
        max_h = min(init_h * self.max_size_scale, prev_h * (1.0 + self.max_size_growth_per_frame))
        bw = min(max(bw, min_w), max_w)
        bh = min(max(bh, min_h), max_h)

        init_aspect = init_w / init_h
        min_aspect = init_aspect / self.max_aspect_change
        max_aspect = init_aspect * self.max_aspect_change
        aspect = bw / max(1e-6, bh)
        if aspect < min_aspect:
            bw = min(max_w, max(min_w, bh * min_aspect))
        elif aspect > max_aspect:
            bh = min(max_h, max(min_h, bw / max_aspect))

        alpha = self.size_smooth_alpha
        bw = alpha * prev_w + (1.0 - alpha) * bw
        bh = alpha * prev_h + (1.0 - alpha) * bh

        cx = x + 0.5 * float(bbox_xywh[2])
        cy = y + 0.5 * float(bbox_xywh[3])
        h, w = int(frame_hw[0]), int(frame_hw[1])
        x = max(0.0, min(float(w - 5), cx - 0.5 * bw))
        y = max(0.0, min(float(h - 5), cy - 0.5 * bh))
        bw = max(5.0, min(float(w) - x, bw))
        bh = max(5.0, min(float(h) - y, bh))
        return [x, y, bw, bh]

    def _crop_and_preprocess(self, frame, bbox_xywh, factor: float, output_size: int):
        patch, resize_factor = self._sample_target(frame, bbox_xywh, factor, output_size)
        patch = cv2.cvtColor(patch, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        patch = (patch - mean) / std
        chw = np.transpose(patch, (2, 0, 1))[None, ...].astype(np.float32, copy=False)
        return chw, resize_factor

    @staticmethod
    def _sample_target(frame, bbox_xywh, factor: float, output_size: int):
        x, y, bw, bh = map(float, bbox_xywh)
        cx = x + 0.5 * bw
        cy = y + 0.5 * bh
        crop_sz = max(2, int(math.ceil(math.sqrt(max(1.0, bw * bh)) * factor)))
        x1 = int(round(cx - 0.5 * crop_sz))
        y1 = int(round(cy - 0.5 * crop_sz))
        x2 = x1 + crop_sz
        y2 = y1 + crop_sz
        h, w = frame.shape[:2]
        left = max(0, -x1)
        top = max(0, -y1)
        right = max(0, x2 - w + 1)
        bottom = max(0, y2 - h + 1)
        if left or top or right or bottom:
            padded = cv2.copyMakeBorder(frame, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114))
            x1 += left
            y1 += top
        else:
            padded = frame
        patch = padded[y1:y1 + crop_sz, x1:x1 + crop_sz]
        patch = cv2.resize(patch, (output_size, output_size), interpolation=cv2.INTER_LINEAR)
        return patch, float(output_size) / float(crop_sz)

    @staticmethod
    def _hann2d(size: int) -> np.ndarray:
        hann1d = np.array([0.5 - 0.5 * math.cos(2.0 * math.pi * (i + 1) / float(size + 1)) for i in range(size)], dtype=np.float32)
        return np.outer(hann1d, hann1d).reshape(-1)
