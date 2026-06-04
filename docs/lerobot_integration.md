# LeRobot Integration Plan

MLLCV plans to support conversion from MLLCV JSONL episodes to a LeRobot-compatible dataset format.

## Why LeRobot?

LeRobot provides tools, datasets, and models for real-world robotics in PyTorch. Its dataset format is designed for robot learning data, including visual observations, state, actions, and metadata.

## Planned Mapping

| MLLCV field | LeRobot-style meaning |
|---|---|
| `observation.rgb_image` | visual observation |
| `observation.ir_image` | optional secondary visual observation |
| `observation.tracking.bbox_xywh` | state / perception metadata |
| `observation.tracking.kalman_state` | state |
| `observation.gimbal.yaw_deg` | robot state |
| `observation.gimbal.pitch_deg` | robot state |
| `observation.gimbal.zoom` | robot state |
| `instruction` | task / language instruction |
| `action.yaw_rate_deg_s` | action |
| `action.pitch_rate_deg_s` | action |
| `action.zoom_cmd` | action |

## Implementation Stages

1. Validate local JSONL episodes.
2. Build state/action vectors.
3. Convert image paths and metadata.
4. Create local dataset directory.
5. Add optional Hugging Face Hub publishing instructions.
6. Add training examples after the data schema stabilizes.

## Current Status

The converter is currently a validation stub. Full conversion will be added after real-world recording is stable.
