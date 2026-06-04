# VLA Roadmap for MLLCV

MLLCV is being extended from a low-latency tracking prototype into a data-driven robotic perception project.

## Current System

```text
RTSP Camera
  -> LatestFrameRTSP
  -> YOLO Detector / Manual ROI
  -> AsymTrack Tracker
  -> Kalman Prediction
  -> VisualServo
  -> A8 Mini UDP Speed Control
```

## Planned VLA System

```text
Expert Controller / Human Teleoperation
  -> Observation-Action Recorder
  -> Episode Dataset
  -> LeRobot-Compatible Conversion
  -> Policy Training
  -> Policy Inference
  -> Safe Gimbal Control
```

## Milestone 1: Data Recording

- Record camera frame paths
- Record detection and tracking state
- Record Kalman state and latency
- Record gimbal telemetry
- Record expert control action
- Attach language task instruction

## Milestone 2: Dataset Validation

- Validate JSONL schema
- Validate timestamps and frame order
- Check missing images
- Check action ranges
- Generate episode summary

## Milestone 3: LeRobot-Compatible Conversion

- Map RGB/IR frames to image observations
- Map tracking and gimbal telemetry to state vectors
- Map yaw/pitch/zoom commands to action vectors
- Store task instruction metadata
- Prepare train/eval split

## Milestone 4: Policy Learning

Possible training directions:

- behavior cloning with image features and state
- imitation learning from expert visual servo controller
- LeRobot policy training
- future VLA-style instruction-conditioned policy

## Milestone 5: Safe Deployment

- dry-run inference
- action range limits
- acceleration limits
- emergency stop
- confidence-based fallback to classical tracker/controller
