# Release Notes: v0.1.1

## Initial Public Prototype Release

`v0.1.1` marks the first public prototype release of the reorganized MLLCV low-latency visual tracking project.

## Main Features

- RTSP latest-frame capture for low-latency video ingestion.
- YOLO-style detector integration for initialization, target correction, and reacquisition.
- AsymTrack and OSTrack tracking integration paths.
- Delayed Kalman filter prediction for latency compensation.
- Visual-servo conversion from target-center error to yaw/pitch speed commands.
- Siyi A8 Mini UDP command wrapper with dry-run support.
- Example documentation for local-video and RTSP-based testing.

## Known Limitations

- This is a prototype and requires environment-specific tuning.
- Private model weights, TensorRT engines, RTSP URLs, and recordings are not included.
- Real gimbal operation depends on hardware orientation, network setup, and safe calibration.
- CI intentionally avoids hardware, private models, and GPU-only checks.
- Some scripts are research or experiment utilities rather than polished user-facing commands.

## Safety Notes

- Dry-run mode should be used before any real hardware command.
- Do not expose UDP control or RTSP streams on untrusted networks.
- Verify yaw and pitch signs before using `--real-gimbal`.
- Keep a manual stop or power-off path available during hardware tests.

## Next Roadmap Items

- Add synthetic tests for DKF and target selection.
- Add clearer hardware calibration docs.
- Add portable detector/tracker setup instructions.
- Add small public demo assets if licensing permits.
- Improve release packaging for external model assets.
