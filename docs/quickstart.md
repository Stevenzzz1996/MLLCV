# Quick Start

This guide explains how to start using MLLCV.

## 1. Clone the Repository

```bash
git clone https://github.com/Stevenzzz1996/MLLCV.git
cd MLLCV
```

## 2. Create a Python Environment

```bash
python -m venv .venv
source .venv/bin/activate
```

For Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## 3. Install Basic Dependencies

```bash
pip install -r requirements.txt
```

## 4. Choose a Submodule

MLLCV contains multiple computer vision learning modules. Different modules may require different dependency versions.

Recommended starting points:

- YOLO / object detection examples
- Face recognition examples
- Semantic segmentation examples
- ResNet / classification examples
- Model compression and deployment notes

## 5. Important Notes

This repository contains legacy educational examples. Some scripts may require older versions of TensorFlow, Keras, or OpenCV.

Before running a script, check:

- Python version
- Required dependencies
- Dataset path
- Model file path
- Input image or video path

## 6. Do Not Commit Large Files

Please do not commit:

- Model weights
- Datasets
- Generated outputs
- API keys
- Private credentials
