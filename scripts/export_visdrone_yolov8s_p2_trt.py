from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser("Export VisDrone YOLOv8s-P2 960 to TensorRT")
    parser.add_argument("--weights", default="models/visdrone/weights/best.pt")
    parser.add_argument("--imgsz", nargs="+", type=int, default=[960])
    parser.add_argument("--device", default=0)
    parser.add_argument("--half", action="store_true")
    parser.add_argument("--workspace", type=float, default=4.0)
    args = parser.parse_args()

    weights = Path(args.weights)
    if not weights.exists():
        raise SystemExit(f"weights not found: {weights}")

    from ultralytics import YOLO

    model = YOLO(str(weights), task="detect")
    exported = model.export(
        format="engine",
        imgsz=args.imgsz[0] if len(args.imgsz) == 1 else args.imgsz,
        device=args.device,
        half=bool(args.half),
        workspace=args.workspace,
    )
    print(exported)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
