# Local Video Tracking Demo

This demo is for software-only validation with a local video file or webcam. It does not require an RTSP stream or real gimbal hardware.

## Webcam Smoke Run

```bash
python main_low_latency_track.py \
  --config examples/dry_run_tracking_config.yaml \
  --source 0 \
  --dry-run-gimbal \
  --no-yolo \
  --no-gui \
  --max-frames 30
```

## Local Video File

```bash
python main_low_latency_track.py \
  --config examples/dry_run_tracking_config.yaml \
  --source /path/to/local_video.mp4 \
  --dry-run-gimbal \
  --no-yolo \
  --no-gui \
  --max-frames 300
```

## Notes

- `--no-yolo` avoids loading private detector weights.
- `--dry-run-gimbal` avoids UDP hardware commands.
- `--no-gui` is useful for servers or CI-like environments.
- To test manual tracking with a GUI, remove `--no-gui` and select a target interactively.
