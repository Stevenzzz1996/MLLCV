# A8 Mini Low-Latency Predictive Tracking Prototype

This prototype wires the control loop described in the two design documents:

```text
LatestFrameRTSP -> YOLO detector -> AsymTrack -> Kalman prediction -> VisualServo -> A8 mini UDP speed control
```

Default detection uses the open-source Ultralytics `yolo26m.pt` weight, which is downloaded automatically on first run when the installed Ultralytics version supports YOLO26. Replace it with a trained project weight later by editing `config_low_latency.yaml`.

## Install

The current machine has a working conda environment named `calib` with Ultralytics and CUDA PyTorch:

```bash
conda activate calib
```

If you use another environment, install the Python dependencies:

```bash
pip install -r requirements.txt
```

## Run

Dry-run gimbal is enabled by default:

```bash
python3 main_low_latency_track.py --config config_low_latency.yaml
```

Skip detector loading while tuning RTSP latency, tracker, prediction, and gimbal control:

```bash
python3 main_low_latency_track.py --config config_low_latency.yaml --dry-run-gimbal --no-yolo
```

Use TCP RTSP if UDP shows too many HEVC reference-frame warnings:

```bash
python3 main_low_latency_track.py --config config_low_latency.yaml --rtsp-transport tcp --dry-run-gimbal --no-yolo
```

Smoke test without a GUI:

```bash
python3 main_low_latency_track.py --config config_low_latency.yaml --dry-run-gimbal --no-gui --no-yolo --max-frames 30
```

Set `runtime.dry_run_gimbal: false` only after confirming yaw/pitch direction and stop behavior.

## Controls

`T`: auto-select target and enter auto tracking
`I`: draw a manual ROI and initialize tracking without a detector
`M`: manual tracking
`W/A/S/D`: manual gimbal speed
`C`: center gimbal
`R`: reacquire
`Space`: stop
`ESC`: safe stop and exit
