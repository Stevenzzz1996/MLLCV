from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class TrackState(str, Enum):
    IDLE = "IDLE"
    MANUAL_TRACK = "MANUAL_TRACK"
    AUTO_TRACK = "AUTO_TRACK"
    LOST = "LOST"
    REACQUIRE = "REACQUIRE"
    STOPPED = "STOPPED"
    SAFE_STOP = "SAFE_STOP"


@dataclass
class Detection:
    cls_id: int
    cls_name: str
    conf: float
    bbox_xyxy: tuple[float, float, float, float]

    @property
    def center(self) -> tuple[float, float]:
        x1, y1, x2, y2 = self.bbox_xyxy
        return (0.5 * (x1 + x2), 0.5 * (y1 + y2))

    @property
    def area(self) -> float:
        x1, y1, x2, y2 = self.bbox_xyxy
        return max(0.0, x2 - x1) * max(0.0, y2 - y1)


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def load_config(path: str | Path) -> dict[str, Any]:
    import yaml

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def bbox_center(bbox_xyxy: tuple[float, float, float, float]) -> tuple[float, float]:
    x1, y1, x2, y2 = bbox_xyxy
    return (0.5 * (x1 + x2), 0.5 * (y1 + y2))


def bbox_iou(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def xyxy_to_xywh(bbox_xyxy: tuple[float, float, float, float]) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = bbox_xyxy
    return (int(x1), int(y1), int(max(1, x2 - x1)), int(max(1, y2 - y1)))


def xywh_to_xyxy(bbox_xywh: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    x, y, w, h = bbox_xywh
    return (float(x), float(y), float(x + w), float(y + h))
