# System Architecture

MLLCV is organized around a low-latency tracking and control loop. The goal is to keep the newest available video frame flowing through detector, tracker, prediction, and gimbal-control stages without building a long frame queue.

## Data Flow

```text
RTSP / video source
  -> LatestFrameRTSP
  -> detector initialization or reacquisition
  -> AsymTrack / OSTrack single-object tracker
  -> delayed Kalman filter prediction
  -> visual-servo speed command
  -> Siyi A8 Mini UDP command
```

## Main Components

- `main_low_latency_track.py`: runtime orchestration, CLI flags, state machine, GUI controls, detector/tracker/predictor integration, and safe-stop behavior.
- `modules/latest_frame_rtsp.py`: latest-frame capture for RTSP or local video sources.
- `modules/yolo26_detector.py`: detector wrapper used for initialization, correction, and reacquisition.
- `modules/asymtrack_tracker.py`: AsymTrack wrapper. The vendored upstream project lives in `third_party/AsymTrack`.
- `modules/ostrack_tracker.py`: OSTrack TensorRT integration path.
- `modules/dkf_filter.py`: delayed Kalman filter for bounding-box state, velocity, delayed measurements, and camera-motion compensation.
- `modules/visual_servo.py`: target-center error to yaw/pitch speed command conversion.
- `modules/gimbal_controller.py`: Siyi A8 Mini UDP packet construction and send logic.

## Runtime States

The main control loop uses explicit states from `modules/common.py`:

- `IDLE`: no active target.
- `MANUAL_TRACK`: operator-selected target.
- `AUTO_TRACK`: detector-selected target.
- `LOST`: target lost and commands stopped.
- `REACQUIRE`: detector-assisted search for the target.
- `STOPPED` and `SAFE_STOP`: stopped states.

## Latency Strategy

The prototype combines several latency controls:

- Latest-frame capture avoids processing stale queued RTSP frames.
- Detector intervals limit expensive detector calls while tracking is healthy.
- DKF prediction estimates target position at the control horizon.
- Visual-servo speed limits and smoothing prevent aggressive command jumps.

This is still a prototype. Real deployments should measure end-to-end latency on the target hardware and tune configuration values accordingly.
