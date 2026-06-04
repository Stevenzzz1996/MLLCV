from __future__ import annotations

from pathlib import Path


REQUIRED_PATHS = [
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "CHANGELOG.md",
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
    "docs/release-notes-v0.1.0.md",
    "docs/codex-application-statement.md",
    "docs/vla_roadmap.md",
    "docs/data_recording.md",
    "docs/vla_dataset_format.md",
    "docs/lerobot_integration.md",
    "docs/safety_and_privacy.md",
    "docs/github_issues_to_create.md",
    "docs/release_v0.2.0_draft.md",
    ".github/workflows",
    ".github/workflows/python-syntax.yml",
    "examples/dry_run_tracking_config.yaml",
    "examples/local_video_tracking_demo.md",
    "examples/rtsp_tracking_demo.md",
    "examples/vla_record_demo.py",
    "data/.gitkeep",
    "mllcv/vla/README.md",
    "mllcv/vla/schema.py",
    "mllcv/vla/recorder.py",
    "mllcv/vla/writer.py",
    "mllcv/vla/convert_to_lerobot.py",
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
