from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.asymtrack_tracker import AsymTrackTracker
from modules.common import bbox_center, bbox_iou, xywh_to_xyxy


def center_error(a, b) -> float:
    ax, ay = a
    bx, by = b
    return float(math.hypot(ax - bx, ay - by))


def read_gt(path: Path) -> list[tuple[float, float, float, float]]:
    boxes = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            parts = [p for p in line.replace("\t", ",").replace(" ", ",").split(",") if p.strip()]
            if len(parts) < 4:
                continue
            x, y, w, h = map(float, parts[:4])
            boxes.append((x, y, w, h))
    return boxes


def load_frame(image_path: Path):
    frame = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if frame is None:
        raise RuntimeError(f"failed to read image: {image_path}")
    return frame


def discover_sequences(root: Path) -> list[Path]:
    seqs = []
    for path in sorted(root.glob("Sequence_*")):
        if (path / "images").is_dir() and (path / "annotations" / "groundtruth.txt").exists():
            seqs.append(path)
    return seqs


def map_box_back(pred_box: list[float], state_xywh, search_size: int, resize_factor: float):
    x, y, w, h = state_xywh
    cx_prev = x + 0.5 * w
    cy_prev = y + 0.5 * h
    cx, cy, pw, ph = pred_box
    half_side = 0.5 * search_size / resize_factor
    cx_real = cx + (cx_prev - half_side)
    cy_real = cy + (cy_prev - half_side)
    return (cx_real - 0.5 * pw, cy_real - 0.5 * ph, cx_real + 0.5 * pw, cy_real + 0.5 * ph)


def summarize(values):
    arr = np.asarray([v for v in values if v is not None and np.isfinite(v)], dtype=np.float64)
    if arr.size == 0:
        return {"mean": None, "p95": None, "max": None}
    return {
        "mean": float(arr.mean()),
        "p95": float(np.percentile(arr, 95)),
        "max": float(arr.max()),
    }


def raw_pytorch_forward(tracker: AsymTrackTracker, search, template):
    if hasattr(tracker.network.backbone, "tempinit"):
        tracker.network.backbone.tempinit = False
    if hasattr(tracker.network.backbone, "fuselist"):
        tracker.network.backbone.fuselist = []
    with torch.no_grad():
        xz = tracker.network.forward_backbone([search.to(tracker.device), template.to(tracker.device)], train=False)
        out_dict, _, _ = tracker.network.forward_head(xz=xz)
    return out_dict["pred_boxes"].detach().cpu().numpy()


