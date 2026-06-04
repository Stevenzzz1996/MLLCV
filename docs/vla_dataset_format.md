# MLLCV VLA Dataset Format

The current MLLCV VLA dataset format is JSONL-based. Each line is a synchronized step.

## File Layout

```text
episode_000001/
├── episode_000001.jsonl
├── frames/
│   ├── rgb_000000.jpg
│   ├── rgb_000001.jpg
│   └── ...
└── meta.json
```

## Step Schema

```json
{
  "episode_id": "episode_000001",
  "frame_id": 0,
  "timestamp": 1720000000.123,
  "instruction": "Keep the target centered in the image.",
  "observation": {
    "rgb_image": "frames/rgb_000000.jpg",
    "ir_image": null,
    "tracking": {
      "bbox_xywh": [600, 330, 80, 60],
      "target_center_xy": [640, 360],
      "track_score": 0.91,
      "kalman_state": [640, 360, 0.0, 0.0],
      "latency_ms": 120.0
    },
    "gimbal": {
      "yaw_deg": 1.2,
      "pitch_deg": -2.0,
      "zoom": 1.0,
      "mode": "track"
    }
  },
  "action": {
    "yaw_rate_deg_s": 2.0,
    "pitch_rate_deg_s": -1.0,
    "zoom_cmd": 0,
    "stop": false,
    "mode": "track"
  }
}
```

## Notes

- `bbox_xywh` uses image pixel coordinates.
- `yaw_rate_deg_s` and `pitch_rate_deg_s` use degrees per second.
- `zoom_cmd` may be defined as `-1`, `0`, `+1`, or device-specific values.
- `instruction` should describe the task, not the implementation.
- All paths should be relative to the episode directory.
