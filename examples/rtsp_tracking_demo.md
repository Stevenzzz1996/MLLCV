# RTSP Tracking Demo

This demo explains how to run against an RTSP source without committing private stream URLs.

## Private URL Handling

Do not commit real RTSP URLs, credentials, tokens, or camera IP addresses. Keep them in a local config file that is not pushed, or pass them at runtime:

```bash
python main_low_latency_track.py \
  --config examples/dry_run_tracking_config.yaml \
  --source "rtsp://USER:PASS@CAMERA_HOST:8554/main.264" \
  --rtsp-transport tcp \
  --dry-run-gimbal \
  --no-yolo \
  --no-gui \
  --max-frames 300
```

## UDP vs TCP RTSP

- Use `--rtsp-transport udp` when the network is clean and low latency is the priority.
- Use `--rtsp-transport tcp` when UDP packet loss causes decode warnings or unstable frames.

## Moving Toward Hardware

Before using `--real-gimbal`, verify dry-run behavior and read:

- [A8 Mini Control](../docs/a8-mini-control.md)
- [Security Policy](../SECURITY.md)

Real hardware should be tested with conservative speed limits and a manual stop path.
