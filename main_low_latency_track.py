from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from types import SimpleNamespace

import cv2

from modules.asymtrack_tracker import AsymTrackTracker
from modules.common import TrackState, bbox_center, bbox_iou, clamp, load_config
from modules.dkf_filter import DKFFilter
from modules.gimbal_controller import A8MiniGimbal
from modules.global_motion import GlobalMotionEstimator
from modules.latest_frame_rtsp import LatestFrameRTSP
from modules.ostrack_tracker import OSTrackTracker
from modules.preview_publisher import PreviewPublisher
from modules.recorder import DataRecorder
from modules.speed_ramp import GimbalSpeedRamp
from modules.target_predictor import KalmanTargetPredictor
from modules.target_selector import ConfirmBuffer, auto_select, match_detection_to_track, select_by_click
from modules.visual_servo import VisualServo
from modules.yolo26_detector import YOLO26Detector


def make_click_bbox(frame_shape, x: int, y: int, box_size: int = 96):
    h, w = frame_shape[:2]
    half = max(8, box_size // 2)
    x1 = max(0, x - half)
    y1 = max(0, y - half)
    x2 = min(w - 1, x + half)
    y2 = min(h - 1, y + half)
    if x2 <= x1 or y2 <= y1:
        return None
    return (x1, y1, x2, y2)


def make_center_bbox(frame_shape, size_text: str):
    try:
        box_w, box_h = [int(v) for v in size_text.lower().split("x", 1)]
    except Exception:
        box_w, box_h = 220, 140
    h, w = frame_shape[:2]
    cx, cy = w // 2, h // 2
    x1 = max(0, cx - box_w // 2)
    y1 = max(0, cy - box_h // 2)
    x2 = min(w - 1, cx + box_w // 2)
    y2 = min(h - 1, cy + box_h // 2)
    return (x1, y1, x2, y2)


def normalize_bbox_xyxy(bbox_xyxy, frame_shape):
    if bbox_xyxy is None:
        return None
    h, w = frame_shape[:2]
    x1, y1, x2, y2 = bbox_xyxy
    return [
        clamp(float(x1) / max(1.0, float(w)), 0.0, 1.0),
        clamp(float(y1) / max(1.0, float(h)), 0.0, 1.0),
        clamp(float(x2) / max(1.0, float(w)), 0.0, 1.0),
        clamp(float(y2) / max(1.0, float(h)), 0.0, 1.0),
    ]


def normalize_center_error(center, frame_shape):
    if center is None:
        return [0.0, 0.0]
    h, w = frame_shape[:2]
    cx, cy = center
    return [
        (float(cx) - float(w) * 0.5) / max(1.0, float(w) * 0.5),
        (float(cy) - float(h) * 0.5) / max(1.0, float(h) * 0.5),
    ]


def _class_thresholds(det, cfg: dict) -> dict:
    control = cfg["control"]
    cls_id = getattr(det, "cls_id", None) if det is not None else None
    cls_name = str(getattr(det, "cls_name", "")).lower() if det is not None else ""
    human_ids = set(control.get("human_class_ids", [0, 1]) or [])
    human_names = {str(v).lower() for v in control.get("human_class_names", ["pedestrian", "people", "person"]) or []}
    is_human = cls_id in human_ids or cls_name in human_names
    if is_human:
        return {
            "min_conf": float(control.get("human_min_conf", 0.06)),
            "min_area_ratio": float(control.get("human_min_target_area_ratio", 0.00008)),
            "min_box_height": float(control.get("human_min_target_box_height", 8)),
            "min_box_width": float(control.get("human_min_target_box_width", 5)),
        }
    return {
        "min_conf": float(control.get("min_target_conf", 0.12)),
        "min_area_ratio": float(control.get("min_target_area_ratio", 0.0015)),
        "min_box_height": float(control.get("min_target_box_height", 32)),
        "min_box_width": float(control.get("min_target_box_width", 16)),
    }


def is_human_detection(det, cfg: dict) -> bool:
    if det is None:
        return False
    control = cfg["control"]
    cls_id = getattr(det, "cls_id", None)
    cls_name = str(getattr(det, "cls_name", "")).lower()
    human_ids = set(control.get("human_class_ids", [0, 1]) or [])
    human_names = {str(v).lower() for v in control.get("human_class_names", ["pedestrian", "people", "person"]) or []}
    return cls_id in human_ids or cls_name in human_names


def filter_same_target_class(detections, target_meta, cfg: dict):
    if target_meta is None:
        return detections
    if is_human_detection(target_meta, cfg):
        same = [d for d in detections if is_human_detection(d, cfg)]
        return same if same else detections
    target_cls_id = getattr(target_meta, "cls_id", None)
    if target_cls_id is not None:
        same = [d for d in detections if getattr(d, "cls_id", None) == target_cls_id]
        return same if same else detections
    target_cls_name = str(getattr(target_meta, "cls_name", "")).lower()
    if target_cls_name:
        same = [d for d in detections if str(getattr(d, "cls_name", "")).lower() == target_cls_name]
        return same if same else detections
    return detections


def is_trackable_bbox(bbox_xyxy, frame_shape, cfg: dict, det=None) -> bool:
    if bbox_xyxy is None:
        return False
    h, w = frame_shape[:2]
    x1, y1, x2, y2 = bbox_xyxy
    bw = max(0.0, float(x2 - x1))
    bh = max(0.0, float(y2 - y1))
    area_ratio = (bw * bh) / max(1.0, float(w * h))
    thr = _class_thresholds(det, cfg)
    if det is not None and float(getattr(det, "conf", 1.0)) < thr["min_conf"]:
        return False
    return area_ratio >= thr["min_area_ratio"] and bh >= thr["min_box_height"] and bw >= thr["min_box_width"]


def filter_trackable_detections(detections, frame_shape, cfg: dict):
    return [d for d in detections if is_trackable_bbox(d.bbox_xyxy, frame_shape, cfg, d)]


def detection_meta(det):
    if det is None:
        return None
    return SimpleNamespace(
        cls_id=getattr(det, "cls_id", None),
        cls_name=getattr(det, "cls_name", ""),
        conf=getattr(det, "conf", 1.0),
    )


def choose_auto_detection(detections, frame_shape, cfg: dict, predicted_bbox=None):
    if not detections:
        return None
    preferred = cfg.get("target_selector", {}).get("preferred_class_ids")
    if preferred:
        preferred = set(preferred)
        preferred_dets = [d for d in detections if getattr(d, "cls_id", None) in preferred]
        if preferred_dets:
            return auto_select(preferred_dets, frame_shape, predicted_bbox=predicted_bbox)
        if bool(cfg.get("target_selector", {}).get("require_preferred_class", False)):
            return None
    return auto_select(detections, frame_shape, predicted_bbox=predicted_bbox)


def parse_imgsz(value):
    if isinstance(value, (list, tuple)):
        return [int(v) for v in value]
    if isinstance(value, str) and "x" in value.lower():
        h, w = value.lower().split("x", 1)
        return [int(h), int(w)]
    return int(value)


def orient_frame(frame, rotate=0, flip=None):
    if rotate in (90, "90", "cw"):
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    elif rotate in (180, "180"):
        frame = cv2.rotate(frame, cv2.ROTATE_180)
    elif rotate in (270, "270", "ccw"):
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    if flip == "h":
        frame = cv2.flip(frame, 1)
    elif flip == "v":
        frame = cv2.flip(frame, 0)
    return frame


class MouseState:
    def __init__(self) -> None:
        self.click: tuple[int, int] | None = None

    def callback(self, event, x, y, flags, param) -> None:
        if event == cv2.EVENT_LBUTTONDOWN:
            self.click = (x, y)


class NullTracker:
    initialized = False

    def init(self, frame, bbox_xyxy) -> bool:
        return False

    def update(self, frame):
        return None, 0.0, False

    def reset(self) -> None:
        return None


def should_run_yolo(state: TrackState, frame_id: int, cfg: dict) -> bool:
    ycfg = cfg["yolo26"]
    if state in {TrackState.LOST, TrackState.REACQUIRE}:
        interval = int(ycfg.get("detect_interval_lost", 3))
    elif state in {TrackState.MANUAL_TRACK, TrackState.AUTO_TRACK}:
        interval = int(ycfg.get("detect_interval_track", 20))
    else:
        interval = int(ycfg.get("detect_interval_idle", 3))
    return frame_id % max(1, interval) == 0


def is_tracking_state(state: TrackState) -> bool:
    return state in {TrackState.MANUAL_TRACK, TrackState.AUTO_TRACK}


def is_auto_detection_state(state: TrackState, auto_track_enabled: bool) -> bool:
    return auto_track_enabled and state == TrackState.AUTO_TRACK


def draw_overlay(frame, state, detections, track_bbox, pred_center, hud: dict) -> None:
    h, w = frame.shape[:2]
    cv2.drawMarker(frame, (w // 2, h // 2), (230, 230, 230), cv2.MARKER_CROSS, 24, 1)
    for det in detections:
        x1, y1, x2, y2 = map(int, det.bbox_xyxy)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (50, 210, 255), 2)
        cv2.putText(frame, f"{det.cls_name} {det.conf:.2f}", (x1, max(18, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 210, 255), 1)
    if track_bbox is not None:
        x1, y1, x2, y2 = map(int, track_bbox)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (40, 240, 80), 2)
        cx, cy = bbox_center(track_bbox)
        cv2.circle(frame, (int(cx), int(cy)), 4, (40, 240, 80), -1)
    if pred_center is not None:
        px, py = map(int, pred_center)
        cv2.circle(frame, (px, py), 7, (40, 90, 255), 2)
        cv2.line(frame, (w // 2, h // 2), (px, py), (40, 90, 255), 1)
    lines = [f"state={state.value}"]
    lines.extend(f"{k}={v}" for k, v in hud.items())
    for i, text in enumerate(lines[:8]):
        cv2.putText(frame, text, (10, 24 + i * 22), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 255, 255), 2)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config_low_latency.yaml")
    parser.add_argument("--source", default=None, help="Override RTSP/video source. Use 0 for webcam.")
    parser.add_argument("--dry-run-gimbal", action="store_true")
    parser.add_argument("--real-gimbal", action="store_true", help="Really send UDP commands to the A8 mini gimbal.")
    parser.add_argument("--no-gui", action="store_true", help="Run without creating an OpenCV window.")
    parser.add_argument("--max-frames", type=int, default=0, help="Exit after N processed frames; useful for smoke tests.")
    parser.add_argument("--rtsp-transport", choices=["udp", "tcp"], default=None)
    parser.add_argument("--predict-ms", type=float, default=None)
    parser.add_argument("--kp-yaw", type=float, default=None)
    parser.add_argument("--kp-pitch", type=float, default=None)
    parser.add_argument("--rotate", default=None, help="Frame rotation: 0, 90, 180, 270.")
    parser.add_argument("--flip", choices=["h", "v"], default=None)
    parser.add_argument("--no-yolo", action="store_true", help="Disable detector loading; manual ROI tracking still works.")
    parser.add_argument("--auto-track", action="store_true", help="Auto-select the best detection and enter AUTO_TRACK.")
    parser.add_argument("--center-track", default=None, help="Initialize tracking from center ROI, e.g. 220x140.")
    parser.add_argument("--detect-track", action="store_true", help="Use detector boxes directly as the tracking measurement.")
    parser.add_argument("--detect-every", type=int, default=3, help="Detection interval for --detect-track.")
    parser.add_argument("--detect-miss-limit", type=int, default=5, help="Stop detect-track after N detector misses.")
    parser.add_argument("--preview-jpeg", default=None, help="Publish the annotated preview to this JPEG path.")
    parser.add_argument("--command-file", default=None, help="Dashboard command JSON path.")
    parser.add_argument("--operator-state-file", default=None, help="Latest human operator action JSON path.")
    args = parser.parse_args()
    cfg = load_config(args.config)

    source = args.source if args.source is not None else cfg["video"]["source"]
    if source == "0":
        source = 0
    capture = LatestFrameRTSP(
        source=source,
        rtsp_transport=args.rtsp_transport or cfg["video"].get("rtsp_transport", "udp"),
        buffer_size=int(cfg["video"].get("buffer_size", 1)),
        reconnect_sec=float(cfg["video"].get("reconnect_sec", 1.0)),
    )
    detector = YOLO26Detector(
        model_path=cfg["yolo26"]["model"],
        backend=cfg["yolo26"].get("backend", "ultralytics"),
        imgsz=parse_imgsz(cfg["yolo26"].get("imgsz", 640)),
        conf=float(cfg["yolo26"].get("conf", 0.35)),
        classes=cfg["yolo26"].get("classes"),
        enable=bool(cfg["yolo26"].get("enable", True)) and not args.no_yolo,
    )
    tracker_backend = str(cfg.get("tracking", {}).get("backend", "asymtrack")).lower()
    if args.detect_track:
        tracker = NullTracker()
    elif tracker_backend == "ostrack":
        ocfg = cfg.get("ostrack", {})
        tracker = OSTrackTracker(
            engine=ocfg.get("engine", "/home/mll/PycharmProjects/OSTrack/ostrack.engine"),
            device=ocfg.get("device", "cuda"),
            template_factor=float(ocfg.get("template_factor", 2.0)),
            search_factor=float(ocfg.get("search_factor", 4.0)),
            template_size=int(ocfg.get("template_size", 128)),
            search_size=int(ocfg.get("search_size", 256)),
            score_threshold=float(ocfg.get("score_threshold", 0.35)),
            template_update_score=float(ocfg.get("template_update_score", 0.70)),
            template_update_interval=int(ocfg.get("template_update_interval", 8)),
            max_lost_count=int(ocfg.get("max_lost_count", 8)),
            min_size_scale=float(ocfg.get("min_size_scale", 0.45)),
            max_size_scale=float(ocfg.get("max_size_scale", 2.20)),
            max_size_growth_per_frame=float(ocfg.get("max_size_growth_per_frame", 0.10)),
            max_size_shrink_per_frame=float(ocfg.get("max_size_shrink_per_frame", 0.18)),
            max_aspect_change=float(ocfg.get("max_aspect_change", 1.80)),
            size_smooth_alpha=float(ocfg.get("size_smooth_alpha", 0.70)),
        )
    else:
        tracker = AsymTrackTracker(
            backend=cfg["asymtrack"].get("backend", "pytorch"),
            model=cfg["asymtrack"].get("model"),
            engine=cfg["asymtrack"].get("engine"),
            repo_root=cfg["asymtrack"].get("repo_root", "third_party/AsymTrack"),
            yaml_name=cfg["asymtrack"].get("yaml_name", "tiny"),
            device=cfg["asymtrack"].get("device", "cuda"),
            max_lost_count=int(cfg["asymtrack"].get("max_lost_count", 10)),
        )
    predictor = KalmanTargetPredictor(
        process_noise=float(cfg["prediction"].get("process_noise", 50.0)),
        measurement_noise=float(cfg["prediction"].get("measurement_noise", 25.0)),
        history_sec=float(cfg["prediction"].get("history_sec", 2.0)),
        latency_est_ms=float(cfg["prediction"].get("latency_est_ms", 0.0)),
        init_pos_var=float(cfg["prediction"].get("init_pos_var", 100.0)),
        init_vel_var=float(cfg["prediction"].get("init_vel_var", 10000.0)),
        gate_px=float(cfg["prediction"].get("gate_px", 0.0)),
        gate_mahalanobis=float(cfg["prediction"].get("gate_mahalanobis", 0.0)),
        yaw_px_per_cmd=float(cfg["prediction"].get("yaw_px_per_cmd", 0.0)),
        pitch_px_per_cmd=float(cfg["prediction"].get("pitch_px_per_cmd", 0.0)),
        reliable_sigma_px=float(cfg["prediction"].get("reliable_sigma_px", 30.0)),
        max_sigma_px=float(cfg["prediction"].get("max_sigma_px", 80.0)),
    )
    dkf = DKFFilter(cfg.get("dkf", {}))
    gmotion_cfg = cfg.get("global_motion", {})
    global_motion = GlobalMotionEstimator(
        enable=bool(gmotion_cfg.get("enable", cfg.get("dkf", {}).get("camera_motion_compensation", False))),
        downscale=float(gmotion_cfg.get("downscale", 0.5)),
        max_corners=int(gmotion_cfg.get("max_corners", 500)),
        min_points=int(gmotion_cfg.get("min_points", 80)),
        refresh_interval=int(gmotion_cfg.get("refresh_interval", 8)),
        max_velocity_px_s=float(gmotion_cfg.get("max_velocity_px_s", 1500.0)),
        smoothing_alpha=float(gmotion_cfg.get("smoothing_alpha", 0.35)),
        max_delta_px_s=float(gmotion_cfg.get("max_delta_px_s", 500.0)),
        reset_decay=float(gmotion_cfg.get("reset_decay", 0.2)),
    )
    servo_cfg = dict(cfg["servo"])
    servo_cfg.pop("mode", None)
    if args.kp_yaw is not None:
        servo_cfg["kp_yaw"] = args.kp_yaw
    if args.kp_pitch is not None:
        servo_cfg["kp_pitch"] = args.kp_pitch
    servo = VisualServo(**servo_cfg)
    gcfg = cfg["gimbal"]
    gimbal = A8MiniGimbal(
        ip=gcfg.get("ip", "192.168.144.25"),
        port=int(gcfg.get("port", 37260)),
        yaw_sign=int(gcfg.get("yaw_sign", 1)),
        pitch_sign=int(gcfg.get("pitch_sign", 1)),
        dry_run=False if args.real_gimbal else bool(cfg["runtime"].get("dry_run_gimbal", True) or args.dry_run_gimbal),
        need_ack=bool(gcfg.get("need_ack", False)),
    )
    speed_ramp = GimbalSpeedRamp(
        gimbal,
        hz=float(cfg["control"].get("command_hz", 120)),
        max_yaw_delta_per_sec=float(cfg["control"].get("max_yaw_delta_per_sec", 300)),
        max_pitch_delta_per_sec=float(cfg["control"].get("max_pitch_delta_per_sec", 180)),
    )
    recorder = DataRecorder(
        root=cfg["record"].get("root", "recordings"),
        enable=bool(cfg["record"].get("enable", False)),
        save_video=bool(cfg["record"].get("save_video", True)),
        save_frames=bool(cfg["record"].get("save_frames", False)),
        save_jsonl=bool(cfg["record"].get("save_jsonl", True)),
        fps=float(cfg["record"].get("fps", cfg.get("preview", {}).get("fps", 25))),
        queue_size=int(cfg["record"].get("queue_size", 120)),
        dataset=str(cfg["record"].get("dataset", "smolvla_scan")),
        auto_start=bool(cfg["record"].get("auto_start", True)),
    )
    preview_cfg = cfg.get("preview", {})
    preview_path = args.preview_jpeg or preview_cfg.get("path", "/tmp/source_track_preview.jpg")
    preview = PreviewPublisher(
        path=preview_path,
        enable=bool(preview_cfg.get("enable", False) or args.preview_jpeg),
        fps=float(preview_cfg.get("fps", cfg["display"].get("fps_limit", 15))),
        quality=int(preview_cfg.get("quality", 80)),
    )

    mouse = MouseState()
    window = "A8 mini low-latency track"
    show_gui = bool(cfg["runtime"].get("show_gui", True)) and not args.no_gui
    if show_gui:
        cv2.namedWindow(window, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(window, mouse.callback)

    state = TrackState.IDLE
    auto_track_enabled = bool(args.auto_track)
    command_path = Path(args.command_file or cfg["control"].get("command_file", "/tmp/source_track_command.json"))
    operator_state_path = Path(args.operator_state_file or cfg["control"].get("operator_state_file", "/tmp/source_track_operator_action.json"))
    last_command_mtime_ns = 0
    last_operator_mtime_ns = 0
    operator_action = {
        "time": 0.0,
        "source": "none",
        "action": "none",
        "yaw": 0,
        "pitch": 0,
        "zoom": 1.0,
        "zoom_direction": 0,
        "track_mode": "manual",
        "recording": False,
    }
    detections = []
    frame_id = 0
    track_bbox = None
    pred_center = None
    last_cmd_ts = 0.0
    last_loop_ts = time.time()
    last_frame_ts_seen = 0.0
    last_status_ts = 0.0
    last_yaw_speed = 0
    last_pitch_speed = 0
    stale_count = 0
    duplicate_count = 0
    processed_count = 0
    last_printed_state = None
    display_interval = 1.0 / max(1.0, float(cfg["display"].get("fps_limit", 15)))
    last_display_ts = 0.0
    detect_miss_count = 0
    detector_miss_count = 0
    last_detector_ok_ts = 0.0
    last_kf_update_ts = 0.0
    last_template_update_frame = 0
    tracker_init_frame_id = -1
    lost_until_ts = 0.0
    reacquire_until_ts = 0.0
    reacquire_bbox = None
    active_target_meta = None
    confirm_cfg = cfg.get("confirm", {})
    auto_confirm = ConfirmBuffer(
        confirm_frames=int(confirm_cfg.get("confirm_frames", 2)),
        iou_thr=float(confirm_cfg.get("iou_thr", 0.15)),
        max_center_jump_ratio=float(confirm_cfg.get("max_center_jump_ratio", 0.12)),
        require_same_class=bool(confirm_cfg.get("require_same_class", True)),
    )

    def update_predictor_from_bbox(bbox, frame_shape, frame_timestamp: float, now_ts: float, score: float = 1.0) -> bool:
        x1, y1, x2, y2 = bbox
        h, w = frame_shape[:2]
        area_ratio = max(0.0, x2 - x1) * max(0.0, y2 - y1) / max(1.0, float(w * h))
        return predictor.update(
            bbox,
            frame_timestamp,
            current_time=now_ts,
            score=score,
            area_ratio=area_ratio,
            u=(last_yaw_speed, last_pitch_speed),
        )

    def init_target_filters(bbox) -> bool:
        predictor.reset()
        ok_dkf = dkf.init_from_bbox(bbox)
        return ok_dkf

    def reset_target_filters() -> None:
        predictor.reset()
        dkf.reset()

    def request_stop(immediate: bool = True) -> None:
        speed_ramp.stop(immediate=immediate)

    def confirm_auto_candidate(det, frame_shape):
        if det is None:
            auto_confirm.clear()
            return None
        auto_confirm.push(det)
        if not auto_confirm.is_stable(frame_shape):
            return None
        confirmed = auto_confirm.items[-1]
        auto_confirm.clear()
        return confirmed

    def enter_lost(now_ts: float) -> None:
        nonlocal state, track_bbox, pred_center, detector_miss_count, detect_miss_count, lost_until_ts, reacquire_until_ts, last_detector_ok_ts, last_kf_update_ts, last_template_update_frame, tracker_init_frame_id, last_yaw_speed, last_pitch_speed, reacquire_bbox, active_target_meta
        reacquire_bbox = dkf.get_bbox() or track_bbox or reacquire_bbox
        request_stop()
        last_yaw_speed = 0
        last_pitch_speed = 0
        tracker.reset()
        reset_target_filters()
        servo.reset()
        track_bbox = None
        pred_center = None
        detector_miss_count = 0
        detect_miss_count = 0
        last_detector_ok_ts = 0.0
        last_kf_update_ts = 0.0
        last_template_update_frame = 0
        tracker_init_frame_id = -1
        lost_until_ts = now_ts + float(cfg["control"].get("lost_hold_ms", 500)) / 1000.0
        reacquire_until_ts = lost_until_ts + float(cfg["control"].get("reacquire_search_ms", 1500)) / 1000.0
        auto_confirm.clear()
        state = TrackState.LOST

    def stop_tracking(new_state: TrackState = TrackState.STOPPED) -> None:
        nonlocal state, track_bbox, pred_center, detector_miss_count, detect_miss_count, reacquire_until_ts, last_detector_ok_ts, last_kf_update_ts, last_template_update_frame, tracker_init_frame_id, last_yaw_speed, last_pitch_speed, reacquire_bbox, active_target_meta
        request_stop()
        tracker.reset()
        reset_target_filters()
        servo.reset()
        track_bbox = None
        pred_center = None
        detector_miss_count = 0
        detect_miss_count = 0
        last_detector_ok_ts = 0.0
        last_kf_update_ts = 0.0
        last_template_update_frame = 0
        tracker_init_frame_id = -1
        last_yaw_speed = 0
        last_pitch_speed = 0
        reacquire_until_ts = 0.0
        reacquire_bbox = None
        active_target_meta = None
        auto_confirm.clear()
        state = new_state

    def limit_speed_command(target_yaw: float, target_pitch: float, dt: float) -> tuple[int, int]:
        control_cfg = cfg.get("control", {})
        dt = max(1e-3, float(dt))
        max_yaw = float(control_cfg.get("auto_max_yaw_speed", cfg["servo"].get("max_yaw_speed", 90)))
        max_pitch = float(control_cfg.get("auto_max_pitch_speed", cfg["servo"].get("max_pitch_speed", 45)))
        target_yaw = clamp(float(target_yaw), -max_yaw, max_yaw)
        target_pitch = clamp(float(target_pitch), -max_pitch, max_pitch)
        yaw_delta = max(0.0, float(control_cfg.get("max_yaw_delta_per_sec", 360.0))) * dt
        pitch_delta = max(0.0, float(control_cfg.get("max_pitch_delta_per_sec", 240.0))) * dt
        if yaw_delta > 0.0:
            target_yaw = clamp(target_yaw, last_yaw_speed - yaw_delta, last_yaw_speed + yaw_delta)
        if pitch_delta > 0.0:
            target_pitch = clamp(target_pitch, last_pitch_speed - pitch_delta, last_pitch_speed + pitch_delta)
        return int(round(target_yaw)), int(round(target_pitch))

    def handle_dashboard_command(command: dict, frame, frame_ts: float, now_ts: float) -> None:
        nonlocal state, track_bbox, pred_center, detect_miss_count, detector_miss_count, last_detector_ok_ts, last_kf_update_ts, last_template_update_frame, tracker_init_frame_id, reacquire_bbox, active_target_meta, auto_track_enabled
        action = str(command.get("action", "")).lower()
        if not action:
            return
        if action == "record_start":
            recorder.start(
                frame.shape if frame is not None else None,
                metadata={
                    "task": command.get("task", "human_scan"),
                    "source": str(source),
                    "operator_state_file": str(operator_state_path),
                    "command_file": str(command_path),
                    "policy_goal": "learn human gimbal scan/reacquire/coarse-follow behavior from image and tracking state",
                    "action_space": {
                        "yaw": "int [-100,100]",
                        "pitch": "int [-100,100]",
                        "zoom_direction": "int {-1,0,1}",
                        "action_vector": "[yaw/100, pitch/100, zoom_direction]",
                    },
                    "observation_space": {
                        "image": "BGR frame saved as video and/or JPEG",
                        "detections": "VisDrone detector boxes",
                        "tracker": "current target state",
                        "state_vector": "normalized target/control bbox, center error, target/camera velocity, current gimbal speed",
                    },
                    "recommended_use": "behavior cloning or SmolVLA/LeRobot finetuning; keep DKF/servo as low-level safety controller",
                },
            )
            print(f"dashboard action=record_start episode={recorder.episode_dir}", flush=True)
        elif action == "record_stop":
            episode_dir = recorder.episode_dir
            recorder.stop_episode()
            print(f"dashboard action=record_stop episode={episode_dir}", flush=True)
        elif action in {"manual", "manual_mode"}:
            auto_track_enabled = False
            stop_tracking(TrackState.STOPPED)
            print("dashboard action=manual_mode", flush=True)
        elif action in {"auto", "auto_track"}:
            if tracker.initialized or state in {TrackState.MANUAL_TRACK, TrackState.AUTO_TRACK, TrackState.LOST}:
                stop_tracking(TrackState.IDLE)
            auto_track_enabled = True
            print("dashboard action=auto_track", flush=True)
        elif action in {"stop_track", "release", "stop"}:
            auto_track_enabled = False
            stop_tracking(TrackState.STOPPED)
            print("dashboard action=stop_track", flush=True)
        elif action in {"center_track", "lock_center"}:
            auto_track_enabled = False
            box_text = str(command.get("box", cfg["control"].get("manual_center_box", "260x180")))
            center_bbox = make_center_bbox(frame.shape, box_text)
            if tracker.init(frame, center_bbox) and init_target_filters(center_bbox):
                servo.reset()
                track_bbox = center_bbox
                pred_center = bbox_center(center_bbox)
                detect_miss_count = 0
                detector_miss_count = 0
                last_detector_ok_ts = now_ts
                last_kf_update_ts = now_ts
                last_template_update_frame = frame_id
                tracker_init_frame_id = frame_id
                reacquire_bbox = None
                active_target_meta = None
                update_predictor_from_bbox(center_bbox, frame.shape, frame_ts, now_ts, 1.0)
                state = TrackState.MANUAL_TRACK
                print(f"dashboard action=center_track bbox={center_bbox}", flush=True)
            else:
                print("dashboard action=center_track failed=tracker_init", flush=True)
        elif action in {"reset"}:
            auto_track_enabled = False
            stop_tracking(TrackState.IDLE)
            print("dashboard action=reset", flush=True)
    predict_ms = float(args.predict_ms if args.predict_ms is not None else cfg["prediction"].get("predict_ms", 100))
    predict_ms = min(predict_ms, float(cfg["prediction"].get("max_predict_ms", 200)))

    capture.start()
    try:
        while True:
            ok, frame, frame_ts = capture.read_latest()
            if not ok:
                request_stop()
                time.sleep(0.01)
                continue

            rotate = args.rotate if args.rotate is not None else cfg["video"].get("rotate", 0)
            try:
                rotate = int(rotate)
            except Exception:
                pass
            frame = orient_frame(frame, rotate=rotate, flip=args.flip or cfg["video"].get("flip"))

            now = time.time()
            if frame_ts == last_frame_ts_seen:
                duplicate_count += 1
                time.sleep(0.01)
                continue
            last_frame_ts_seen = frame_ts
            frame_age_ms = (now - frame_ts) * 1000.0
            if frame_age_ms > float(cfg["latency"].get("max_frame_age_ms", 150)):
                stale_count += 1
                if cfg["control"].get("stop_on_stale_frame", True):
                    request_stop()
                time.sleep(0.001)
                continue

            frame_id += 1
            processed_count += 1
            step_dt = max(1e-3, min(float(cfg.get("dkf", {}).get("max_dt", 0.2)), now - last_loop_ts))
            camera_motion = global_motion.update(frame, now)
            if dkf.is_initialized():
                dkf.predict(step_dt, camera_motion=camera_motion)
            dkf_cfg = cfg.get("dkf", {})
            base_latency_sec = float(dkf_cfg.get("latency_ms", cfg["prediction"].get("latency_est_ms", 0.0))) / 1000.0
            pipeline_latency_sec = float(dkf_cfg.get("pipeline_latency_ms", 0.0)) / 1000.0
            measured_frame_sec = frame_age_ms / 1000.0 if bool(dkf_cfg.get("add_frame_age", True)) else 0.0
            measurement_delay_sec = base_latency_sec + pipeline_latency_sec + measured_frame_sec
            track_score = 0.0
            track_ok = False
            if state == TrackState.LOST and now < lost_until_ts:
                request_stop()
                track_bbox = None
                pred_center = None
                active_target_meta = None
                reset_target_filters()
            elif state == TrackState.LOST and now >= lost_until_ts:
                state = TrackState.REACQUIRE
            try:
                stat = command_path.stat()
                if stat.st_mtime_ns != last_command_mtime_ns:
                    last_command_mtime_ns = stat.st_mtime_ns
                    command = json.loads(command_path.read_text(encoding="utf-8"))
                    handle_dashboard_command(command, frame, frame_ts, now)
            except FileNotFoundError:
                pass
            except Exception as exc:
                print(f"dashboard command error={exc}", flush=True)
            try:
                stat = operator_state_path.stat()
                if stat.st_mtime_ns != last_operator_mtime_ns:
                    last_operator_mtime_ns = stat.st_mtime_ns
                    operator_action = json.loads(operator_state_path.read_text(encoding="utf-8"))
            except FileNotFoundError:
                pass
            except Exception as exc:
                print(f"operator action error={exc}", flush=True)
            if args.center_track and not tracker.initialized and not args.detect_track:
                center_bbox = make_center_bbox(frame.shape, args.center_track)
                if tracker.init(frame, center_bbox) and init_target_filters(center_bbox):
                    servo.reset()
                    last_detector_ok_ts = now
                    last_kf_update_ts = now
                    reacquire_bbox = None
                    track_bbox = center_bbox
                    tracker_init_frame_id = frame_id
                    active_target_meta = None
                    state = TrackState.AUTO_TRACK if auto_track_enabled else TrackState.MANUAL_TRACK
            if args.detect_track:
                run_detector = frame_id % max(1, args.detect_every) == 0
            elif is_tracking_state(state) and tracker.initialized:
                run_detector = False
            else:
                run_detector = should_run_yolo(state, frame_id, cfg)
            if not run_detector and is_tracking_state(state) and not args.detect_track:
                detections = []
            if run_detector:
                detections = filter_trackable_detections(detector.detect(frame), frame.shape, cfg)
                if args.detect_track and detections:
                    if track_bbox is not None and is_tracking_state(state):
                        det = match_detection_to_track(
                            detections,
                            track_bbox,
                            frame.shape,
                            min_iou=float(cfg["control"].get("detector_match_iou", 0.03)),
                            max_center_dist=float(cfg["control"].get("detector_max_center_dist", 0.35)),
                        )
                    elif auto_track_enabled:
                        det = choose_auto_detection(detections, frame.shape, cfg, predicted_bbox=dkf.get_bbox())
                    else:
                        det = None
                    if det:
                        detect_miss_count = 0
                        last_detector_ok_ts = now
                        track_bbox = det.bbox_xyxy
                        active_target_meta = detection_meta(det)
                        track_score = det.conf
                        track_ok = True
                        dkf.update_detector(
                            track_bbox,
                            track_score,
                            step_dt,
                            measurement_delay_sec=measurement_delay_sec,
                            camera_motion=camera_motion,
                        )
                        if not update_predictor_from_bbox(track_bbox, frame.shape, frame_ts, now, track_score):
                            enter_lost(now)
                            continue
                        last_kf_update_ts = now
                        pred_center = predictor.predict_future(predict_ms / 1000.0)
                        reacquire_bbox = None
                        state = TrackState.AUTO_TRACK if auto_track_enabled else TrackState.MANUAL_TRACK
                    elif is_tracking_state(state):
                        detect_miss_count += 1
                        if detect_miss_count >= max(1, args.detect_miss_limit):
                            enter_lost(now)
                elif args.detect_track:
                    detect_miss_count += 1
                    if detect_miss_count >= max(1, args.detect_miss_limit):
                        enter_lost(now)
                elif auto_track_enabled and state in {TrackState.IDLE, TrackState.STOPPED, TrackState.LOST, TrackState.REACQUIRE} and detections and not (state == TrackState.LOST and now < lost_until_ts):
                    reacquire_detections = filter_same_target_class(detections, active_target_meta, cfg)
                    if state == TrackState.REACQUIRE and reacquire_bbox is not None and now <= reacquire_until_ts:
                        candidate_det = match_detection_to_track(
                            reacquire_detections,
                            reacquire_bbox,
                            frame.shape,
                            min_iou=0.0,
                            max_center_dist=float(cfg["control"].get("reacquire_max_center_dist", 0.70)),
                        )
                    else:
                        if state == TrackState.REACQUIRE and reacquire_bbox is not None and now > reacquire_until_ts:
                            reacquire_bbox = None
                            active_target_meta = None
                            auto_confirm.clear()
                            state = TrackState.IDLE
                            reacquire_detections = detections
                        candidate_det = choose_auto_detection(reacquire_detections, frame.shape, cfg, predicted_bbox=dkf.get_bbox() or reacquire_bbox)
                    det = confirm_auto_candidate(candidate_det, frame.shape)
                    if det and is_trackable_bbox(det.bbox_xyxy, frame.shape, cfg, det) and tracker.init(frame, det.bbox_xyxy) and init_target_filters(det.bbox_xyxy):
                        servo.reset()
                        track_bbox = det.bbox_xyxy
                        active_target_meta = detection_meta(det)
                        last_detector_ok_ts = now
                        last_kf_update_ts = now
                        last_template_update_frame = frame_id
                        tracker_init_frame_id = frame_id
                        reacquire_bbox = None
                        state = TrackState.AUTO_TRACK

            if args.detect_track:
                track_ok = track_bbox is not None and dkf.is_initialized()
                track_score = track_score if track_ok else 0.0
            elif tracker.initialized:
                if tracker_init_frame_id == frame_id and track_bbox is not None:
                    track_score = max(track_score, 1.0)
                    track_ok = True
                else:
                    track_bbox, track_score, track_ok = tracker.update(frame)
                if track_ok:
                    dkf_ok = dkf.update_tracker(
                        track_bbox,
                        track_score,
                        step_dt,
                        measurement_delay_sec=measurement_delay_sec,
                        camera_motion=camera_motion,
                    )
                    if not dkf_ok:
                        dkf.reanchor_from_bbox(track_bbox, step_dt, camera_motion=camera_motion)
                    if not update_predictor_from_bbox(track_bbox, frame.shape, frame_ts, now, track_score):
                        predictor.reset()
                        update_predictor_from_bbox(track_bbox, frame.shape, frame_ts, now, track_score)
                    last_kf_update_ts = now
                    pred_center = predictor.predict_future(predict_ms / 1000.0)
                elif cfg["control"].get("stop_on_tracker_lost", True):
                    dkf.mark_lost()
                    if dkf.is_initialized() and dkf.lost_frames <= int(cfg.get("dkf", {}).get("max_predict_lost_count", 3)):
                        track_ok = True
                        track_score = 0.0
                        track_bbox = dkf.get_predicted_bbox(0.0)
                    else:
                        enter_lost(now)

            key = cv2.waitKey(1) & 0xFF if show_gui else 255
            if mouse.click:
                det = select_by_click(detections, *mouse.click)
                selected_bbox = det.bbox_xyxy if det else make_click_bbox(frame.shape, *mouse.click)
                mouse.click = None
                if selected_bbox and (det is None or is_trackable_bbox(selected_bbox, frame.shape, cfg, det)):
                    if args.detect_track:
                        track_bbox = selected_bbox
                        active_target_meta = detection_meta(det)
                        init_target_filters(track_bbox)
                        dkf.update_detector(
                            track_bbox,
                            1.0,
                            step_dt,
                            measurement_delay_sec=measurement_delay_sec,
                            camera_motion=camera_motion,
                        )
                        update_predictor_from_bbox(track_bbox, frame.shape, frame_ts, now, 1.0)
                        servo.reset()
                        detect_miss_count = 0
                        last_detector_ok_ts = now
                        last_kf_update_ts = now
                        pred_center = predictor.predict_future(predict_ms / 1000.0)
                        state = TrackState.AUTO_TRACK if auto_track_enabled else TrackState.MANUAL_TRACK
                    elif tracker.init(frame, selected_bbox) and init_target_filters(selected_bbox):
                        servo.reset()
                        track_bbox = selected_bbox
                        active_target_meta = detection_meta(det)
                        last_detector_ok_ts = now
                        last_kf_update_ts = now
                        last_template_update_frame = frame_id
                        tracker_init_frame_id = frame_id
                        reacquire_bbox = None
                        state = TrackState.MANUAL_TRACK
            if key in (ord("t"), ord("T")):
                if not tracker.initialized and detections:
                    det = choose_auto_detection(detections, frame.shape, cfg, predicted_bbox=dkf.get_bbox())
                    if det:
                        if tracker.init(frame, det.bbox_xyxy) and init_target_filters(det.bbox_xyxy):
                            servo.reset()
                            track_bbox = det.bbox_xyxy
                            active_target_meta = detection_meta(det)
                            last_detector_ok_ts = now
                            last_kf_update_ts = now
                            last_template_update_frame = frame_id
                            tracker_init_frame_id = frame_id
                            reacquire_bbox = None
                if tracker.initialized:
                    state = TrackState.AUTO_TRACK
            elif key in (ord("i"), ord("I")):
                if show_gui:
                    roi = cv2.selectROI(window, frame, False, False)
                    x, y, w, h = roi
                    roi_bbox = (x, y, x + w, y + h)
                    if w > 0 and h > 0 and tracker.init(frame, roi_bbox) and init_target_filters(roi_bbox):
                        servo.reset()
                        track_bbox = roi_bbox
                        active_target_meta = None
                        tracker_init_frame_id = frame_id
                        state = TrackState.MANUAL_TRACK
            elif key in (ord("m"), ord("M")):
                state = TrackState.MANUAL_TRACK if tracker.initialized else TrackState.IDLE
                request_stop()
            elif key in (ord("r"), ord("R")):
                state = TrackState.REACQUIRE
                tracker.reset()
                reset_target_filters()
                reacquire_bbox = None
                active_target_meta = None
                request_stop()
            elif key in (ord("c"), ord("C")):
                gimbal.center()
            elif key == 32:
                state = TrackState.STOPPED
                tracker.reset()
                reset_target_filters()
                servo.reset()
                reacquire_bbox = None
                active_target_meta = None
                request_stop()
            elif key == 27:
                state = TrackState.SAFE_STOP
                request_stop()
                break

            yaw_speed = last_yaw_speed
            pitch_speed = last_pitch_speed
            err_x = err_y = 0.0
            if predictor.initialized:
                predictor.predict_to(now, (last_yaw_speed, last_pitch_speed))
                pred_center = predictor.predict_future(predict_ms / 1000.0)
            catchup_score = 0.0
            velocity_norm = 0.0
            if dkf_cfg.get("enabled", True):
                ahead_time = base_latency_sec + pipeline_latency_sec + measured_frame_sec
                current_bbox = dkf.get_bbox() if dkf.is_initialized() else track_bbox
                current_center = bbox_center(current_bbox) if current_bbox is not None else None
                current_err_x, current_err_y = servo.measure_error(frame.shape, current_center)
                if current_err_x is not None and current_err_y is not None:
                    error_mag = max(abs(current_err_x), abs(current_err_y))
                    vx, vy = dkf.get_velocity()
                    h, w = frame.shape[:2]
                    velocity_norm = math.sqrt((vx / max(1.0, w * 0.5)) ** 2 + (vy / max(1.0, h * 0.5)) ** 2)
                    catchup_error = float(dkf_cfg.get("catchup_error", 0.12))
                    settle_error = float(dkf_cfg.get("settle_error", 0.05))
                    catchup_vel_norm = float(dkf_cfg.get("catchup_vel_norm", 0.18))
                    if error_mag > settle_error or velocity_norm > catchup_vel_norm:
                        err_score = (error_mag - settle_error) / max(1e-6, catchup_error - settle_error)
                        vel_score = velocity_norm / max(1e-6, catchup_vel_norm)
                        catchup_score = max(0.0, min(1.0, max(err_score, vel_score)))
                        ahead_time += catchup_score * float(dkf_cfg.get("catchup_extra_ms", 80.0)) / 1000.0
                if dkf.is_stationary():
                    ahead_time *= float(dkf_cfg.get("stationary_ahead_scale", 0.10))
                    catchup_score = 0.0
                else:
                    ahead_time *= max(float(dkf_cfg.get("min_motion_ahead_scale", 0.35)), dkf.motion_score())
                ahead_time = max(float(dkf_cfg.get("min_ahead_time", 0.0)), ahead_time)
                ahead_time = min(float(dkf_cfg.get("max_ahead_time", dkf.max_dt)), ahead_time)
            else:
                ahead_time = 0.0
            ego_vx = ego_vy = 0.0
            if bool(dkf_cfg.get("camera_motion_compensation", False)):
                if str(dkf_cfg.get("camera_motion_units", "command")).lower() in {"px_s", "pixel_s", "pixels_per_second"}:
                    ego_vx = float(camera_motion[0])
                    ego_vy = float(camera_motion[1])
                else:
                    ego_vx = -float(dkf_cfg.get("yaw_px_per_cmd", 0.0)) * float(camera_motion[0])
                    ego_vy = -float(dkf_cfg.get("pitch_px_per_cmd", 0.0)) * float(camera_motion[1])
            dkf_vx, dkf_vy = dkf.get_velocity()
            control_bbox = dkf.get_predicted_bbox(ahead_time, camera_motion=camera_motion) if dkf.is_initialized() else None
            center_target = bbox_center(control_bbox) if control_bbox is not None else (
                pred_center if pred_center is not None else (bbox_center(track_bbox) if track_bbox is not None else None)
            )
            if control_bbox is not None:
                pred_center = bbox_center(control_bbox)
            if is_tracking_state(state) and track_ok and center_target is not None:
                if track_bbox is not None and not is_trackable_bbox(track_bbox, frame.shape, cfg, active_target_meta):
                    enter_lost(now)
                    last_yaw_speed = 0
                    last_pitch_speed = 0
                    yaw_speed = pitch_speed = 0
                    track_ok = False
                    continue
                err_x, err_y = servo.measure_error(frame.shape, center_target)
                if err_x is None or err_y is None:
                    enter_lost(now)
                    continue
                if now - last_kf_update_ts > float(cfg["prediction"].get("max_kf_age_ms", 150)) / 1000.0:
                    enter_lost(now)
                    last_yaw_speed = 0
                    last_pitch_speed = 0
                    yaw_speed = pitch_speed = 0
                    track_ok = False
                    continue
                max_dkf_uncertainty = float(cfg.get("dkf", {}).get("max_uncertainty_px", cfg["prediction"].get("max_sigma_px", 80)))
                if dkf.is_initialized() and dkf.uncertainty() > max_dkf_uncertainty:
                    enter_lost(now)
                    last_yaw_speed = 0
                    last_pitch_speed = 0
                    yaw_speed = pitch_speed = 0
                    track_ok = False
                    continue
                if (
                    bool(cfg["control"].get("strict_detector_gate", False))
                    and now - last_detector_ok_ts > float(cfg["control"].get("max_detector_age_ms", 350)) / 1000.0
                ):
                    enter_lost(now)
                    last_yaw_speed = 0
                    last_pitch_speed = 0
                    yaw_speed = pitch_speed = 0
                    track_ok = False
                    continue
                if max(abs(err_x), abs(err_y)) > float(cfg["control"].get("max_center_error", 0.85)):
                    enter_lost(now)
                    last_yaw_speed = 0
                    last_pitch_speed = 0
                    yaw_speed = pitch_speed = 0
                    track_ok = False
                    continue
                command_period = 1.0 / max(1.0, float(cfg["control"].get("command_hz", 25)))
                if now - last_cmd_ts >= command_period:
                    cmd_dt = now - last_cmd_ts if last_cmd_ts > 0.0 else command_period
                    gain_scale = predictor.confidence_scale()
                    if dkf.lost_frames > 0:
                        gain_scale *= float(cfg.get("dkf", {}).get("lost_control_scale", 0.25))
                    gain_scale *= 1.0 + catchup_score * float(dkf_cfg.get("catchup_gain", 0.45))
                    raw_yaw_speed, raw_pitch_speed, err_x, err_y = servo.compute_bbox(
                        frame.shape,
                        control_bbox or track_bbox,
                        dkf.get_velocity(),
                        gain_scale=gain_scale,
                    )
                    yaw_speed, pitch_speed = limit_speed_command(raw_yaw_speed, raw_pitch_speed, cmd_dt)
                    speed_ramp.set_target(yaw_speed, pitch_speed)
                    last_yaw_speed = yaw_speed
                    last_pitch_speed = pitch_speed
                    last_cmd_ts = now
            elif is_tracking_state(state):
                request_stop()
                last_yaw_speed = 0
                last_pitch_speed = 0
            else:
                last_yaw_speed = 0
                last_pitch_speed = 0

            loop_dt = max(1e-3, now - last_loop_ts)
            last_loop_ts = now
            sigma_x, sigma_y = predictor.get_sigma()
            dkf_unc = dkf.uncertainty()
            hud = {
                "age_ms": f"{frame_age_ms:.0f}",
                "ctrl_hz": f"{1.0 / loop_dt:.1f}",
                "yaw": yaw_speed,
                "pitch": pitch_speed,
                "ex": f"{err_x:.2f}",
                "ey": f"{err_y:.2f}",
                "score": f"{track_score:.2f}",
                "pred_ms": f"{predict_ms:.0f}",
                "ahead_ms": f"{ahead_time * 1000.0:.0f}",
                "catch": f"{catchup_score:.2f}",
                "stat": int(dkf.is_stationary()),
                "vel": f"{dkf_vx:.0f},{dkf_vy:.0f}",
                "ego": f"{ego_vx:.0f},{ego_vy:.0f}",
                "dkf": f"{dkf_unc:.1f}" if dkf.is_initialized() else "-",
            }
            record_frame = frame.copy()
            draw_overlay(frame, state, detections, track_bbox, pred_center, hud)
            human_action = {
                "source": operator_action.get("source", "none"),
                "timestamp": float(operator_action.get("time", 0.0) or 0.0),
                "name": operator_action.get("action", "none"),
                "yaw": int(operator_action.get("yaw", 0) or 0),
                "pitch": int(operator_action.get("pitch", 0) or 0),
                "zoom": float(operator_action.get("zoom", 1.0) or 1.0),
                "zoom_direction": int(operator_action.get("zoom_direction", 0) or 0),
                "track_mode": operator_action.get("track_mode", "manual"),
                "recording": bool(operator_action.get("recording", False)),
                "age_ms": max(0.0, (now - float(operator_action.get("time", 0.0) or 0.0)) * 1000.0)
                if operator_action.get("time", 0.0)
                else None,
            }
            smolvla_action = [
                max(-1.0, min(1.0, human_action["yaw"] / 100.0)),
                max(-1.0, min(1.0, human_action["pitch"] / 100.0)),
                max(-1.0, min(1.0, float(human_action["zoom_direction"]))),
            ]
            target_center = bbox_center(track_bbox) if track_bbox else None
            control_center = bbox_center(control_bbox) if control_bbox else None
            target_cls_id = getattr(active_target_meta, "cls_id", None) if active_target_meta is not None else None
            target_cls_name = getattr(active_target_meta, "cls_name", "") if active_target_meta is not None else ""
            recorder.record_step(
                {
                    "timestamp": now,
                    "frame_index": frame_id,
                    "dt": loop_dt,
                    "frame_age_ms": frame_age_ms,
                    "state": state.value,
                    "target_class": {"cls_id": target_cls_id, "cls_name": target_cls_name},
                    "tracker_bbox": list(track_bbox) if track_bbox else None,
                    "control_bbox": list(control_bbox) if control_bbox else None,
                    "tracker_bbox_norm": normalize_bbox_xyxy(track_bbox, record_frame.shape),
                    "control_bbox_norm": normalize_bbox_xyxy(control_bbox, record_frame.shape),
                    "tracker_score": track_score,
                    "predicted_center": list(pred_center) if pred_center else None,
                    "target_center_error_norm": normalize_center_error(target_center, record_frame.shape),
                    "control_center_error_norm": normalize_center_error(control_center, record_frame.shape),
                    "target_velocity": [dkf_vx, dkf_vy],
                    "camera_image_velocity": [ego_vx, ego_vy],
                    "dkf_sigma": [sigma_x, sigma_y],
                    "dkf_bbox_uncertainty": dkf_unc,
                    "dkf_ahead_ms": ahead_time * 1000.0,
                    "dkf_catchup_score": catchup_score,
                    "target_velocity_norm": velocity_norm,
                    "target_stationary": int(dkf.is_stationary()),
                    "dkf_lost_frames": dkf.lost_frames,
                    "dkf_update_accepted": dkf.last_update_accepted,
                    "dkf_reject_reason": dkf.last_reject_reason,
                    "err_x": err_x,
                    "err_y": err_y,
                    "detections": [
                        {"cls_id": d.cls_id, "cls_name": d.cls_name, "conf": d.conf, "bbox_xyxy": list(d.bbox_xyxy)}
                        for d in detections
                    ],
                    "observation": {
                        "frame_shape": list(record_frame.shape),
                        "state": state.value,
                        "target_bbox": list(track_bbox) if track_bbox else None,
                        "target_bbox_norm": normalize_bbox_xyxy(track_bbox, record_frame.shape),
                        "control_bbox_norm": normalize_bbox_xyxy(control_bbox, record_frame.shape),
                        "target_center_error": [err_x, err_y],
                        "target_center_error_norm": normalize_center_error(target_center, record_frame.shape),
                        "control_center_error_norm": normalize_center_error(control_center, record_frame.shape),
                        "detections_count": len(detections),
                        "target_class": {"cls_id": target_cls_id, "cls_name": target_cls_name},
                        "state_vector": [
                            err_x,
                            err_y,
                            dkf_vx / 1000.0,
                            dkf_vy / 1000.0,
                            ego_vx / 1000.0,
                            ego_vy / 1000.0,
                            float(yaw_speed) / 100.0,
                            float(pitch_speed) / 100.0,
                            float(track_score),
                            1.0 if dkf.is_stationary() else 0.0,
                        ],
                    },
                    "action": human_action,
                    "action_vector": smolvla_action,
                    "autonomy_action": {
                        "yaw_speed": yaw_speed,
                        "pitch_speed": pitch_speed,
                        "zoom_direction": 0,
                        "auto_track_enable": int(is_auto_detection_state(state, auto_track_enabled)),
                        "manual_track_enable": int(state == TrackState.MANUAL_TRACK),
                        "stop_enable": int(state in {TrackState.STOPPED, TrackState.SAFE_STOP, TrackState.LOST}),
                    },
                },
                record_frame,
            )
            status_interval = float(cfg["runtime"].get("console_status_sec", 1.0))
            if status_interval > 0 and (now - last_status_ts >= status_interval or state != last_printed_state):
                last_status_ts = now
                last_printed_state = state
                print(
                    "status "
                    f"state={state.value} frame={frame_id} age_ms={frame_age_ms:.0f} "
                    f"det={len(detections)} track={int(track_ok)} yaw={yaw_speed} pitch={pitch_speed} "
                    f"ex={err_x:.3f} ey={err_y:.3f} ahead_ms={ahead_time * 1000.0:.0f} "
                    f"catch={catchup_score:.2f} stationary={int(dkf.is_stationary())} "
                    f"vel=({dkf_vx:.0f},{dkf_vy:.0f}) ego=({ego_vx:.0f},{ego_vy:.0f}) "
                    f"dkf_unc={dkf_unc:.1f} lost_frames={dkf.lost_frames} "
                    f"stale={stale_count} dup={duplicate_count} dry_run={int(gimbal.dry_run)}",
                    flush=True,
                )
            preview.publish(frame, now)
            if show_gui and now - last_display_ts >= display_interval:
                cv2.imshow(window, frame)
                last_display_ts = now
            if args.max_frames and frame_id >= args.max_frames:
                break
    finally:
        request_stop()
        capture.stop()
        recorder.close()
        if show_gui:
            cv2.destroyAllWindows()
        speed_ramp.close()
        gimbal.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
