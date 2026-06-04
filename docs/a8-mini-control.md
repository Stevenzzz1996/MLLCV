# Siyi A8 Mini Control Notes

MLLCV includes a small UDP controller for Siyi A8 Mini gimbal commands in `modules/gimbal_controller.py`.

## What the Code Sends

The controller builds packets with:

- Header bytes `0x55 0x66`
- Control byte
- Payload length
- Sequence number
- Command ID
- Payload
- CRC16-CCITT checksum

The current wrapper exposes:

- `set_speed(yaw_speed, pitch_speed)`
- `set_angle(yaw_deg, pitch_deg)`
- `center()`
- `zoom_in()`, `zoom_out()`, `zoom_stop()`
- `set_zoom(multiple)`
- `stop()`

## Default Safety Posture

The example configuration keeps `runtime.dry_run_gimbal: true`. In dry-run mode the program constructs commands but does not send UDP packets to the hardware.

Use `--real-gimbal` only after you have verified:

- The configured IP belongs to the intended gimbal.
- The UDP port is correct.
- The mount has safe physical clearance.
- Positive yaw and pitch directions are understood.
- `Space`, process termination, and `stop()` behavior have been validated.

## Configuration Fields

```yaml
gimbal:
  ip: "192.168.144.25"
  port: 37260
  yaw_sign: 1
  pitch_sign: -1
  need_ack: false
```

`yaw_sign` and `pitch_sign` are hardware-orientation dependent. Start with low speed limits and dry-run logs before sending real commands.

## Hardware Safety

Physical gimbal movement can damage hardware or injure people if the control signs or limits are wrong. Keep conservative speed limits during setup, avoid testing near obstacles, and keep a manual stop path available.

Do not expose A8 Mini UDP control on an untrusted network.
