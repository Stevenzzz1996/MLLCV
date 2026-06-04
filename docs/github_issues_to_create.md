# Suggested GitHub Issues

## 1. [Roadmap] Add VLA data recording pipeline

Track the implementation of observation-action episode recording for MLLCV.

Tasks:

- add VLA schema
- add JSONL writer
- add mock recording demo
- add dataset validation
- document the recording format

## 2. [Security] Review RTSP, model loading, and gimbal command risks

Track security risks related to video input, model files, file paths, and UDP gimbal control.

Tasks:

- check unsafe file loading
- check model loading risks
- avoid committing credentials
- add dry-run defaults
- document safety limits

## 3. [Docs] Add VLA and LeRobot integration documentation

Track documentation for the VLA roadmap and LeRobot-compatible conversion plan.

Tasks:

- add `docs/vla_roadmap.md`
- add `docs/lerobot_integration.md`
- add `docs/vla_dataset_format.md`
- update README

## 4. [Testing] Add smoke test for VLA mock recording

Track test coverage for the mock VLA recorder.

Tasks:

- run `examples/vla_record_demo.py` in CI
- validate generated JSONL
- check schema fields

## 5. [Example] Add sanitized demo episode

Track a future public demo episode that does not contain sensitive footage.

Tasks:

- create synthetic or public-safe frames
- record mock actions
- validate dataset format
- document usage
