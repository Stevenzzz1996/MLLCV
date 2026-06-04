# Quick Start

This guide starts with software-only validation and then shows where hardware-specific configuration fits.

## 1. Clone and Install

```bash
git clone https://github.com/Stevenzzz1996/MLLCV.git
cd MLLCV

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The full runtime may need optional packages and hardware-specific engines depending on the selected detector or tracker backend. The repository does not include private model weights or TensorRT engines.

## 2. Validate Repository Structure

```bash
python scripts/validate_project_structure.py
python -m compileall main_low_latency_track.py modules scripts
```

These checks do not require a gimbal, RTSP stream, private model, or GPU.

## 3. Run a Dry-Run Smoke Command

Use a webcam or local video source and disable detector loading:

```bash
python main_low_latency_track.py \
  --config examples/dry_run_tracking_config.yaml \
  --source 0 \
  --dry-run-gimbal \
  --no-yolo \
  --no-gui \
  --max-frames 30
```

If no webcam is available, replace `--source 0` with a local video file path.

## 4. Configure Models

Detector and tracker model paths live in YAML:

- `yolo26.model`
- `asymtrack.model`
- `asymtrack.engine`
- `ostrack.engine`

Keep private models, generated TensorRT engines, and large weights outside Git. Use download instructions or external release assets instead.

## 5. Connect Hardware Carefully

Before using `--real-gimbal`:

- Confirm the A8 Mini IP and UDP port.
- Verify `gimbal.yaw_sign` and `gimbal.pitch_sign`.
- Keep `runtime.dry_run_gimbal: true` until stop behavior is tested.
- Test in a clear physical area with an operator able to stop the system.

See [A8 Mini Control](a8-mini-control.md) for safety notes.
