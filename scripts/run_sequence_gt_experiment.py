from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from collections import deque
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.asymtrack_tracker import AsymTrackTracker
from modules.common import bbox_center, bbox_iou, xywh_to_xyxy
from modules.target_predictor import KalmanTargetPredictor


def center_error(a, b) -> float:
    ax, ay = a
    bx, by = b
    return float(math.hypot(ax - bx, ay - by))


def load_groundtruth(path: Path):
    boxes = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            boxes.append(None)
            continue
        parts = [float(x) for x in line.replace("\t", ",").replace(" ", ",").split(",") if x]
        if len(parts) < 4:
            raise ValueError(f"bad groundtruth line in {path}: {line}")
        x, y, w, h = parts[:4]
        if any(math.isnan(v) for v in (x, y, w, h)) or w <= 0 or h <= 0:
            boxes.append(None)
            continue
        boxes.append(tuple(map(float, xywh_to_xyxy((x, y, w, h)))))
    return boxes


def summarize(rows, prefix=""):
    if not rows:
        return {}
    baseline = np.array([r["baseline_err_px"] for r in rows], dtype=float)
    pred = np.array([r["pred_err_px"] for r in rows], dtype=float)
    gt_delay = np.array([r["gt_delay_err_px"] for r in rows], dtype=float)
    return {
        f"{prefix}baseline_mean_px": float(baseline.mean()),
        f"{prefix}pred_mean_px": float(pred.mean()),
        f"{prefix}gt_delay_mean_px": float(gt_delay.mean()),
        f"{prefix}baseline_p95_px": float(np.percentile(baseline, 95)),
        f"{prefix}pred_p95_px": float(np.percentile(pred, 95)),
        f"{prefix}mean_improvement_px": float((baseline - pred).mean()),
        f"{prefix}improved_ratio": float(np.mean(pred < baseline)),
    }


def split_segments(rows, max_gap):
    segments = []
    current = []
    last_frame = None
    for row in rows:
        frame_idx = row["frame_idx"]
        if last_frame is None or frame_idx - last_frame <= max_gap:
            current.append(row)
        else:
            segments.append(current)
            current = [row]
        last_frame = frame_idx
    if current:
        segments.append(current)
    return segments


