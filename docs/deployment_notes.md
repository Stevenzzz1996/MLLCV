# Deployment Notes

This document collects deployment-oriented notes for computer vision models.

## Topics

Planned topics include:

- Model export
- ONNX conversion
- TensorRT deployment
- OpenCV inference
- Edge device deployment
- Runtime performance considerations
- Input preprocessing consistency
- Postprocessing consistency

## Deployment Checklist

Before deploying a CV model, check:

- Input size
- Color format, such as BGR or RGB
- Normalization mean and std
- Batch dimension
- Output tensor format
- Coordinate mapping
- Postprocessing logic
- Runtime dependency versions
- Hardware acceleration support
