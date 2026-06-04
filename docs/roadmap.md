# Roadmap

MLLCV is an early-stage prototype. The roadmap focuses on making the project easier to run, review, and extend safely.

## Near Term

- Improve portable example configurations.
- Add more pure-Python validation checks that do not need hardware.
- Add small synthetic tests for DKF update and prediction behavior.
- Document detector and tracker backend requirements.
- Make local-video demos easier to run without private assets.

## Hardware and Safety

- Add a gimbal sign-calibration checklist.
- Add safer first-run command limits.
- Document emergency stop expectations.
- Improve logging around real UDP command sends.

## Tracking and Prediction

- Add clearer detector reacquisition examples.
- Add DKF tuning notes based on recorded public examples.
- Separate tracker wrappers from experiment scripts where useful.
- Add metrics scripts that can run on public or synthetic sequences.

## Release and Maintenance

- Keep large models, TensorRT engines, and recordings out of Git.
- Publish model download instructions separately when licenses permit.
- Add release notes for each public prototype tag.
- Keep vendored third-party code changes minimal and documented.
