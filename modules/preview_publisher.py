from __future__ import annotations

import os
import time
from pathlib import Path

import cv2


class PreviewPublisher:
    def __init__(
        self,
        path: str = "/tmp/source_track_preview.jpg",
        enable: bool = False,
        fps: float = 15.0,
        quality: int = 80,
    ) -> None:
        self.path = Path(path)
        self.enable = bool(enable)
        self.interval = 1.0 / max(1.0, float(fps))
        self.quality = int(max(30, min(95, quality)))
        self._last_ts = 0.0
        self._tmp_path = self.path.with_name(f".{self.path.name}.tmp")
        if self.enable:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def publish(self, frame, now: float | None = None) -> None:
        if not self.enable or frame is None:
            return
        now = time.time() if now is None else now
        if now - self._last_ts < self.interval:
            return
        ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), self.quality])
        if not ok:
            return
        with open(self._tmp_path, "wb") as f:
            f.write(encoded.tobytes())
        os.replace(self._tmp_path, self.path)
        self._last_ts = now
