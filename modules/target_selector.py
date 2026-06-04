from __future__ import annotations

from .common import Detection, bbox_center, bbox_iou
from .dkf_filter import valid_bbox


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def select_by_click(detections: list[Detection], x: int, y: int) -> Detection | None:
    hits = []
    for det in detections:
        x1, y1, x2, y2 = det.bbox_xyxy
        if x1 <= x <= x2 and y1 <= y <= y2:
            hits.append(det)
    if not hits:
        return None
    return max(hits, key=lambda d: (d.conf, -d.area))


def auto_select(
    detections: list[Detection],
    frame_shape,
    predicted_bbox=None,
    allowed_classes=None,
    min_area_ratio: float = 0.0,
    max_area_ratio: float = 1.0,
) -> Detection | None:
    if not detections:
        return None
    h, w = frame_shape[:2]
    frame_area = max(1.0, float(w * h))
    use_pred = valid_bbox(predicted_bbox)

    candidates = []
    for det in detections:
        cls_id = getattr(det, "cls_id", getattr(det, "cls", None))
        if allowed_classes is not None and cls_id not in allowed_classes:
            continue
        area_ratio = det.area / frame_area
        if area_ratio < min_area_ratio or area_ratio > max_area_ratio:
            continue
        candidates.append(det)
    if not candidates:
        return None

    def score(det: Detection) -> float:
        cx, cy = det.center
        area_ratio = det.area / frame_area
        area_score = _clamp01(1.0 - abs(area_ratio - 0.03) / 0.08)
        center_dist = (((cx - w * 0.5) / w) ** 2 + ((cy - h * 0.5) / h) ** 2) ** 0.5
        center_score = _clamp01(1.0 - 2.0 * center_dist)
        conf_score = _clamp01(det.conf)
        if use_pred:
            pred_iou_score = _clamp01(bbox_iou(predicted_bbox, det.bbox_xyxy))
            return 0.45 * conf_score + 0.35 * pred_iou_score + 0.10 * center_score + 0.10 * area_score
        return 0.55 * conf_score + 0.25 * center_score + 0.20 * area_score

    return max(candidates, key=score)


def match_detection_to_track(detections: list[Detection], track_bbox, frame_shape, min_iou: float = 0.05, max_center_dist: float = 0.35) -> Detection | None:
    if not detections or track_bbox is None:
        return None
    h, w = frame_shape[:2]
    tcx, tcy = bbox_center(track_bbox)

    def score(det: Detection) -> float:
        dcx, dcy = det.center
        center_dist = (((dcx - tcx) / max(1, w)) ** 2 + ((dcy - tcy) / max(1, h)) ** 2) ** 0.5
        return 2.0 * bbox_iou(track_bbox, det.bbox_xyxy) + 0.5 * det.conf - center_dist

    best = max(detections, key=score)
    iou = bbox_iou(track_bbox, best.bbox_xyxy)
    dcx, dcy = best.center
    center_dist = (((dcx - tcx) / max(1, w)) ** 2 + ((dcy - tcy) / max(1, h)) ** 2) ** 0.5
    if iou >= min_iou or center_dist <= max_center_dist:
        return best
    return None


class ConfirmBuffer:
    def __init__(
        self,
        confirm_frames: int,
        iou_thr: float = 0.45,
        max_center_jump_ratio: float = 0.15,
        require_same_class: bool = False,
    ) -> None:
        self.confirm_frames = max(1, int(confirm_frames))
        self.iou_thr = float(iou_thr)
        self.max_center_jump_ratio = float(max_center_jump_ratio)
        self.require_same_class = bool(require_same_class)
        self.items: list[Detection] = []

    def push(self, det: Detection) -> None:
        self.items.append(det)
        self.items = self.items[-self.confirm_frames :]

    def clear(self) -> None:
        self.items.clear()

    def is_stable(self, frame_shape=None) -> bool:
        if len(self.items) < self.confirm_frames:
            return False
        diag = None
        if frame_shape is not None and len(frame_shape) >= 2:
            h, w = frame_shape[:2]
            diag = max(1.0, (float(w * w + h * h)) ** 0.5)
        for i in range(1, len(self.items)):
            prev = self.items[i - 1]
            curr = self.items[i]
            if bbox_iou(prev.bbox_xyxy, curr.bbox_xyxy) < self.iou_thr:
                return False
            if self.require_same_class and getattr(prev, "cls_id", None) != getattr(curr, "cls_id", None):
                return False
            if diag is not None:
                pcx, pcy = prev.center
                ccx, ccy = curr.center
                jump = ((ccx - pcx) ** 2 + (ccy - pcy) ** 2) ** 0.5 / diag
                if jump > self.max_center_jump_ratio:
                    return False
        return True
