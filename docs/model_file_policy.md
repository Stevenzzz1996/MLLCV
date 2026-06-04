# Model File Policy

MLLCV should not store large model files directly in Git.

## Do Not Commit

Please do not commit files with extensions such as:

- `.pth`
- `.pt`
- `.onnx`
- `.engine`
- `.h5`
- `.ckpt`
- `.pb`
- `.tflite`
- `.weights`

## Why

Large model files make the repository harder to clone and maintain. Some model files may also come from third parties with unclear licenses.

## Recommended Practice

Use one of the following instead:

- Link to official model sources
- Provide download instructions
- Use GitHub Releases for small demo assets
- Use external storage for large files
- Provide checksums when possible

## Security Note

Only load model files from trusted sources. Model files may carry supply-chain or unsafe deserialization risks depending on the framework.
