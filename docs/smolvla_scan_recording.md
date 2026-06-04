# SmolVLA Human Scan Recording

This project can record human-operated gimbal scanning episodes for later SmolVLA-style imitation learning.

## Start

Start the dashboard and tracker with the same operator state file:

```bash
python scripts/gimbal_dashboard.py \
  --port 7860 \
  --stream-fps 25 \
  --preview /tmp/source_track_preview.jpg \
  --command-file /tmp/source_track_command.json \
  --operator-state-file /tmp/source_track_operator_action.json
```

```bash
conda run --no-capture-output -n smolvla-deploy \
  python main_low_latency_track.py \
  --config config_low_latency.yaml \
  --real-gimbal \
  --no-gui \
  --preview-jpeg /tmp/source_track_preview.jpg \
  --command-file /tmp/source_track_command.json \
  --operator-state-file /tmp/source_track_operator_action.json
```

Open:

```text
http://127.0.0.1:7860
```

## Record An Episode

1. Click `REC START`.
2. Manually scan with the dashboard direction buttons or keyboard.
3. Use zoom controls if needed.
4. Click `REC STOP`.

Episodes are saved under:

```text
recordings/smolvla_scan/episode_YYYYMMDD_HHMMSS/
```

## Episode Layout

```text
episode_YYYYMMDD_HHMMSS/
  metadata.json
  data.jsonl
  video.mp4
  frames/
    000000.jpg
    000001.jpg
```

`config_low_latency.yaml` currently uses manual episode start:

```yaml
record:
  enable: true
  auto_start: false
  dataset: "smolvla_scan"
  root: "recordings/smolvla_scan"
  save_video: true
  save_frames: true
  save_jsonl: true
  fps: 25
```

## Row Schema

Each `data.jsonl` row contains:

```json
{
  "timestamp": 0.0,
  "frame_index": 0,
  "observation": {
    "image": "frames/000000.jpg",
    "frame_shape": [720, 1280, 3],
    "state": "IDLE",
    "target_bbox": null,
    "target_center_error": [0.0, 0.0],
    "detections_count": 0
  },
  "action": {
    "source": "dashboard",
    "timestamp": 0.0,
    "name": "speed",
    "yaw": 20,
    "pitch": 0,
    "zoom": 1.0,
    "zoom_direction": 0,
    "track_mode": "manual",
    "recording": true
  },
  "action_vector": [0.2, 0.0, 0.0],
  "autonomy_action": {
    "yaw_speed": 0,
    "pitch_speed": 0,
    "zoom_direction": 0
  }
}
```

Use `observation.image` plus `action_vector` as the first imitation-learning pair:

```text
action_vector = [yaw / 100, pitch / 100, zoom_direction]
```

Rows are sanitized before writing, so non-finite values such as `NaN` or `Infinity` become `null` for strict JSON readers.
