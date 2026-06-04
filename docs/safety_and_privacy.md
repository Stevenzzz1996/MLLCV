# Safety and Privacy

MLLCV may interact with video streams, camera frames, model files, and gimbal control commands. Safety and privacy must be considered before any real deployment or data publication.

## Do Not Commit

- RTSP URLs with credentials
- device IP addresses from private networks
- API keys
- private model weights
- real surveillance footage
- private faces
- license plates
- company interiors
- raw human telemetry
- private calibration files

## Gimbal Control Safety

Before sending commands to real hardware:

- test in dry-run mode
- clamp yaw and pitch speed
- clamp acceleration
- validate frame timestamp freshness
- stop if tracking confidence is low
- stop if Kalman uncertainty is high
- keep a manual emergency stop path

## Dataset Safety

Before publishing a dataset:

- blur faces and license plates
- remove audio unless required
- remove metadata that reveals location
- avoid scenes containing sensitive equipment
- use short sanitized clips
- document dataset limitations

## Security Review Areas

- unsafe file loading
- model loading risks
- path traversal
- dependency vulnerabilities
- untrusted video inputs
- uncontrolled UDP command output
- accidental secret exposure
