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
from modules.common import bbox_center, bbox_iou
from modules.isr_onnx_detector import ISRONNXDetector
from modules.target_predictor import KalmanTargetPredictor
from modules.target_selector import auto_select, match_detection_to_track


def center_error(a, b) -> float:
    ax, ay = a
    bx, by = b
    return float(math.hypot(ax - bx, ay - by))


def summarize_error_rows(rows):
    if not rows:
        return {}
    base = np.array([r["baseline_err_px"] for r in rows], dtype=float)
    pred = np.array([r["pred_err_px"] for r in rows], dtype=float)
    return {
        "baseline_mean_px": float(base.mean()),
        "pred_mean_px": float(pred.mean()),
        "baseline_p95_px": float(np.percentile(base, 95)),
        "pred_p95_px": float(np.percentile(pred, 95)),
        "mean_improvement_px": float((base - pred).mean()),
        "improved_ratio": float(np.mean(pred < base)),
    }


def split_valid_segments(valid_rows, max_frame_gap):
    segments = []
    current = []
    last_frame = None
    for row in valid_rows:
        frame_idx = row["frame_idx"]
        if last_frame is None or frame_idx - last_frame <= max_frame_gap:
            current.append(row)
        else:
            segments.append(current)
            current = [row]
        last_frame = frame_idx
    if current:
        segments.append(current)
    return segments


def choose_reference(detections, prev_bbox, frame_shape, allow_reselect=False):
    if not detections:
        return None
    if prev_bbox is None:
        return auto_select(detections, frame_shape)
    matched = match_detection_to_track(detections, prev_bbox, frame_shape, min_iou=0.01, max_center_dist=0.45)
    if matched is not None:
        return matched
    if allow_reselect:
        return auto_select(detections, frame_shape)
    return None


