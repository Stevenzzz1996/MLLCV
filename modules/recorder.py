from __future__ import annotations

import json
import math
import queue
import threading
import time
from pathlib import Path
from typing import Any

import cv2


class DataRecorder:
    def __init__(
        self,
        root: str = "recordings",
        enable: bool = False,
        save_video: bool = True,
        save_frames: bool = False,
        save_jsonl: bool = True,
        fps: float = 25.0,
        queue_size: int = 120,
        dataset: str = "smolvla_scan",
        auto_start: bool = True,
    ) -> None:
        self.root = Path(root)
        self.enable = enable
        self.save_video = save_video
        self.save_frames = save_frames
        self.save_jsonl = save_jsonl
        self.fps = fps
        self.dataset = dataset
        self.auto_start = auto_start
        self.episode_dir: Path | None = None
        self.data_file = None
        self.video = None
        self.frames_dir: Path | None = None
        self.frame_count = 0
        self._queue: queue.Queue | None = queue.Queue(maxsize=max(1, queue_size)) if enable else None
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._write_lock = threading.Lock()

    def start(self, frame_shape=None, metadata: dict[str, Any] | None = None) -> None:
        if not self.enable or self.episode_dir is not None:
            return
        self.root.mkdir(parents=True, exist_ok=True)
        self.episode_dir = self.root / time.strftime("episode_%Y%m%d_%H%M%S")
        self.episode_dir.mkdir(parents=True, exist_ok=True)
        self.frame_count = 0
        if self.save_jsonl:
            self.data_file = open(self.episode_dir / "data.jsonl", "a", encoding="utf-8")
        if self.save_frames:
            self.frames_dir = self.episode_dir / "frames"
            self.frames_dir.mkdir(parents=True, exist_ok=True)
        if self.save_video and frame_shape is not None:
            h, w = frame_shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            self.video = cv2.VideoWriter(str(self.episode_dir / "video.mp4"), fourcc, self.fps, (w, h))
        meta = {
            "dataset": self.dataset,
            "schema": "smolvla_scan_v2",
            "created_time": time.time(),
            "fps": self.fps,
            "save_video": self.save_video,
            "save_frames": self.save_frames,
            **(metadata or {}),
        }
        (self.episode_dir / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._writer_loop, name="DataRecorder", daemon=True)
            self._thread.start()

    def stop_episode(self) -> None:
        if not self.enable or self.episode_dir is None:
            return
        self._drain()
        with self._write_lock:
            if self.data_file:
                self.data_file.close()
                self.data_file = None
            if self.video:
                self.video.release()
                self.video = None
        self.episode_dir = None
        self.frames_dir = None

    def record_step(self, row: dict, frame=None) -> None:
        if not self.enable:
            return
        if self.episode_dir is None:
            if not self.auto_start:
                return
            self.start(frame.shape if frame is not None else None)
        if self._queue is None:
            return
        should_copy_frame = frame is not None and (self.video is not None or self.frames_dir is not None)
        item = (row, frame.copy() if should_copy_frame else None)
        try:
            self._queue.put_nowait(item)
        except queue.Full:
            try:
                self._queue.get_nowait()
            except queue.Empty:
                pass
            try:
                self._queue.put_nowait(item)
            except queue.Full:
                pass

    def _writer_loop(self) -> None:
        while not self._stop.is_set() or (self._queue is not None and not self._queue.empty()):
            try:
                row, frame = self._queue.get(timeout=0.1) if self._queue is not None else (None, None)
            except queue.Empty:
                continue
            self._write(row, frame)

    def _write(self, row: dict, frame=None) -> None:
        if row is None:
            return
        with self._write_lock:
            frame_path = None
            if self.frames_dir is not None and frame is not None:
                frame_path = self.frames_dir / f"{self.frame_count:06d}.jpg"
                cv2.imwrite(str(frame_path), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
                row.setdefault("observation", {})
                row["observation"]["image"] = str(frame_path.relative_to(self.episode_dir)) if self.episode_dir else str(frame_path)
            self.frame_count += 1
            if self.data_file:
                self.data_file.write(json.dumps(sanitize_json(row), ensure_ascii=False) + "\n")
                self.data_file.flush()
            if self.video is not None and frame is not None:
                self.video.write(frame)

    def _drain(self) -> None:
        if self._queue is None:
            return
        while True:
            try:
                row, frame = self._queue.get_nowait()
            except queue.Empty:
                break
            self._write(row, frame)

    def close(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        self.stop_episode()


def sanitize_json(value):
    if isinstance(value, dict):
        return {str(k): sanitize_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [sanitize_json(v) for v in value]
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    return value
