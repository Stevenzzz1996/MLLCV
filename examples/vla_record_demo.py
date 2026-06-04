"""Mock VLA recording demo.

This demo creates a small fake observation-action episode without requiring
a camera, model, RTSP stream, or A8 Mini gimbal. It is intended for CI,
documentation, and quick verification of the VLA recording schema.
"""

from __future__ import annotations

import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mllcv.vla.recorder import VLAEpisodeRecorder
from mllcv.vla.schema import Action, GimbalTelemetry, Observation, TrackingState


def main() -> None:
    output_dir = Path("data/mock_vla_episode")
    recorder = VLAEpisodeRecorder(
        output_dir=output_dir,
        episode_id="episode_mock_000001",
        instruction="Keep the target centered in the image.",
    )

    try:
        for i in range(10):
            cx = 640 + 20 * math.sin(i / 3)
            cy = 360 + 10 * math.cos(i / 3)
            obs = Observation(
                rgb_image=None,
                tracking=TrackingState(
                    bbox_xywh=[cx - 40, cy - 30, 80, 60],
                    target_center_xy=[cx, cy],
                    track_score=0.90,
                    kalman_state=[cx, cy, 0.0, 0.0],
                    latency_ms=120.0,
                ),
                gimbal=GimbalTelemetry(
                    yaw_deg=1.0 + 0.1 * i,
                    pitch_deg=-2.0,
                    zoom=1.0,
                    mode="dry_run",
                ),
            )
            action = Action(
                yaw_rate_deg_s=float((640 - cx) * 0.02),
                pitch_rate_deg_s=float((360 - cy) * 0.02),
                zoom_cmd=0,
                stop=False,
                mode="track",
            )
            recorder.record(observation=obs, action=action, timestamp=time.time())
    finally:
        recorder.close()

    print(f"Mock VLA episode saved to: {output_dir}")


if __name__ == "__main__":
    main()