def draw(frame, ref, track_bbox, pred_center, delayed_center, row):
    h, w = frame.shape[:2]
    cv2.drawMarker(frame, (w // 2, h // 2), (230, 230, 230), cv2.MARKER_CROSS, 28, 1)
    if ref is not None:
        x1, y1, x2, y2 = map(int, ref.bbox_xyxy)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 220, 255), 2)
        cv2.putText(frame, f"ref {ref.conf:.2f}", (x1, max(18, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 220, 255), 2)
    if track_bbox is not None:
        x1, y1, x2, y2 = map(int, track_bbox)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (60, 240, 80), 2)
    if delayed_center is not None:
        cv2.circle(frame, tuple(map(int, delayed_center)), 5, (255, 120, 40), -1)
    if pred_center is not None:
        cv2.circle(frame, tuple(map(int, pred_center)), 7, (40, 80, 255), 2)
    lines = [
        f"f={row['frame_idx']} delay={row['delay_ms']}ms pred={row['predict_ms']}ms",
        f"base_err={row.get('baseline_err_px')} pred_err={row.get('pred_err_px')}",
        f"ref={row.get('ref_valid', 0)} det_corr={row['detector_corrected']} template={row['template_refreshed']} lost={row['lost']}",
    ]
    for i, text in enumerate(lines):
        cv2.putText(frame, text, (10, 24 + i * 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return frame


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", default="/home/mll/Desktop/VIDEOS/videos/output_new.mp4")
    parser.add_argument("--detector", default="/home/mll/CPP_PROJ/code_release/version_v7_weights/isr_v2_8l_20250304_ver7_960.onnx")
    parser.add_argument("--asymtrack", default="/home/mll/Downloads/AsymTrack_ep0500.pth.tar")
    parser.add_argument("--repo-root", default="third_party/AsymTrack")
    parser.add_argument("--output-dir", default="experiments/offline_delay")
    parser.add_argument("--delay-ms", type=float, default=200.0)
    parser.add_argument("--predict-ms", type=float, default=200.0)
    parser.add_argument("--conf", type=float, default=0.20)
    parser.add_argument("--classes", default="", help="Comma-separated class ids; empty means all.")
    parser.add_argument("--max-frames", type=int, default=0)
    parser.add_argument("--eval-stride", type=int, default=3)
    parser.add_argument("--detector-correct-interval", type=int, default=3)
    parser.add_argument("--template-update-interval", type=int, default=12)
    parser.add_argument("--allow-reference-reselect", action="store_true", help="Allow reference detector to pick a new target after association fails.")
    parser.add_argument("--max-ref-center-jump", type=float, default=220.0, help="Reject reference jumps larger than this many pixels; <=0 disables.")
    parser.add_argument("--min-segment-rows", type=int, default=10, help="Minimum consecutive valid rows for stable-segment metrics.")
    parser.add_argument("--write-video", action="store_true")
    args = parser.parse_args()

    out_dir = Path(args.output_dir) / time.strftime("%Y%m%d_%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)
    classes = [int(x) for x in args.classes.split(",") if x.strip()] or None
    detector = ISRONNXDetector(args.detector, conf=args.conf, classes=classes)
    tracker = AsymTrackTracker(model=args.asymtrack, repo_root=args.repo_root, yaml_name="tiny")
    kf = KalmanTargetPredictor(process_noise=50.0, measurement_noise=25.0)

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        raise RuntimeError(f"failed to open video: {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    delay_frames = max(1, int(round(args.delay_ms * fps / 1000.0)))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video_writer = None
    if args.write_video:
        video_writer = cv2.VideoWriter(str(out_dir / "overlay.mp4"), cv2.VideoWriter_fourcc(*"mp4v"), fps / args.eval_stride, (w, h))

    rows = []
    frame_buffer = deque(maxlen=delay_frames + 1)
    prev_ref_bbox = None
    last_template_frame = -10**9
    initialized = False
    lost_count = 0
    detector_corrections = 0
    template_refreshes = 0
    ref_misses = 0
    ref_switch_rejects = 0

    jsonl = open(out_dir / "steps.jsonl", "w", encoding="utf-8")
    frame_idx = -1
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame_idx += 1
        if args.max_frames and frame_idx >= args.max_frames:
            break
        frame_buffer.append((frame_idx, frame.copy()))
        if len(frame_buffer) <= delay_frames:
            continue
        if frame_idx % args.eval_stride != 0:
            continue

        delayed_idx, delayed_frame = frame_buffer[0]
        current_ts = frame_idx / fps
        delayed_ts = delayed_idx / fps
        row = {
            "frame_idx": frame_idx,
            "delayed_idx": delayed_idx,
            "fps": fps,
            "delay_ms": args.delay_ms,
            "predict_ms": args.predict_ms,
            "detector_corrected": 0,
            "template_refreshed": 0,
            "lost": 0,
            "ref_valid": 0,
            "ref_miss": 0,
            "ref_switch_rejected": 0,
        }

        ref_dets = detector.detect(frame)
        ref = choose_reference(ref_dets, prev_ref_bbox, frame.shape, args.allow_reference_reselect)
        if ref is not None:
            if prev_ref_bbox is not None and args.max_ref_center_jump > 0:
                jump_px = center_error(bbox_center(prev_ref_bbox), ref.center)
                row["ref_center_jump_px"] = jump_px
                if jump_px > args.max_ref_center_jump and not args.allow_reference_reselect:
                    ref = None
                    ref_switch_rejects += 1
                    row["ref_switch_rejected"] = 1
            if ref is not None:
                prev_ref_bbox = ref.bbox_xyxy
                row["ref_valid"] = 1
                row["ref_bbox"] = list(ref.bbox_xyxy)
                row["ref_conf"] = ref.conf
        if ref is None:
            ref_misses += 1
            row["ref_miss"] = 1

        if not initialized:
            init_dets = detector.detect(delayed_frame)
            init_det = choose_reference(init_dets, None, delayed_frame.shape, True)
            if init_det is not None and tracker.init(delayed_frame, init_det.bbox_xyxy):
                initialized = True
                kf.reset()
                last_template_frame = frame_idx
            else:
                row["lost"] = 1
                jsonl.write(json.dumps(row) + "\n")
                rows.append(row)
                continue

        track_bbox, track_score, track_ok = tracker.update(delayed_frame)
        if not track_ok or track_bbox is None:
            initialized = False
            kf.reset()
            lost_count += 1
            row["lost"] = 1
            jsonl.write(json.dumps(row) + "\n")
            rows.append(row)
            continue

        if frame_idx % max(1, args.detector_correct_interval) == 0:
            dets = detector.detect(delayed_frame)
            det = match_detection_to_track(dets, track_bbox, delayed_frame.shape, min_iou=0.02, max_center_dist=0.45)
            if det is not None:
                detector_corrections += 1
                row["detector_corrected"] = 1
                if frame_idx - last_template_frame >= max(1, args.template_update_interval) or bbox_iou(track_bbox, det.bbox_xyxy) < 0.15:
                    tracker.init(delayed_frame, det.bbox_xyxy)
                    last_template_frame = frame_idx
                    template_refreshes += 1
                    row["template_refreshed"] = 1
                track_bbox = det.bbox_xyxy

        kf.update(track_bbox, delayed_ts)
        pred_center = kf.predict_future(max(0.0, current_ts - delayed_ts + args.predict_ms / 1000.0 - args.delay_ms / 1000.0))
        delayed_center = bbox_center(track_bbox)
        row["track_bbox"] = list(track_bbox)
        row["delayed_center"] = list(delayed_center)
        row["pred_center"] = list(pred_center) if pred_center is not None else None
        row["velocity"] = list(kf.get_velocity())

        if ref is not None:
            ref_center = ref.center
            row["ref_center"] = list(ref_center)
            row["baseline_err_px"] = center_error(delayed_center, ref_center)
            row["pred_err_px"] = center_error(pred_center, ref_center) if pred_center is not None else None
            row["improvement_px"] = row["baseline_err_px"] - row["pred_err_px"] if row["pred_err_px"] is not None else None

        jsonl.write(json.dumps(row) + "\n")
        rows.append(row)
        if video_writer is not None:
            video_writer.write(draw(frame.copy(), ref, track_bbox, pred_center, delayed_center, row))
        if frame_idx % max(1, int(fps * 5)) == 0:
            print(f"frame {frame_idx}/{frame_count} rows={len(rows)} corrections={detector_corrections} lost={lost_count}", flush=True)

    jsonl.close()
    cap.release()
    if video_writer is not None:
        video_writer.release()

    valid = [r for r in rows if r.get("pred_err_px") is not None]
    segments = split_valid_segments(valid, max_frame_gap=max(1, args.eval_stride))
    segment_rows = []
    for idx, segment in enumerate(segments):
        stats = summarize_error_rows(segment)
        segment_rows.append(
            {
                "segment_idx": idx,
                "start_frame": segment[0]["frame_idx"],
                "end_frame": segment[-1]["frame_idx"],
                "rows": len(segment),
                **stats,
            }
        )
    stable_segments = [s for s in segments if len(s) >= max(1, args.min_segment_rows)]
    stable_rows = [r for s in stable_segments for r in s]

    summary = {
        "video": args.video,
        "detector": args.detector,
        "delay_ms": args.delay_ms,
        "predict_ms": args.predict_ms,
        "fps": fps,
        "rows": len(rows),
        "valid_eval_rows": len(valid),
        "lost_count": lost_count,
        "detector_corrections": detector_corrections,
        "template_refreshes": template_refreshes,
        "ref_misses": ref_misses,
        "ref_switch_rejects": ref_switch_rejects,
        "allow_reference_reselect": args.allow_reference_reselect,
        "max_ref_center_jump": args.max_ref_center_jump,
        "valid_segments": len(segments),
        "stable_segments": len(stable_segments),
        "min_segment_rows": args.min_segment_rows,
        "valid_ratio": float(len(valid) / len(rows)) if rows else 0.0,
    }
    if valid:
        summary.update(summarize_error_rows(valid))
    if stable_rows:
        stable_stats = summarize_error_rows(stable_rows)
        summary.update({f"stable_{k}": v for k, v in stable_stats.items()})
    if segment_rows:
        longest = max(segment_rows, key=lambda x: x["rows"])
        best = max(segment_rows, key=lambda x: x["mean_improvement_px"])
        summary.update(
            {
                "longest_segment_start": longest["start_frame"],
                "longest_segment_end": longest["end_frame"],
                "longest_segment_rows": longest["rows"],
                "longest_segment_improvement_px": longest["mean_improvement_px"],
                "best_segment_start": best["start_frame"],
                "best_segment_end": best["end_frame"],
                "best_segment_rows": best["rows"],
                "best_segment_improvement_px": best["mean_improvement_px"],
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
