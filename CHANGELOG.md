# Changelog

## v0.1.0 - Low-Latency Tracking Prototype

### Added

- Reorganized MLLCV into a low-latency computer vision tracking and robotics perception prototype.
- Added A8 Mini low-latency predictive tracking workflow documentation.
- Added RTSP latest-frame capture pipeline documentation.
- Added YOLO detector integration notes.
- Added AsymTrack tracking workflow notes.
- Added Kalman prediction and visual servo control documentation.
- Added dry-run gimbal mode and smoke-test commands.
- Added GitHub issue templates and pull request template.
- Added lightweight GitHub Actions validation workflow.
- Added `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and `SECURITY.md`.

### Known Limitations

- This is an early-stage prototype and requires hardware-specific tuning.
- Private model weights, RTSP URLs, TensorRT engines, and recordings are not included.
- CI intentionally avoids hardware, GPU-only checks, and private assets.
