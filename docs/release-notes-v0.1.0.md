# MLLCV v0.1.0 - Low-Latency Tracking Prototype

This release reorganizes MLLCV into a low-latency computer vision and robotics perception project.

## Highlights

- Added A8 Mini low-latency predictive tracking prototype.
- Added RTSP latest-frame capture pipeline.
- Added YOLO detector integration.
- Added AsymTrack tracking workflow.
- Added Kalman prediction and visual servo control.
- Added dry-run gimbal mode and smoke-test commands.
- Added GitHub issue templates, PR template, workflows, CONTRIBUTING, CODE_OF_CONDUCT, and CHANGELOG.

## Known Limitations

- This is an early-stage prototype, not a production-ready robotics framework.
- Hardware operation requires careful sign calibration, speed limits, and stop-path validation.
- Private model weights, TensorRT engines, RTSP URLs, and recordings are not included.
- CI avoids checks that require unavailable hardware, private models, or GPU-specific runtime dependencies.

## Safety Notes

- Start in dry-run mode.
- Do not expose RTSP streams or UDP gimbal control on untrusted networks.
- Verify yaw/pitch signs before using `--real-gimbal`.
- Keep a manual stop or power-off path available during hardware testing.
