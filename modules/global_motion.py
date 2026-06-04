from __future__ import annotations

import math

import cv2
import numpy as np


class GlobalMotionEstimator:
    def __init__(
        self,
        enable: bool = True,
        downscale: float = 0.5,
        max_corners: int = 500,
        min_points: int = 80,
        refresh_interval: int = 8,
        max_velocity_px_s: float = 1500.0,
        smoothing_alpha: float = 0.35,
        max_delta_px_s: float = 500.0,
        reset_decay: float = 0.2,
    ) -> None:
        self.enable = bool(enable)
        self.downscale = float(downscale)
        if self.downscale <= 0.0 or self.downscale > 1.0:
            self.downscale = 0.5
        self.max_corners = int(max_corners)
        self.min_points = int(min_points)
        self.refresh_interval = int(refresh_interval)
        self.max_velocity_px_s = float(max_velocity_px_s)
        self.smoothing_alpha = max(0.0, min(0.95, float(smoothing_alpha)))
        self.max_delta_px_s = max(0.0, float(max_delta_px_s))
        self.reset_decay = max(0.0, min(1.0, float(reset_decay)))
        self.prev_gray = None
        self.prev_pts = None
        self.prev_ts = None
        self.frame_count = 0
        self.last_velocity = (0.0, 0.0)

    def update(self, frame, timestamp: float) -> tuple[float, float]:
        if not self.enable:
            return 0.0, 0.0
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.downscale != 1.0:
            gray = cv2.resize(gray, None, fx=self.downscale, fy=self.downscale, interpolation=cv2.INTER_AREA)
        now = float(timestamp)
        if self.prev_gray is None or self.prev_pts is None or len(self.prev_pts) < self.min_points:
            self._reset(gray, now)
            return 0.0, 0.0

        dt = max(1e-3, now - float(self.prev_ts if self.prev_ts is not None else now))
        next_pts, status, _ = cv2.calcOpticalFlowPyrLK(
            self.prev_gray,
            gray,
            self.prev_pts,
            None,
            winSize=(21, 21),
            maxLevel=3,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 20, 0.03),
        )
        if next_pts is None or status is None:
            self._reset(gray, now)
            return self._decay_velocity()

        good = status.reshape(-1) > 0
        prev_good = self.prev_pts.reshape(-1, 2)[good]
        next_good = next_pts.reshape(-1, 2)[good]
        if len(prev_good) < max(12, self.min_points // 4):
            self._reset(gray, now)
            return self._decay_velocity()

        affine, inliers = cv2.estimateAffinePartial2D(
            prev_good,
            next_good,
            method=cv2.RANSAC,
            ransacReprojThreshold=3.0,
            maxIters=300,
            confidence=0.98,
        )
        if affine is None:
            self._reset(gray, now)
            return self._decay_velocity()

        dx = float(affine[0, 2]) / self.downscale
        dy = float(affine[1, 2]) / self.downscale
        vx = dx / dt
        vy = dy / dt
        norm = math.hypot(vx, vy)
        if norm > self.max_velocity_px_s > 0.0:
            scale = self.max_velocity_px_s / norm
            vx *= scale
            vy *= scale
        vx, vy = self._smooth_velocity(vx, vy)
        self.last_velocity = (vx, vy)

        self.frame_count += 1
        if (
            self.frame_count % max(1, self.refresh_interval) == 0
            or next_good.shape[0] < self.min_points
            or (inliers is not None and int(inliers.sum()) < self.min_points // 2)
        ):
            self._reset(gray, now)
        else:
            self.prev_gray = gray
            self.prev_pts = next_good.reshape(-1, 1, 2).astype(np.float32)
            self.prev_ts = now
        return self.last_velocity

    def _reset(self, gray, timestamp: float) -> None:
        self.prev_gray = gray
        self.prev_ts = float(timestamp)
        self.prev_pts = cv2.goodFeaturesToTrack(
            gray,
            maxCorners=self.max_corners,
            qualityLevel=0.01,
            minDistance=8,
            blockSize=7,
        )
        if self.prev_pts is None:
            self.prev_pts = np.empty((0, 1, 2), dtype=np.float32)

    def _smooth_velocity(self, vx: float, vy: float) -> tuple[float, float]:
        last_x, last_y = self.last_velocity
        dx = vx - last_x
        dy = vy - last_y
        delta_norm = math.hypot(dx, dy)
        if delta_norm > self.max_delta_px_s > 0.0:
            scale = self.max_delta_px_s / delta_norm
            vx = last_x + dx * scale
            vy = last_y + dy * scale
        alpha = self.smoothing_alpha
        return alpha * last_x + (1.0 - alpha) * vx, alpha * last_y + (1.0 - alpha) * vy

    def _decay_velocity(self) -> tuple[float, float]:
        last_x, last_y = self.last_velocity
        self.last_velocity = (last_x * self.reset_decay, last_y * self.reset_decay)
        return self.last_velocity
