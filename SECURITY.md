# Security Policy

MLLCV combines network video input, model loading, UDP hardware control, and physical gimbal movement. Security and safety reports are welcome.

## Reporting Security Issues

Please open a GitHub issue with a clear description, or contact the maintainer privately if public disclosure would create risk. Do not include real credentials, private RTSP URLs, private recordings, or API keys in public reports.

## Areas of Concern

This project is especially interested in reports about:

- Unsafe UDP command behavior
- Exposed Siyi A8 Mini control interfaces
- RTSP stream handling from untrusted networks
- Unsafe file or model loading
- Accidental secret exposure in configs or logs
- Unsafe defaults that could move hardware unexpectedly
- Dependency vulnerabilities

## UDP and Hardware Safety

The A8 Mini UDP controller can move physical hardware. Keep control networks private, avoid exposing UDP ports to untrusted users, and validate all sign conventions and speed limits before running with `--real-gimbal`.

Dry-run mode should remain the default for examples and first-run documentation.

## RTSP and Network Inputs

Treat RTSP streams as untrusted network inputs unless they come from a controlled device. Avoid publishing real stream URLs. Use TCP or UDP transport based on your network, but do not assume that a stream is safe merely because it is local.

## Model Files

Do not commit private or large model files. Only load model weights or TensorRT engines from trusted sources. Model files may carry supply-chain risk depending on the framework and serialization format.
