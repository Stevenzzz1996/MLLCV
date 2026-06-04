from __future__ import annotations

from pathlib import Path


REQUIRED_PATHS = [
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "requirements.txt",
    "main_low_latency_track.py",
    "config_low_latency.yaml",
    "docs",
    "docs/architecture.md",
    "docs/quickstart.md",
    "docs/a8-mini-control.md",
    "docs/dkf-latency-compensation.md",
    "docs/roadmap.md",
    "docs/release-notes-v0.1.1.md",
    ".github/workflows",
    ".github/workflows/python-syntax.yml",
    "examples/dry_run_tracking_config.yaml",
    "examples/local_video_tracking_demo.md",
    "examples/rtsp_tracking_demo.md",
    "scripts",
    "scripts/validate_project_structure.py",
    "scripts/import_smoke_check.py",
    "modules/latest_frame_rtsp.py",
    "modules/gimbal_controller.py",
    "modules/dkf_filter.py",
    "modules/visual_servo.py",
]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    missing = [path for path in REQUIRED_PATHS if not (root / path).exists()]

    if missing:
        print("Missing required project files:")
        for path in missing:
            print(f"  - {path}")
        return 1

    print("Project structure validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
