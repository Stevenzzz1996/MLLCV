# Data Recording

MLLCV records data as episode-based observation-action trajectories.

## Why Episode Data?

Robotic perception and VLA training require synchronized time-series data, not just independent images. Each step should include what the system sees, what it believes, and what action is taken.

## Recommended Fields

Each step should include:

- timestamp
- episode ID
- frame ID
- language instruction
- RGB frame path
- IR frame path, if available
- detection bbox
- tracking score
- target center
- Kalman prediction state
- gimbal yaw/pitch/zoom telemetry
- expert action: yaw rate, pitch rate, zoom command, stop, mode
- latency in milliseconds

## Expert Sources

The expert action may come from:

1. Visual servo controller
2. Human teleoperation
3. Hybrid controller
4. Replay from a validated trajectory

## Storage Recommendation

Do not commit real recordings to Git. Use:

- local `data/` directory during development
- Git LFS for small public demo assets
- Hugging Face Dataset for public sanitized datasets
- private storage for sensitive real-world recordings

## Privacy Warning

Do not publish private faces, license plates, company interiors, device credentials, RTSP URLs, or sensitive scenes.
