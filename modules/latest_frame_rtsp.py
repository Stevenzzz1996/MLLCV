from __future__ import annotations

import os
import threading
import time
from typing import Optional

import cv2


class LatestFrameRTSP:
    def __init__(
        self,
        source: str,
        rtsp_transport: str = "udp",
        buffer_size: int = 1,
        reconnect_sec: float = 1.0,
    ) -> None:
        self.source = source
        self.rtsp_transport = rtsp_transport
        self.buffer_size = buffer_size
        self.reconnect_sec = reconnect_sec
        self._cap: Optional[cv2.VideoCapture] = None
        self._lock = threading.Lock()
        self._frame = None
        self._frame_ts = 0.0
        self._ok = False
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="LatestFrameRTSP", daemon=True)
        self._thread.start()

    def _open(self) -> cv2.VideoCapture:
        os.environ.setdefault(
            "OPENCV_FFMPEG_CAPTURE_OPTIONS",
            f"rtsp_transport;{self.rtsp_transport}|fflags;nobuffer|flags;low_delay|framedrop;1",
        )
        if isinstance(self.source, int):
            cap = cv2.VideoCapture(self.source)
        else:
            cap = cv2.VideoCapture(self.source, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, self.buffer_size)
        return cap

    def _loop(self) -> None:
        while not self._stop.is_set():
            self._cap = self._open()
            if not self._cap.isOpened():
                time.sleep(self.reconnect_sec)
                continue
            while not self._stop.is_set():
                ok, frame = self._cap.read()
                now = time.time()
                if not ok or frame is None:
                    with self._lock:
                        self._ok = False
                    break
                with self._lock:
                    self._ok = True
                    self._frame = frame
                    self._frame_ts = now
            self._cap.release()
            time.sleep(self.reconnect_sec)

    def read_latest(self):
        with self._lock:
            if not self._ok or self._frame is None:
                return False, None, 0.0
            return True, self._frame.copy(), self._frame_ts

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1.0)
        if self._cap is not None:
            self._cap.release()
