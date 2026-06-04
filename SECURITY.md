# Security Policy

MLLCV is an educational computer vision repository. It may include examples involving model files, image/video inputs, third-party dependencies, and data preprocessing scripts.

## Supported Versions

The current public version is maintained on the `main` branch. Security-related improvements will be applied to the latest version of the repository.

## Security Areas

This project is especially interested in reviewing:

- Unsafe file loading patterns
- Model loading risks
- Dependency vulnerabilities
- Accidental secret exposure
- Insecure path handling
- Unsafe use of external files or datasets
- Unsafe deserialization
- Code quality issues that may affect reproducibility or safety

## Model and Dataset Safety

Please do not upload large model files, private datasets, credentials, API keys, or sensitive personal data to this repository.

When using external model files or datasets, verify their source and integrity before running scripts.

## Reporting a Vulnerability

If you find a security issue, please open a GitHub issue with a clear description.

Please do not include sensitive data, private credentials, or real API keys in issues or pull requests.
