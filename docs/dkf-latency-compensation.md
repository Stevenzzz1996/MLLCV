# Delayed Kalman Filter Latency Compensation

The delayed Kalman filter in `modules/dkf_filter.py` estimates target box position, size, and velocity while accounting for measurement delay and optional camera-motion compensation.

## Why Latency Compensation Exists

In a live tracking system, the tracker measurement often describes where the target was when the frame was captured, not where it is when the gimbal command is sent. This delay can cause overshoot, sluggish correction, or loss of lock.

The DKF is intended to help by:

- Tracking target center, size, and velocity.
- Blending tracker and detector measurements with separate noise settings.
- Compensating delayed measurements within configured bounds.
- Predicting a future target location for visual-servo control.

## Important Configuration

```yaml
dkf:
  latency_ms: 200
  pipeline_latency_ms: 20
  delayed_measurement_compensation: true
  max_measurement_delay: 0.45
  process_noise: 5000.0
  measurement_noise: 25.0
  gate_mahalanobis: 25.0
```

Tune these values on the actual camera, detector, tracker, and compute platform. The checked-in values are project defaults, not universal benchmarks.

## Measurement Sources

The filter can ingest:

- Tracker measurements for frequent target updates.
- Detector measurements for correction or reacquisition.
- Optional camera-motion estimates to reduce apparent target motion caused by gimbal movement.

## Practical Tuning Notes

- Increase measurement noise if tracker boxes are jittery.
- Increase process noise if the target moves quickly and prediction lags.
- Keep `max_measurement_delay` bounded to avoid large stale corrections.
- Watch for rejected updates through gate settings if the filter refuses valid measurements.
- Validate on logs or recorded sequences before commanding hardware.