def run_sequence(args, seq_dir: Path):
    image_paths = sorted((seq_dir / "images").glob("*.jpg"))
    gt_xywh = read_gt(seq_dir / "annotations" / "groundtruth.txt")
    n = min(len(image_paths), len(gt_xywh))
    if args.max_frames:
        n = min(n, args.max_frames)
    if n < 2:
        raise RuntimeError(f"sequence too short: {seq_dir}")

    first_frame = load_frame(image_paths[0])
    init_xyxy = xywh_to_xyxy(gt_xywh[0])

    raw_ref = AsymTrackTracker(
        backend="pytorch",
        model=args.checkpoint,
        repo_root=args.repo_root,
        yaml_name=args.yaml_name,
        device=args.device,
    )
    raw_trt = AsymTrackTracker(
        backend="tensorrt",
        model=args.checkpoint,
        engine=args.engine,
        repo_root=args.repo_root,
        yaml_name=args.yaml_name,
        device=args.device,
    )
    py_track = AsymTrackTracker(
        backend="pytorch",
        model=args.checkpoint,
        repo_root=args.repo_root,
        yaml_name=args.yaml_name,
        device=args.device,
    )
    trt_track = AsymTrackTracker(
        backend="tensorrt",
        model=args.checkpoint,
        engine=args.engine,
        repo_root=args.repo_root,
        yaml_name=args.yaml_name,
        device=args.device,
    )
    for tracker in (raw_ref, raw_trt, py_track, trt_track):
        if not tracker.init(first_frame, init_xyxy):
            raise RuntimeError(f"tracker init failed: {seq_dir}")

    rows = []
    raw_abs_mean = []
    raw_abs_max = []
    raw_center_px = []
    raw_iou = []
    py_gt_iou = []
    trt_gt_iou = []
    traj_center_px = []
    traj_iou = []
    py_update_ms = []
    trt_update_ms = []
    collapse_count = 0
    raw_bad_count = 0
    traj_bad_count = 0

    for idx in range(1, n):
        frame = load_frame(image_paths[idx])
        prev_state = list(gt_xywh[idx - 1])
        gt_box = xywh_to_xyxy(gt_xywh[idx])

        x_patch_arr, resize_factor = raw_ref.sample_target(
            frame, prev_state, raw_ref.search_factor, output_sz=raw_ref.search_size
        )
        search = raw_ref.preprocessor.process(x_patch_arr)

        t0 = time.perf_counter()
        pred_py = raw_pytorch_forward(raw_ref, search, raw_ref.template)
        py_raw_ms = (time.perf_counter() - t0) * 1000.0
        t0 = time.perf_counter()
        pred_trt = raw_trt._trt_infer(search, raw_trt.template)
        trt_raw_ms = (time.perf_counter() - t0) * 1000.0

        diff = np.abs(pred_py.astype(np.float32) - pred_trt.astype(np.float32))
        raw_abs_mean.append(float(diff.mean()))
        raw_abs_max.append(float(diff.max()))

        pred_py_box = map_box_back(
            (pred_py.reshape(-1, 4).mean(axis=0) * raw_ref.search_size / resize_factor).tolist(),
            prev_state,
            raw_ref.search_size,
            resize_factor,
        )
        pred_trt_box = map_box_back(
            (pred_trt.reshape(-1, 4).mean(axis=0) * raw_trt.search_size / resize_factor).tolist(),
            prev_state,
            raw_trt.search_size,
            resize_factor,
        )
        raw_center = center_error(bbox_center(pred_py_box), bbox_center(pred_trt_box))
        raw_center_px.append(raw_center)
        raw_iou_value = bbox_iou(pred_py_box, pred_trt_box)
        raw_iou.append(raw_iou_value)
        if raw_center > args.raw_center_tol or raw_iou_value < args.raw_iou_tol:
            raw_bad_count += 1

        t0 = time.perf_counter()
        py_box, _, py_ok = py_track.update(frame)
        py_update_ms.append((time.perf_counter() - t0) * 1000.0)
        t0 = time.perf_counter()
        trt_box, _, trt_ok = trt_track.update(frame)
        trt_update_ms.append((time.perf_counter() - t0) * 1000.0)

        if py_ok and py_box is not None:
            py_gt_iou.append(bbox_iou(py_box, gt_box))
        if trt_ok and trt_box is not None:
            trt_gt_iou.append(bbox_iou(trt_box, gt_box))
            tw = max(0.0, trt_box[2] - trt_box[0])
            th = max(0.0, trt_box[3] - trt_box[1])
            if tw <= args.collapse_size or th <= args.collapse_size:
                collapse_count += 1
        if py_ok and trt_ok and py_box is not None and trt_box is not None:
            traj_center = center_error(bbox_center(py_box), bbox_center(trt_box))
            traj_iou_value = bbox_iou(py_box, trt_box)
            traj_center_px.append(traj_center)
            traj_iou.append(traj_iou_value)
            if traj_center > args.traj_center_tol or traj_iou_value < args.traj_iou_tol:
                traj_bad_count += 1

        if args.write_rows:
            rows.append(
                {
                    "sequence": seq_dir.name,
                    "frame": idx + 1,
                    "raw_abs_mean": raw_abs_mean[-1],
                    "raw_abs_max": raw_abs_max[-1],
                    "raw_center_px": raw_center,
                    "raw_iou": raw_iou_value,
                    "py_raw_ms": py_raw_ms,
                    "trt_raw_ms": trt_raw_ms,
                    "py_ok": int(py_ok),
                    "trt_ok": int(trt_ok),
                    "traj_center_px": traj_center_px[-1] if traj_center_px else None,
                    "traj_iou": traj_iou[-1] if traj_iou else None,
                    "py_gt_iou": py_gt_iou[-1] if py_gt_iou else None,
                    "trt_gt_iou": trt_gt_iou[-1] if trt_gt_iou else None,
                }
            )

        if idx % max(1, args.print_every) == 0:
            print(
                f"{seq_dir.name} frame={idx + 1}/{n} "
                f"raw_center={raw_center:.2f}px raw_iou={raw_iou_value:.3f} "
                f"collapse={collapse_count}",
                flush=True,
            )

    summary = {
        "sequence": seq_dir.name,
        "frames": n,
        "eval_frames": n - 1,
        "raw_bad_count": raw_bad_count,
        "traj_bad_count": traj_bad_count,
        "trt_collapse_count": collapse_count,
        "raw_abs_mean": summarize(raw_abs_mean)["mean"],
        "raw_abs_max": summarize(raw_abs_max)["max"],
        "raw_center_mean_px": summarize(raw_center_px)["mean"],
        "raw_center_p95_px": summarize(raw_center_px)["p95"],
        "raw_iou_mean": summarize(raw_iou)["mean"],
        "raw_iou_p95_bad": float(np.percentile(1.0 - np.asarray(raw_iou), 95)) if raw_iou else None,
        "traj_center_mean_px": summarize(traj_center_px)["mean"],
        "traj_center_p95_px": summarize(traj_center_px)["p95"],
        "traj_iou_mean": summarize(traj_iou)["mean"],
        "py_gt_iou_mean": summarize(py_gt_iou)["mean"],
        "trt_gt_iou_mean": summarize(trt_gt_iou)["mean"],
        "py_update_mean_ms": summarize(py_update_ms)["mean"],
        "trt_update_mean_ms": summarize(trt_update_ms)["mean"],
        "raw_center_tol": args.raw_center_tol,
        "raw_iou_tol": args.raw_iou_tol,
        "traj_center_tol": args.traj_center_tol,
        "traj_iou_tol": args.traj_iou_tol,
    }
    return summary, rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", default="/home/mll/Downloads/tracking_test")
    parser.add_argument("--sequence", action="append", default=[])
    parser.add_argument("--checkpoint", default="/home/mll/Downloads/AsymTrack_ep0500.pth.tar")
    parser.add_argument("--engine", default="models/asymtrack/asymtrack_tiny_fp32.engine")
    parser.add_argument("--repo-root", default="third_party/AsymTrack")
    parser.add_argument("--yaml-name", default="tiny")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--output-dir", default="experiments/asymtrack_trt_compare")
    parser.add_argument("--max-frames", type=int, default=150)
    parser.add_argument("--print-every", type=int, default=30)
    parser.add_argument("--write-rows", action="store_true")
    parser.add_argument("--raw-center-tol", type=float, default=3.0)
    parser.add_argument("--raw-iou-tol", type=float, default=0.90)
    parser.add_argument("--traj-center-tol", type=float, default=15.0)
    parser.add_argument("--traj-iou-tol", type=float, default=0.60)
    parser.add_argument("--collapse-size", type=float, default=12.0)
    args = parser.parse_args()

    root = Path(args.data_root)
    seqs = [root / name for name in args.sequence] if args.sequence else discover_sequences(root)
    if not seqs:
        raise RuntimeError(f"no annotated image sequences found under {root}")

    out_dir = Path(args.output_dir) / time.strftime("%Y%m%d_%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)
    all_summaries = []
    all_rows = []
    for seq in seqs:
        print(f"running {seq}", flush=True)
        summary, rows = run_sequence(args, seq)
        all_summaries.append(summary)
        all_rows.extend(rows)
        print(json.dumps(summary, indent=2), flush=True)

    with (out_dir / "summary.json").open("w", encoding="utf-8") as f:
        json.dump(all_summaries, f, indent=2, ensure_ascii=False)
    with (out_dir / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_summaries[0].keys()))
        writer.writeheader()
        writer.writerows(all_summaries)
    if all_rows:
        with (out_dir / "rows.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
            writer.writeheader()
            writer.writerows(all_rows)
    print(f"outputs: {out_dir}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
