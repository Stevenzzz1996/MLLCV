"""Schema definitions for MLLCV VLA observation-action episodes.

The schema is intentionally lightweight and JSONL-friendly.
It is designed for gimbal-based robotic perception tasks where
camera frames, tracking states, gimbal telemetry, language instructions,
and expert actions are recorded as synchronized episodes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class GimbalTelemetry:
    yaw_deg: Optional[float] = None
    pitch_deg: Optional[float] = None
    zoom: Optional[float] = None
    mode: str = "unknown"


@dataclass
class TrackingState:
    bbox_xywh: Optional[List[float]] = None
    target_center_xy: Optional[List[float]] = None
    track_score: Optional[float] = None
    kalman_state: Optional[List[float]] = None
    latency_ms: Optional[float] = None


@dataclass
class Observation:
    rgb_image: Optional[str] = None
    ir_image: Optional[str] = None
    tracking: TrackingState = field(default_factory=TrackingState)
    gimbal: GimbalTelemetry = field(default_factory=GimbalTelemetry)
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Action:
    yaw_rate_deg_s: float = 0.0
    pitch_rate_deg_s: float = 0.0
    zoom_cmd: int = 0
    stop: bool = False
    mode: str = "track"


@dataclass
class EpisodeStep:
    episode_id: str
    frame_id: int
    timestamp: float
    instruction: str
    observation: Observation
    action: Action
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
