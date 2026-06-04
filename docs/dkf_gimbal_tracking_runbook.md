# DKF Gimbal Tracking Runbook

## Current status

This prototype runs the real A8 Mini gimbal tracking loop with:

- RTSP latest-frame capture from `rtsp://192.168.144.25:8554/main.264`
- YOLO26 TensorRT detection from `yolo26m.engine`
- AsymTrack TensorRT tracking from `models/asymtrack/asymtrack_tiny_fp32.engine`
- DKF delay compensation for the known control/video delay
- UDP velocity control to the A8 Mini gimbal
- Local JPEG preview at `/tmp/source_track_preview.jpg`

The current control path is:

`RTSP frame -> YOLO correction -> AsymTrack continuous tracking -> DKF prediction -> visual servo -> A8 UDP speed command`

The preview window does not open RTSP directly. It reads `/tmp/source_track_preview.jpg`, because the camera stream may reject a second RTSP client with `404`.

## Conda environments

Use two environments:

- `smolvla-deploy`: TensorRT tracking/control runtime.
- `calib`: OpenCV GUI preview runtime.

## Start tracking

From `/home/mll/CPP_PROJ/source_track`:

```bash
conda run --no-capture-output -n smolvla-deploy \
  python main_low_latency_track.py \
  --config config_low_latency.yaml \
  --real-gimbal \
  --no-gui \
  --auto-track \
  --preview-jpeg /tmp/source_track_preview.jpg
```

Recommended background start:

```bash
LOG="runs/real_trt_dkf_$(date +%Y%m%d_%H%M%S).log"
echo "$LOG" > /tmp/source_track_trt_log.txt
setsid -f bash -lc "cd /home/mll/CPP_PROJ/source_track && \
  conda run --no-capture-output -n smolvla-deploy \
  python main_low_latency_track.py \
  --config config_low_latency.yaml \
  --real-gimbal \
  --no-gui \
  --auto-track \
  --preview-jpeg /tmp/source_track_preview.jpg \
  > '$LOG' 2>&1"
```

## Start preview window

```bash
conda run --no-capture-output -n calib \
  python scripts/show_preview_jpeg.py \
  --path /tmp/source_track_preview.jpg
```

The preview process can stay open while the tracking process restarts.

## Stop safely

Stop the tracking process:

```bash
pgrep -af '[m]ain_low_latency_track.py'
kill <pid1> <pid2> <pid3>
```

Send a gimbal stop command:

```bash
conda run --no-capture-output -n smolvla-deploy python - <<'PY'
from modules.gimbal_controller import A8MiniGimbal
g = A8MiniGimbal(ip='192.168.144.25', port=37260, yaw_sign=1, pitch_sign=-1, dry_run=False, need_ack=False)
g.stop()
g.close()
print('gimbal stop sent')
PY
```

## Key parameters

File: `config_low_latency.yaml`

- `dkf.latency_ms: 200`: known system delay.
- `dkf.pipeline_latency_ms: 20`: local processing/control pipeline estimate.
- `dkf.add_frame_age: true`: add measured frame age to prediction time.
- `dkf.min_ahead_time: 0.18`, `dkf.max_ahead_time: 0.26`: clamps DKF look-ahead.
- `dkf.catchup_extra_ms`: adds extra look-ahead during the catch-up phase when the target is already delayed from center.
- `dkf.catchup_error`, `dkf.settle_error`: switch between fast catch-up and steady tracking.
- `dkf.catchup_gain`: temporary gain boost during catch-up, then fades out near center.
- `dkf.tracker_velocity_blend: 0.70`: fast velocity injection from AsymTrack frame-to-frame displacement.
- `dkf.velocity_deadband_px_s: 18`: suppresses static jitter velocity.
- `servo.hold_deadzone_x/y`: hold zone for static targets.
- `servo.stationary_vel_norm`: normalized speed threshold used to decide static target behavior.
- `servo.min_yaw_speed`, `servo.min_pitch_speed`: minimum effective gimbal command outside the hold zone.
- `control.strict_detector_gate: false`: detector corrects drift but does not frequently break tracking.

## What has been fixed

- TensorRT inference is used for both YOLO and AsymTrack in the real tracking path.
- Control goes directly from tracker/DKF to gimbal speed commands.
- A separate preview window no longer opens a second RTSP connection.
- DKF now predicts using the known delay, typically around `220-240ms` in the latest run.
- Static target oscillation is reduced with a hold zone and velocity deadband.
- DKF velocity response is faster because consecutive bbox displacement is fused into the velocity state.

## Current limitations

- Multi-person scenes can still confuse automatic target selection if a new person is closer to the predicted box.
- The true gimbal mechanical response delay is not measured by an encoder; it is currently configured as `200ms`.
- Fast target motion still needs live tuning of `tracker_velocity_blend`, `kd_yaw`, `max_ff_yaw_speed`, and `min_yaw_speed`.
- If static jitter returns, first increase `hold_deadzone_x/y` or `velocity_deadband_px_s`, not the visual deadzone.

## Quick log checks

Current log:

```bash
tail -n 80 "$(cat /tmp/source_track_trt_log.txt)"
```

Important fields:

- `age_ms`: measured frame age.
- `ahead_ms`: DKF prediction time after delay compensation.
- `catch`: catch-up phase score. `0` means steady tracking/hold; near `1` means fast catch-up.
- `ex`, `ey`: normalized target center error. Lower is better.
- `yaw`, `pitch`: gimbal velocity command.
- `dkf_unc`: DKF uncertainty.
- `lost_frames`: short prediction count after tracker loss.
