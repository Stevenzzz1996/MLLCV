from __future__ import annotations

import math

import numpy as np

from .common import clamp


def valid_bbox(bbox_xyxy) -> bool:
    if bbox_xyxy is None or len(bbox_xyxy) != 4:
        return False
    try:
        x1, y1, x2, y2 = map(float, bbox_xyxy)
    except Exception:
        return False
    return all(math.isfinite(v) for v in (x1, y1, x2, y2)) and x2 > x1 and y2 > y1


def xyxy_to_cxcywh(bbox_xyxy):
    if not valid_bbox(bbox_xyxy):
        return None
    x1, y1, x2, y2 = map(float, bbox_xyxy)
    w = x2 - x1
    h = y2 - y1
    return np.array([x1 + 0.5 * w, y1 + 0.5 * h, w, h], dtype=np.float64)


def cxcywh_to_xyxy(cxcywh):
    cx, cy, w, h = map(float, cxcywh)
    if not all(math.isfinite(v) for v in (cx, cy, w, h)) or w <= 1.0 or h <= 1.0:
        return None
    return (cx - 0.5 * w, cy - 0.5 * h, cx + 0.5 * w, cy + 0.5 * h)


class DKFFilter:
    def __init__(self, cfg: dict | None = None) -> None:
        cfg = cfg or {}
        self.default_dt = float(cfg.get("default_dt", 1.0 / 30.0))
        self.max_dt = float(cfg.get("max_dt", 0.2))
        self.init_pos_var = float(cfg.get("init_pos_var", 25.0))
        self.init_size_var = float(cfg.get("init_size_var", 25.0))
        self.init_vel_var = float(cfg.get("init_vel_var", 100.0))
        self.init_size_vel_var = float(cfg.get("init_size_vel_var", 25.0))
        self.q_pos = float(cfg.get("q_pos", cfg.get("process_noise", 5000.0) * 0.02))
        self.q_size = float(cfg.get("q_size", 10.0))
        self.q_vel = float(cfg.get("q_vel", cfg.get("process_noise", 5000.0)))
        self.q_size_vel = float(cfg.get("q_size_vel", 50.0))
        self.r_tracker_pos = float(cfg.get("r_tracker_pos", cfg.get("measurement_noise", 25.0)))
        self.r_tracker_size = float(cfg.get("r_tracker_size", cfg.get("measurement_noise", 25.0) * 2.0))
        self.r_detector_pos = float(cfg.get("r_detector_pos", cfg.get("measurement_noise", 25.0)))
        self.r_detector_size = float(cfg.get("r_detector_size", cfg.get("measurement_noise", 25.0) * 2.0))
        self.tracker_r_scale = float(cfg.get("tracker_r_scale", 4.0))
        self.detector_r_scale = float(cfg.get("detector_r_scale", 2.0))
        self.tracker_velocity_blend = float(cfg.get("tracker_velocity_blend", 0.65))
        self.detector_velocity_blend = float(cfg.get("detector_velocity_blend", 0.35))
        self.size_velocity_blend = float(cfg.get("size_velocity_blend", 0.15))
        self.velocity_deadband_px_s = float(cfg.get("velocity_deadband_px_s", 25.0))
        self.stationary_speed_px_s = float(cfg.get("stationary_speed_px_s", self.velocity_deadband_px_s))
        self.stationary_frames = int(cfg.get("stationary_frames", 4))
        self.stationary_velocity_decay = float(cfg.get("stationary_velocity_decay", 0.25))
        self.motion_enter_frames = int(cfg.get("motion_enter_frames", 3))
        self.max_velocity_px_s = float(cfg.get("max_velocity_px_s", 2500.0))
        self.delayed_measurement_compensation = bool(cfg.get("delayed_measurement_compensation", True))
        self.max_measurement_delay = float(cfg.get("max_measurement_delay", 0.45))
        self.max_delayed_shift_px = float(cfg.get("max_delayed_shift_px", 220.0))
        self.camera_motion_compensation = bool(cfg.get("camera_motion_compensation", False))
        self.camera_state_compensation = bool(cfg.get("camera_state_compensation", True))
        self.camera_delay_compensation = bool(cfg.get("camera_delay_compensation", False))
        self.camera_future_compensation = bool(cfg.get("camera_future_compensation", False))
        self.camera_motion_units = str(cfg.get("camera_motion_units", "command")).lower()
        self.yaw_px_per_cmd = float(cfg.get("yaw_px_per_cmd", 0.0))
        self.pitch_px_per_cmd = float(cfg.get("pitch_px_per_cmd", 0.0))
        self.max_camera_shift_px = float(cfg.get("max_camera_shift_px", 220.0))
        self.gate_mahalanobis = float(cfg.get("gate_mahalanobis", 25.0))
        self.min_size = float(cfg.get("min_size", 2.0))
        self.reset()

    def reset(self) -> None:
        self.x = np.zeros((8, 1), dtype=np.float64)
        self.P = np.eye(8, dtype=np.float64)
        self.initialized = False
        self.lost_frames = 0
        self.last_update_accepted = True
        self.last_reject_reason = ""
        self.last_z = None
        self.stationary_count = 0
        self.motion_count = 0

    def is_initialized(self) -> bool:
        return self.initialized

    def init_from_bbox(self, bbox_xyxy) -> bool:
        z = xyxy_to_cxcywh(bbox_xyxy)
        if z is None:
            self.reset()
            return False
        self.x = np.zeros((8, 1), dtype=np.float64)
        self.x[0:4, 0] = z
        self.P = np.diag(
            [
                self.init_pos_var,
                self.init_pos_var,
                self.init_size_var,
                self.init_size_var,
                self.init_vel_var,
                self.init_vel_var,
                self.init_size_vel_var,
                self.init_size_vel_var,
            ]
        ).astype(np.float64)
        self.initialized = True
        self.lost_frames = 0
        self.last_update_accepted = True
        self.last_reject_reason = ""
        self.last_z = z.copy()
        self.stationary_count = max(1, self.stationary_frames)
        self.motion_count = 0
        return True

    def predict(self, dt: float, camera_motion: tuple[float, float] = (0.0, 0.0)) -> None:
        if not self.initialized:
            return
        dt = float(dt)
        if dt <= 0.0 or not math.isfinite(dt):
            dt = self.default_dt
        dt = min(dt, self.max_dt)
        F = self._make_F(dt)
        Q = self._make_Q(dt)
        self.x = F @ self.x
        if self.camera_state_compensation:
            self.x[0:2, 0] += self._camera_shift(camera_motion, dt)
        self.P = F @ self.P @ F.T + Q
        self._sanitize_state()

    def update_tracker(
        self,
        bbox_xyxy,
        score: float = 1.0,
        dt: float | None = None,
        measurement_delay_sec: float = 0.0,
        camera_motion: tuple[float, float] = (0.0, 0.0),
    ) -> bool:
        if not self.initialized:
            return self.init_from_bbox(bbox_xyxy)
        z = xyxy_to_cxcywh(bbox_xyxy)
        if z is None:
            return False
        z_update = self._compensate_delayed_measurement(z, measurement_delay_sec, camera_motion)
        score = clamp(float(score), 0.0, 1.0)
        scale = 1.0 + (1.0 - score) * self.tracker_r_scale
        R = np.diag([self.r_tracker_pos * scale, self.r_tracker_pos * scale, self.r_tracker_size * scale, self.r_tracker_size * scale])
        ok = self._update(z_update, R)
        if ok:
            self._blend_measured_velocity(z, dt, self.tracker_velocity_blend, camera_motion)
            self.lost_frames = 0
        return ok

    def reanchor_from_bbox(self, bbox_xyxy, dt: float | None = None, camera_motion: tuple[float, float] = (0.0, 0.0)) -> bool:
        z = xyxy_to_cxcywh(bbox_xyxy)
        if z is None:
            return False
        if not self.initialized:
            return self.init_from_bbox(bbox_xyxy)
        dt = self.default_dt if dt is None else float(dt)
        if dt <= 0.0 or not math.isfinite(dt):
            dt = self.default_dt
        dt = min(dt, self.max_dt)
        old = self.x[0:4, 0].copy()
        measured_v = (z - old) / max(1e-3, dt)
        measured_v[0:2] -= self._camera_velocity(camera_motion)
        self.x[0:4, 0] = z
        self.x[4:8, 0] = 0.5 * self.x[4:8, 0] + 0.5 * measured_v
        self.last_z = z.copy()
        self.P[0:4, 0:4] = np.diag([self.init_pos_var, self.init_pos_var, self.init_size_var, self.init_size_var])
        self.P[4:8, 4:8] = np.diag([self.init_vel_var, self.init_vel_var, self.init_size_vel_var, self.init_size_vel_var])
        self.lost_frames = 0
        self.last_update_accepted = True
        self.last_reject_reason = "reanchored"
        self._sanitize_state()
        return True

    def update_detector(
        self,
        bbox_xyxy,
        conf: float = 1.0,
        dt: float | None = None,
        measurement_delay_sec: float = 0.0,
        camera_motion: tuple[float, float] = (0.0, 0.0),
    ) -> bool:
        if not self.initialized:
            return self.init_from_bbox(bbox_xyxy)
        z = xyxy_to_cxcywh(bbox_xyxy)
        if z is None:
            return False
        z_update = self._compensate_delayed_measurement(z, measurement_delay_sec, camera_motion)
        conf = clamp(float(conf), 0.0, 1.0)
        scale = 1.0 + (1.0 - conf) * self.detector_r_scale
        R = np.diag([self.r_detector_pos * scale, self.r_detector_pos * scale, self.r_detector_size * scale, self.r_detector_size * scale])
        ok = self._update(z_update, R)
        if ok:
            self._blend_measured_velocity(z, dt, self.detector_velocity_blend, camera_motion)
            self.lost_frames = 0
        return ok

    def get_bbox(self):
        if not self.initialized:
            return None
        return cxcywh_to_xyxy(self.x[0:4, 0])

    def get_predicted_bbox(self, ahead_time: float, camera_motion: tuple[float, float] = (0.0, 0.0)):
        if not self.initialized:
            return None
        dt = max(0.0, min(float(ahead_time), self.max_dt if self.max_dt > 0 else float(ahead_time)))
        x_future = self.x.copy()
        if not self.is_stationary():
            x_future[0, 0] += x_future[4, 0] * dt
            x_future[1, 0] += x_future[5, 0] * dt
        x_future[2, 0] += x_future[6, 0] * dt
        x_future[3, 0] += x_future[7, 0] * dt
        if self.camera_future_compensation:
            x_future[0:2, 0] += self._camera_shift(camera_motion, dt)
        return cxcywh_to_xyxy(x_future[0:4, 0])

    def mark_lost(self) -> None:
        self.lost_frames += 1

    def uncertainty(self) -> float:
        if not self.initialized:
            return math.inf
        return float(max(math.sqrt(max(0.0, self.P[0, 0])), math.sqrt(max(0.0, self.P[1, 1]))))

    def get_velocity(self) -> tuple[float, float]:
        if not self.initialized:
            return 0.0, 0.0
        return float(self.x[4, 0]), float(self.x[5, 0])

    def is_stationary(self) -> bool:
        if not self.initialized:
            return True
        speed = float(np.linalg.norm(self.x[4:6, 0]))
        return self.stationary_count >= max(1, self.stationary_frames) and speed < max(1.0, self.stationary_speed_px_s)

    def motion_score(self) -> float:
        if not self.initialized:
            return 0.0
        speed = float(np.linalg.norm(self.x[4:6, 0]))
        return clamp(speed / max(1.0, self.stationary_speed_px_s * 2.0), 0.0, 1.0)

    def _update(self, z: np.ndarray, R: np.ndarray) -> bool:
        H = self._H()
        z = z.reshape(4, 1)
        y = z - H @ self.x
        S = H @ self.P @ H.T + R
        if self.gate_mahalanobis > 0.0:
            d2 = float(y.T @ np.linalg.inv(S) @ y)
            if d2 > self.gate_mahalanobis:
                self.last_update_accepted = False
                self.last_reject_reason = "mahalanobis_gate"
                return False
        K = self.P @ H.T @ np.linalg.inv(S)
        self.x = self.x + K @ y
        I = np.eye(8, dtype=np.float64)
        KH = K @ H
        self.P = (I - KH) @ self.P @ (I - KH).T + K @ R @ K.T
        self._sanitize_state()
        self.last_update_accepted = True
        self.last_reject_reason = ""
        return True

    def _sanitize_state(self) -> None:
        self.x = np.nan_to_num(self.x, nan=0.0, posinf=0.0, neginf=0.0)
        self.P = np.nan_to_num(self.P, nan=1e6, posinf=1e6, neginf=1e6)
        self.x[2, 0] = max(self.min_size, self.x[2, 0])
        self.x[3, 0] = max(self.min_size, self.x[3, 0])
        self.P = 0.5 * (self.P + self.P.T)

    def _blend_measured_velocity(
        self,
        z: np.ndarray,
        dt: float | None,
        blend: float,
        camera_motion: tuple[float, float] = (0.0, 0.0),
    ) -> None:
        if self.last_z is None:
            self.last_z = z.copy()
            return
        dt = self.default_dt if dt is None else float(dt)
        if dt <= 0.0 or not math.isfinite(dt):
            dt = self.default_dt
        dt = min(dt, self.max_dt)
        measured_v = (z - self.last_z) / max(1e-3, dt)
        measured_v[0:2] -= self._camera_velocity(camera_motion)
        speed = float(np.linalg.norm(measured_v[0:2]))
        if speed < self.stationary_speed_px_s:
            self.stationary_count += 1
            self.motion_count = 0
            measured_v[0:2] = 0.0
            decay = clamp(self.stationary_velocity_decay, 0.0, 1.0)
            self.x[4:6, 0] *= decay
            if self.stationary_count >= max(1, self.stationary_frames):
                self.x[4:6, 0] = 0.0
        elif speed < self.velocity_deadband_px_s:
            self.stationary_count += 1
            self.motion_count = 0
            measured_v[0:2] = 0.0
        elif speed > self.max_velocity_px_s:
            self.stationary_count = 0
            self.motion_count += 1
            measured_v[0:2] *= self.max_velocity_px_s / speed
            if self.motion_count < max(1, self.motion_enter_frames):
                self.stationary_count += 1
                measured_v[0:2] = 0.0
                decay = clamp(self.stationary_velocity_decay, 0.0, 1.0)
                self.x[4:6, 0] *= decay
        else:
            self.motion_count += 1
            if self.motion_count < max(1, self.motion_enter_frames):
                self.stationary_count += 1
                measured_v[0:2] = 0.0
                decay = clamp(self.stationary_velocity_decay, 0.0, 1.0)
                self.x[4:6, 0] *= decay
            else:
                self.stationary_count = 0
        blend = clamp(float(blend), 0.0, 1.0)
        size_blend = clamp(self.size_velocity_blend, 0.0, 1.0)
        self.x[4:6, 0] = (1.0 - blend) * self.x[4:6, 0] + blend * measured_v[0:2]
        self.x[6:8, 0] = (1.0 - size_blend) * self.x[6:8, 0] + size_blend * measured_v[2:4]
        self.last_z = z.copy()

    def _compensate_delayed_measurement(
        self,
        z: np.ndarray,
        delay_sec: float,
        camera_motion: tuple[float, float] = (0.0, 0.0),
    ) -> np.ndarray:
        if not self.delayed_measurement_compensation or delay_sec <= 0.0 or not math.isfinite(delay_sec):
            return z
        delay = min(float(delay_sec), max(0.0, self.max_measurement_delay))
        z_update = z.copy()
        shift = np.zeros(4, dtype=np.float64)
        if not self.is_stationary():
            shift += self.x[4:8, 0] * delay
        if self.camera_delay_compensation:
            shift[0:2] += self._camera_shift(camera_motion, delay)
        shift_norm = float(np.linalg.norm(shift[0:2]))
        if shift_norm > self.max_delayed_shift_px > 0.0:
            shift[0:2] *= self.max_delayed_shift_px / shift_norm
        z_update[0:4] += shift
        z_update[2] = max(self.min_size, z_update[2])
        z_update[3] = max(self.min_size, z_update[3])
        return z_update

    def _camera_velocity(self, camera_motion: tuple[float, float]) -> np.ndarray:
        if not self.camera_motion_compensation:
            return np.zeros(2, dtype=np.float64)
        try:
            motion_x = float(camera_motion[0])
            motion_y = float(camera_motion[1])
        except Exception:
            return np.zeros(2, dtype=np.float64)
        if not (math.isfinite(motion_x) and math.isfinite(motion_y)):
            return np.zeros(2, dtype=np.float64)
        if self.camera_motion_units in {"px_s", "pixel_s", "pixels_per_second"}:
            return np.array([motion_x, motion_y], dtype=np.float64)
        return np.array(
            [
                -self.yaw_px_per_cmd * motion_x,
                -self.pitch_px_per_cmd * motion_y,
            ],
            dtype=np.float64,
        )

    def _camera_shift(self, camera_motion: tuple[float, float], dt: float) -> np.ndarray:
        dt = max(0.0, float(dt))
        shift = self._camera_velocity(camera_motion) * dt
        shift_norm = float(np.linalg.norm(shift))
        if shift_norm > self.max_camera_shift_px > 0.0:
            shift *= self.max_camera_shift_px / shift_norm
        return shift

    def _make_F(self, dt: float) -> np.ndarray:
        F = np.eye(8, dtype=np.float64)
        F[0, 4] = dt
        F[1, 5] = dt
        F[2, 6] = dt
        F[3, 7] = dt
        return F

    def _make_Q(self, dt: float) -> np.ndarray:
        return np.diag(
            [
                self.q_pos * dt,
                self.q_pos * dt,
                self.q_size * dt,
                self.q_size * dt,
                self.q_vel * dt,
                self.q_vel * dt,
                self.q_size_vel * dt,
                self.q_size_vel * dt,
            ]
        ).astype(np.float64)

    def _H(self) -> np.ndarray:
        H = np.zeros((4, 8), dtype=np.float64)
        H[0, 0] = 1.0
        H[1, 1] = 1.0
        H[2, 2] = 1.0
        H[3, 3] = 1.0
        return H
