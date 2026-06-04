from __future__ import annotations

import argparse
from pathlib import Path


VISDRONE_YOLOV8S_P2_960_FOLDER_ID = "1fYgmNKjObD1GCigl68geznu6rKxr7X-k"


def main() -> int:
    parser = argparse.ArgumentParser("Download VisDrone YOLOv8s-P2 960 weights")
    parser.add_argument("--output", default="models/visdrone", help="Output directory")
    parser.add_argument("--skip-existing", action="store_true", help="Skip when best.pt and best.onnx already exist")
    args = parser.parse_args()

    out_dir = Path(args.output)
    best_pt = out_dir / "weights" / "best.pt"
    best_onnx = out_dir / "weights" / "best.onnx"
    if args.skip_existing and best_pt.exists() and best_onnx.exists():
        print(f"weights already exist: {best_pt} {best_onnx}")
        return 0

    try:
        import gdown
    except ImportError as exc:
        raise SystemExit("gdown is required: python -m pip install gdown") from exc

    out_dir.mkdir(parents=True, exist_ok=True)
    paths = gdown.download_folder(
        id=VISDRONE_YOLOV8S_P2_960_FOLDER_ID,
        output=str(out_dir),
        quiet=False,
        use_cookies=False,
    )
    print("downloaded:")
    for path in paths or []:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