def draw(frame, gt_bbox, delayed_gt_bbox, track_bbox, pred_center, row):
    x1, y1, x2, y2 = map(int, gt_bbox)
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 220, 255), 2)
    cv2.putText(frame, "gt", (x1, max(18, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 220, 255), 2)

    x1, y1, x2, y2 = map(int, delayed_gt_bbox)
    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 150, 40), 1)

    if track_bbox is not None:
        x1, y1, x2, y2 = map(int, track_bbox)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (60, 240, 80), 2)
        cv2.circle(frame, tuple(map(int, bbox_center(track_bbox))), 5, (60, 240, 80), -1)
    if pred_center is not None:
        cv2.circle(frame, tuple(map(int, pred_center)), 7, (40, 80, 255), 2)

    h, w = frame.shape[:2]
    cv2.drawMarker(frame, (w // 2, h // 2), (230, 230, 230), cv2.MARKER_CROSS, 28, 1)
    lines = [
        f"f={row['frame_idx']} delay={row['delay_ms']}ms pred={row['predict_ms']}ms",
        f"base={row.get('baseline_err_px'):.2f} pred={row.get('pred_err_px'):.2f} gt_delay={row.get('gt_delay_err_px'):.2f}",
        f"gt_corr={row['gt_corrected']} template={row['template_refreshed']} lost={row['lost']}",
    ]
    for i, text in enumerate(lines):
        cv2.putText(frame, text, (10, 24 + i * 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return frame


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sequence-dir", required=True)
    parser.add_argument("--asymtrack", default="/home/mll/Downloads/AsymTrack_ep0500.pth.tar")
    parser.add_argument("--repo-root", default="third_party/AsymTrack")
    parser.add_argument("--output-dir", default="experiments/sequence_gt_delay")
    parser.add_argument("--fps", type=float, default=30.0)
    parser.add_argument("--delay-ms", type=float, default=200.0)
    parser.add_argument("--predict-ms", type=float, default=200.0)
    parser.add_argument("--predictor", choices=["kf", "dkf"], default="dkf")
    parser.add_argument("--process-noise", type=float, default=50.0)
    parser.add_argument("--measurement-noise", type=float, default=25.0)
    parser.add_argument("--max-frames", type=int, default=0)
    parser.add_argument("--eval-stride", type=int, default=5)
    parser.add_argument("--gt-correct-interval", type=int, default=3)
    parser.add_argument("--template-update-interval", type=int, default=12)
    parser.add_argument("--min-segment-rows", type=int, default=10)
    parser.add_argument("--write-video", action="store_true")
    args = parser.parse_args()

    sequence_dir = Path(args.sequence_dir)
    image_dir = sequence_dir / "images"
    gt_path = sequence_dir / "annotations" / "groundtruth.txt"
    images = sorted(image_dir.glob("*.jpg"))
    gt_boxes = load_groundtruth(gt_path)
    total = min(len(images), len(gt_boxes))
    if args.max_frames:
        total = min(total, args.max_frames)
    if total <= 0:
        raise RuntimeError(f"no frames found in {sequence_dir}")

    out_dir = Path(args.output_dir) / f"{sequence_dir.name}_{time.strftime('%Y%m%d_%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    first = cv2.imread(str(images[0]))
    if first is None:
        raise RuntimeError(f"failed to read first image: {images[0]}")
    h, w = first.shape[:2]
    delay_frames = max(1, int(round(args.delay_ms * args.fps / 1000.0)))
    tracker = AsymTrackTracker(model=args.asymtrack, repo_root=args.repo_root, yaml_name="tiny")
    kf = KalmanTargetPredictor(
        process_noise=args.process_noise,
        measurement_noise=args.measurement_noise,
        history_sec=2.0,
        gate_px=240.0,
        gate_mahalanobis=16.0,
        reliable_sigma_px=30.0,
        max_sigma_px=80.0,
    )

    video_writer = None
    if args.write_video:
        video_writer = cv2.VideoWriter(str(out_dir / "overlay.mp4"), cv2.VideoWriter_fourcc(*"mp4v"), args.fps / args.eval_stride, (w, h))

    frame_buffer = deque(maxlen=delay_frames + 1)
    rows = []
    initialized = False
    lost_count = 0
    invalid_gt_count = 0
    gt_corrections = 0
    template_refreshes = 0
    last_template_frame = -10**9

    with open(out_dir / "steps.jsonl", "w", encoding="utf-8") as jsonl:
        for frame_idx in range(total):
            frame = cv2.imread(str(images[frame_idx]))
            if frame is None:
                continue
            frame_buffer.append((frame_idx, frame))
            if len(frame_buffer) <= delay_frames:
                continue
            if frame_idx % args.eval_stride != 0:
                continue

            delayed_idx, delayed_frame = frame_buffer[0]
            gt_bbox = gt_boxes[frame_idx]
            delayed_gt_bbox = gt_boxes[delayed_idx]
            if gt_bbox is None or delayed_gt_bbox is None:
                invalid_gt_count += 1
                initialized = False
                kf.reset()
                continue
            current_ts = frame_idx / args.fps
            delayed_ts = delayed_idx / args.fps
            row = {
                "sequence": sequence_dir.name,
                "frame_idx": frame_idx,
                "delayed_idx": delayed_idx,
                "fps": args.fps,
                "delay_ms": args.delay_ms,
                "predict_ms": args.predict_ms,
                "predictor": args.predictor,
                "gt_corrected": 0,
                "template_refreshed": 0,
                "lost": 0,
                "gt_bbox": list(gt_bbox),
                "delayed_gt_bbox": list(delayed_gt_bbox),
            }

            if not initialized:
                if tracker.init(delayed_frame, delayed_gt_bbox):
                    initialized = True
                    kf.reset()
                    last_template_frame = frame_idx
                else:
                    lost_count += 1
                    row["lost"] = 1
                    rows.append(row)
                    jsonl.write(json.dumps(row) + "\n")
                    continue

            track_bbox, _, track_ok = tracker.update(delayed_frame)
            if not track_ok or track_bbox is None:
                initialized = False
                kf.reset()
                lost_count += 1
                row["lost"] = 1
                rows.append(row)
                jsonl.write(json.dumps(row) + "\n")
                continue

            if args.gt_correct_interval > 0 and frame_idx % args.gt_correct_interval == 0:
                gt_corrections += 1
                row["gt_corrected"] = 1
                if frame_idx - last_template_frame >= max(1, args.template_update_interval) or bbox_iou(track_bbox, delayed_gt_bbox) < 0.15:
                    tracker.init(delayed_frame, delayed_gt_bbox)
                    last_template_frame = frame_idx
                    template_refreshes += 1
                    row["template_refreshed"] = 1
                track_bbox = delayed_gt_bbox

            if args.predictor == "dkf":
                kf.update(track_bbox, delayed_ts, current_time=current_ts, timestamp_is_image_time=True)
                future_dt = max(0.0, args.predict_ms / 1000.0)
            else:
                kf.update(track_bbox, delayed_ts, timestamp_is_image_time=True)
                future_dt = max(0.0, current_ts - delayed_ts + args.predict_ms / 1000.0 - args.delay_ms / 1000.0)
            pred_center = kf.predict_future(future_dt)
            delayed_center = bbox_center(track_bbox)
            gt_center = bbox_center(gt_bbox)
            delayed_gt_center = bbox_center(delayed_gt_bbox)

            row.update(
                {
                    "track_bbox": list(track_bbox),
                    "delayed_center": list(delayed_center),
                    "pred_center": list(pred_center) if pred_center is not None else None,
                    "gt_center": list(gt_center),
                    "velocity": list(kf.get_velocity()),
                    "dkf_sigma": list(kf.get_sigma()),
                    "dkf_confidence": kf.confidence_scale(),
                    "baseline_err_px": center_error(delayed_center, gt_center),
                    "gt_delay_err_px": center_error(delayed_gt_center, gt_center),
                    "pred_err_px": center_error(pred_center, gt_center) if pred_center is not None else None,
                }
            )
            row["improvement_px"] = row["baseline_err_px"] - row["pred_err_px"] if row["pred_err_px"] is not None else None
            rows.append(row)
            jsonl.write(json.dumps(row) + "\n")

            if video_writer is not None:
                video_writer.write(draw(frame.copy(), gt_bbox, delayed_gt_bbox, track_bbox, pred_center, row))
            if frame_idx % max(1, int(args.fps * 10)) == 0:
                print(f"{sequence_dir.name} frame {frame_idx}/{total} rows={len(rows)} gt_corr={gt_corrections} lost={lost_count}", flush=True)

    if video_writer is not None:
        video_writer.release()

    valid = [r for r in rows if r.get("pred_err_px") is not None]
    segments = split_segments(valid, max_gap=max(1, args.eval_stride))
    segment_rows = []
    for idx, segment in enumerate(segments):
        segment_rows.append(
            {
                "segment_idx": idx,
                "start_frame": segment[0]["frame_idx"],
                "end_frame": segment[-1]["frame_idx"],
                "rows": len(segment),
                **summarize(segment),
            }
        )
    stable = [s for s in segments if len(s) >= max(1, args.min_segment_rows)]
    stable_rows = [r for s in stable for r in s]
    summary = {
        "sequence": str(sequence_dir),
        "fps": args.fps,
        "frames": total,
        "delay_ms": args.delay_ms,
        "predict_ms": args.predict_ms,
        "predictor": args.predictor,
        "process_noise": args.process_noise,
        "measurement_noise": args.measurement_noise,
        "delay_frames": delay_frames,
        "rows": len(rows),
        "valid_eval_rows": len(valid),
        "valid_ratio": float(len(valid) / len(rows)) if rows else 0.0,
        "lost_count": lost_count,
        "invalid_gt_count": invalid_gt_count,
        "valid_gt_frames": sum(1 for b in gt_boxes[:total] if b is not None),
        "gt_corrections": gt_corrections,
        "template_refreshes": template_refreshes,
        "valid_segments": len(segments),
        "stable_segments": len(stable),
        "gt_correct_interval": args.gt_correct_interval,
        "template_update_interval": args.template_update_interval,
    }
    summary.update(summarize(valid))
    if stable_rows:
        summary.update(summarize(stable_rows, prefix="stable_"))
    if segment_rows:
        best = max(segment_rows, key=lambda x: x["mean_improvement_px"])
        longest = max(segment_rows, key=lambda x: x["rows"])
        summary.update(
            {
                "best_segment_start": best["start_frame"],
                "best_segment_end": best["end_frame"],
                "best_segment_rows": best["rows"],
                "best_segment_improvement_px": best["mean_improvement_px"],
                "longest_segment_start": longest["start_frame"],
                "longest_segment_end": longest["end_frame"],
                "longest_segment_rows": longest["rows"],
                "longest_segment_improvement_px": longest["mean_improvement_px"],
            }
        )

    with open(out_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    with open(out_dir / "summary.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary.keys()))
        writer.writeheader()
        writer.writerow(summary)
    with open(out_dir / "segments.json", "w", encoding="utf-8") as f:
        json.dump(segment_rows, f, indent=2, ensure_ascii=False)
    if segment_rows:
        with open(out_dir / "segments.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(segment_rows[0].keys()))
            writer.writeheader()
            writer.writerows(segment_rows)

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"outputs: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
