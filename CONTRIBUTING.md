# Contributing to MLLCV

Thank you for helping improve MLLCV.

MLLCV is an early-stage low-latency visual tracking and gimbal-control prototype. Contributions should keep the project easier to run, safer to operate, and simpler to review.

## Set Up the Project

```bash
git clone https://github.com/Stevenzzz1996/MLLCV.git
cd MLLCV

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Some detector or tracker backends require optional packages, CUDA, TensorRT engines, or model weights that are not stored in this repository.

## Run Checks

Before opening a pull request, run:

```bash
python scripts/validate_project_structure.py
python -m compileall main_low_latency_track.py modules scripts
```

If your change touches pure-Python logic, add or run a focused local check. Do not require private RTSP streams, private model weights, GPUs, or real gimbal hardware for general CI.

## Submit Issues

When reporting a bug, include:

- What command you ran
- Which config file you used
- Whether this was dry-run or real-gimbal mode
- Python version and operating system
- Relevant logs or tracebacks
- Whether private model paths or RTSP URLs were redacted

Do not include credentials, private RTSP URLs, private recordings, or private model files.

## Submit Pull Requests

Good pull requests are focused and reviewable. Please include:

- What changed
- Why it changed
- How you tested it
- Risk level
- Related issue, if any

Avoid broad rewrites unless there is an issue or discussion that explains the migration.

## Code Style

- Prefer small functions with explicit names.
- Keep hardware-facing behavior conservative by default.
- Keep examples free of private paths, credentials, and model weights.
- Avoid changing `third_party/AsymTrack` unless the change is necessary and clearly explained.
- Keep comments useful and brief.

## Hardware Safety Notes

Any pull request that changes UDP control, visual-servo gains, sign conventions, speed limits, stop behavior, or real-gimbal defaults should explain the hardware risk.

By default, examples should use dry-run mode. Real hardware operation should require an explicit user action such as `--real-gimbal`.
