from __future__ import annotations

from pathlib import Path
from typing import Sequence

from .common import Detection


class YOLO26Detector:
    def __init__(
        self,
        model_path: str,
        backend: str = "ultralytics",
        imgsz: int | Sequence[int] = 640,
        conf: float = 0.35,
        classes: list[int] | None = None,
        enable: bool = True,
    ) -> None:
        self.enable = enable
        self.backend = backend
        self.model_path = model_path
        self.imgsz = imgsz
        self.conf = conf
        self.classes = classes
        self.model = None
        if self.enable and self.backend in {"ultralytics", "tensorrt", "engine"}:
            try:
                from ultralytics import YOLO
            except ImportError:
                print("WARN: ultralytics is not installed; YOLO detection is disabled.")
                return

            if not Path(model_path).exists() and not model_path.startswith(("yolo", "YOLO")):
                print(f"WARN: YOLO model not found: {model_path}; detection is disabled.")
                return
            try:
                self.model = YOLO(model_path, task="detect")
            except Exception as exc:
                print(f"WARN: failed to load YOLO model {model_path}: {exc}; detection is disabled.")
                self.model = None
        elif self.enable:
            print(f"WARN: unsupported YOLO backend {backend}; detection is disabled.")

    def detect(self, frame) -> list[Detection]:
        if not self.enable or self.model is None:
            return []
        results = self.model.predict(
            frame,
            imgsz=self.imgsz,
            conf=self.conf,
            classes=self.classes,
            verbose=False,
        )
        detections: list[Detection] = []
        names = getattr(self.model, "names", {})
        for r in results:
            if r.boxes is None:
                continue
            for box in r.boxes:
                cls_id = int(box.cls[0])
                x1, y1, x2, y2 = [float(v) for v in box.xyxy[0]]
                detections.append(
                    Detection(
                        cls_id=cls_id,
                        cls_name=str(names.get(cls_id, cls_id)),
                        conf=float(box.conf[0]),
                        bbox_xyxy=(x1, y1, x2, y2),
                    )
                )
        return detections
