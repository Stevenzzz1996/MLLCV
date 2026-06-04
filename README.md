# MLLCV: Low-Latency Computer Vision Tracking and Robotics Perception

MLLCV is an open-source computer vision and robotics perception project focused on low-latency target detection, single-object tracking, Kalman-based prediction, and visual servo control.

The current prototype demonstrates an end-to-end A8 Mini gimbal tracking pipeline:

```text
LatestFrameRTSP -> YOLO detector -> AsymTrack tracker -> Kalman prediction -> VisualServo -> A8 Mini UDP speed control
```

It is designed for robotics, UAV observation, surveillance, edge AI, and real-time computer vision developers who want to study a practical tracking-to-control pipeline rather than an isolated detector or tracker demo.

> Status: prototype. This repository is designed to help developers study and iterate on a real-time tracking control loop. It is not presented as a production-ready framework and does not claim broad adoption or benchmark leadership.

## Why This Project Matters

Real-time visual tracking systems often fail for reasons that are not visible in isolated detector or tracker demos: stale RTSP frames, detector reacquisition delays, tracker drift, camera motion, control-loop latency, and hardware safety constraints. MLLCV is intended to make those integration points explicit so robotics and edge-AI developers can inspect, reproduce, and improve the full loop from video input to gimbal command output.

## Key Features

- RTSP latest-frame video capture to reduce queueing latency.
- YOLO-style detector support for target initialization, correction, and reacquisition.
- AsymTrack and OSTrack integration paths for single-object tracking.
- Delayed Kalman filter (DKF) prediction for latency compensation and smoother target estimates.
- Visual-servo speed command generation with dead zones, smoothing, and command limits.
- Siyi A8 Mini UDP packet support for speed, center, angle, and zoom commands.
- Dry-run mode for software-only validation without sending hardware commands.
- Lightweight CI checks suitable for external contributors without private model weights or hardware.

## System Architecture

```text
RTSP Camera / Local Video
   ↓
LatestFrameReader
   ↓
YOLO Detector / Manual ROI
   ↓
AsymTrack / OSTrack
   ↓
Kalman Prediction
   ↓
Visual Servo Controller
   ↓
A8 Mini UDP Gimbal Control
```

The default control path is conservative: `runtime.dry_run_gimbal` is enabled in the sample configuration. Real UDP control requires an explicit `--real-gimbal` run and hardware-specific validation.

## Quick Start

Create an environment and install the Python dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run a syntax and structure check:

```bash
python -m compileall main_low_latency_track.py modules scripts
python scripts/validate_project_structure.py
```

Run a software-only smoke command with detector loading disabled:

```bash
python main_low_latency_track.py \
  --config examples/dry_run_tracking_config.yaml \
  --source 0 \
  --dry-run-gimbal \
  --no-yolo \
  --no-gui \
  --max-frames 30
```

For local video and RTSP examples, see:

- [Local Video Tracking Demo](examples/local_video_tracking_demo.md)
- [RTSP Tracking Demo](examples/rtsp_tracking_demo.md)

## Configuration

The main runtime configuration is YAML-based. The most important sections are:

- `video`: input source, RTSP transport, buffer behavior, and frame orientation.
- `yolo26`: detector backend, model path, confidence threshold, classes, and detection intervals.
- `tracking`, `asymtrack`, `ostrack`: tracker backend and model or engine paths.
- `prediction` and `dkf`: latency estimate, process noise, measurement noise, delayed-measurement compensation, and camera-motion compensation.
- `servo`: proportional gains, dead zones, speed limits, and yaw/pitch signs.
- `gimbal`: Siyi A8 Mini IP, UDP port, command signs, and ACK behavior.
- `runtime`: GUI, recording, console status, and dry-run behavior.

The checked-in examples intentionally avoid private RTSP URLs and private model weights. Real deployments should keep hardware addresses, private stream URLs, and local model paths outside public commits.

## Dry-Run Mode

Dry-run mode is the recommended first step for every setup. In dry-run mode the control loop can compute commands, draw overlays, and exercise tracking logic without sending UDP packets to the gimbal.

Use one or more of:

```bash
--dry-run-gimbal
--no-yolo
--no-gui
--max-frames 30
```

Only use `--real-gimbal` after confirming:

- The A8 Mini IP and port are correct.
- Yaw and pitch signs match the physical mount.
- Stop behavior is verified.
- The camera has a safe range of motion.
- A human operator can cut power or stop the process.

## Roadmap

- Improve portable sample configs that do not depend on private models.
- Add synthetic-frame tests for target selection and DKF prediction.
- Add optional local-video demo fixtures that are small enough for the repository.
- Document calibration steps for yaw/pitch signs and visual-servo gains.
- Separate hardware-facing scripts from pure software validation tools.
- Add release packaging notes for model assets stored outside Git.

See [docs/roadmap.md](docs/roadmap.md) for more detail.

## Contributing

Contributions are welcome when they make the prototype easier to understand, test, reproduce, or operate safely. Good contributions include documentation fixes, safe defaults, portable examples, small validation scripts, and focused bug fixes.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening issues or pull requests.

## Citation / Acknowledgment

This project currently vendors AsymTrack under `third_party/AsymTrack` and uses it as one supported tracking backend. Please preserve the upstream license and cite or acknowledge upstream tracker work when publishing derived experiments.

The Siyi A8 Mini UDP support is based on the packet structure documented in this repository and should be validated against official hardware documentation before real operation.

## Safety

Network video streams, UDP control packets, model files, and physical gimbals all have safety implications. Do not publish private stream URLs, credentials, private model weights, or sensitive recordings. Read [SECURITY.md](SECURITY.md) and [docs/a8-mini-control.md](docs/a8-mini-control.md) before connecting real hardware.
