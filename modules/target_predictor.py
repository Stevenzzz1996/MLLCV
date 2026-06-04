from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import math

import numpy as np

from .common import bbox_center


@dataclass
class FilterStateNode:
    t: float
    x_pred: np.ndarray
    p_pred: np.ndarray
    x_update: np.ndarray
    p_update: np.ndarray
    u: tuple[float, float]
    dt: float
    has_update: bool = False


class KalmanTargetPredictor:
    """Delay-aware image-plane Kalman filter.

    The public methods keep the previous simple-KF API, while update() can now
    correct a delayed observation at its estimated image timestamp and replay the
    saved state history to the current wall-clock time.
    """

    def __init__(
        self,
        process_noise: float = 50.0,
        measurement_noise: float = 25.0,
        history_sec: float = 2.0,
        latency_est_ms: float = 0.0,
        init_pos_var: float = 100.0,
        init_vel_var: float = 10000.0,
        gate_px: float = 0.0,
        gate_mahalanobis: float = 0.0,
        yaw_px_per_cmd: float = 0.0,
        pitch_px_per_cmd: float = 0.0,
        reliable_sigma_px: float = 30.0,
        max_sigma_px: float = 80.0,
    ) -> None:
        self.process_noise = float(process_noise)
        self.measurement_noise = float(measurement_noise)
        self.history_sec = max(0.2, float(history_sec))
        self.latency_est_sec = max(0.0, float(latency_est_ms) / 1000.0)
        self.init_pos_var = float(init_pos_var)
        self.init_vel_var = float(init_vel_var)
        self.gate_px = max(0.0, float(gate_px))
        self.gate_mahalanobis = max(0.0, float(gate_mahalanobis))
        self.yaw_px_per_cmd = float(yaw_px_per_cmd)
        self.pitch_px_per_cmd = float(pitch_px_per_cmd)
        self.reliable_sigma_px = max(1.0, float(reliable_sigma_px))
        self.max_sigma_px = max(self.reliable_sigma_px + 1.0, float(max_sigma_px))
        self.reset()

    def reset(self) -> None:
        self.x = np.zeros((4, 1), dtype=np.float64)
        self.P = np.eye(4, dtype=np.float64) * 500.0
        self.last_ts: float | None = None
        self.last_measurement_ts: float | None = None
        self.initialized = False
        self.history: deque[FilterStateNode] = deque()
        self.last_update_accepted = True
        self.last_reject_reason = ""

    def update(
        self,
        bbox_xyxy,
        timestamp: float,
        current_time: float | None = None,
        score: float = 1.0,
        area_ratio: float | None = None,
        u: tuple[float, float] = (0.0, 0.0),
        timestamp_is_image_time: bool = False,
    ) -> bool:
        cx, cy = bbox_center(bbox_xyxy)
        t_now = float(current_time if current_time is not None else timestamp)
        t_img = float(timestamp if timestamp_is_image_time else timestamp - self.latency_est_sec)
        t_img = min(t_img, t_now)
        measurement = np.array([[cx], [cy]], dtype=np.float64)
        return self.update_measurement(measurement, t_img, t_now, score=score, area_ratio=area_ratio, u=u)

    def update_measurement(
        self,
        measurement: np.ndarray,
        measurement_ts: float,
        current_time: float,
        score: float = 1.0,
        area_ratio: float | None = None,
        u: tuple[float, float] = (0.0, 0.0),
    ) -> bool:
        z = np.asarray(measurement, dtype=np.float64).reshape(2, 1)
        t_img = float(measurement_ts)
        t_now = max(float(current_time), t_img)
        if not self.initialized:
            self.x[:, 0] = [z[0, 0], z[1, 0], 0.0, 0.0]
            self.P = np.diag([self.init_pos_var, self.init_pos_var, self.init_vel_var, self.init_vel_var]).astype(
                np.float64
            )
            self.last_ts = t_img
            self.last_measurement_ts = t_img
            self.initialized = True
            self._append_node(t_img, self.x.copy(), self.P.copy(), self.x.copy(), self.P.copy(), u, 0.0, True)
            if t_now > t_img:
                self.predict_to(t_now, u)
            self.last_update_accepted = True
            self.last_reject_reason = ""
            return True

        self.predict_to(t_now, u)
        if not self.history:
            self.last_update_accepted = False
            self.last_reject_reason = "empty_history"
            return False
        if t_img < self.history[0].t - 1e-6:
            self.last_update_accepted = False
            self.last_reject_reason = "measurement_too_old"
            return False

        idx = self._ensure_node_at(t_img, u)
        node = self.history[idx]
        x_base = node.x_pred.copy()
        p_base = node.p_pred.copy()
        H = self._H()
        R = self._measurement_noise(score, area_ratio)
        residual = z - H @ x_base
        S = H @ p_base @ H.T + R
        if self._reject_measurement(residual, S):
            self.last_update_accepted = False
            return False

        K = p_base @ H.T @ np.linalg.inv(S)
        x_update = x_base + K @ residual
        I = np.eye(4, dtype=np.float64)
        p_update = (I - K @ H) @ p_base @ (I - K @ H).T + K @ R @ K.T
        self.history[idx] = FilterStateNode(
            t=node.t,
            x_pred=node.x_pred,
            p_pred=node.p_pred,
            x_update=x_update,
            p_update=p_update,
            u=node.u,
            dt=node.dt,
            has_update=True,
        )
        self._replay_from(idx)
        self._trim_history()
        self.last_measurement_ts = t_img
        self.last_update_accepted = True
        self.last_reject_reason = ""
        return True

    def predict_to(self, timestamp: float, u: tuple[float, float] = (0.0, 0.0)) -> None:
        if not self.initialized:
            return
        t = float(timestamp)
        if self.last_ts is None:
            self.last_ts = t
            return
        if t <= self.last_ts + 1e-6:
            return
        dt = max(1e-4, min(0.5, t - self.last_ts))
        F = self._F(dt)
        B = self._B(dt)
        Q = self._Q(dt)
        u_vec = np.array([[float(u[0])], [float(u[1])]], dtype=np.float64)
        x_pred = F @ self.x + B @ u_vec
        p_pred = F @ self.P @ F.T + Q
        self.x = x_pred
        self.P = p_pred
        self.last_ts = t
        self._append_node(t, x_pred.copy(), p_pred.copy(), x_pred.copy(), p_pred.copy(), u, dt, False)
        self._trim_history()

    def predict_future(self, future_dt: float) -> tuple[float, float] | None:
        if not self.initialized:
            return None
        dt = max(0.0, float(future_dt))
        cx = self.x[0, 0] + self.x[2, 0] * dt
        cy = self.x[1, 0] + self.x[3, 0] * dt
        return float(cx), float(cy)

    def get_velocity(self) -> tuple[float, float]:
        if not self.initialized:
            return 0.0, 0.0
        return float(self.x[2, 0]), float(self.x[3, 0])

    def get_center(self) -> tuple[float, float] | None:
        if not self.initialized:
            return None
        return float(self.x[0, 0]), float(self.x[1, 0])

    def get_sigma(self) -> tuple[float, float]:
        if not self.initialized:
            return math.inf, math.inf
        return float(math.sqrt(max(0.0, self.P[0, 0]))), float(math.sqrt(max(0.0, self.P[1, 1])))

    def confidence_scale(self) -> float:
        sigma = max(self.get_sigma())
        if not math.isfinite(sigma):
            return 0.0
        if sigma <= self.reliable_sigma_px:
            return 1.0
        if sigma >= self.max_sigma_px:
            return 0.0
        return float((self.max_sigma_px - sigma) / (self.max_sigma_px - self.reliable_sigma_px))

    def is_reliable(self) -> bool:
        return max(self.get_sigma()) <= self.max_sigma_px

    def _append_node(self, t, x_pred, p_pred, x_update, p_update, u, dt, has_update) -> None:
        self.history.append(
            FilterStateNode(
                t=float(t),
                x_pred=x_pred,
                p_pred=p_pred,
                x_update=x_update,
                p_update=p_update,
                u=(float(u[0]), float(u[1])),
                dt=float(dt),
                has_update=has_update,
            )
        )

    def _trim_history(self) -> None:
        if self.last_ts is None:
            return
        min_t = self.last_ts - self.history_sec
        while len(self.history) > 1 and self.history[0].t < min_t:
            self.history.popleft()

    def _replay_from(self, start_idx: int) -> None:
        for i in range(start_idx + 1, len(self.history)):
            prev = self.history[i - 1]
            old = self.history[i]
            dt = max(1e-4, min(0.5, old.t - prev.t))
            F = self._F(dt)
            B = self._B(dt)
            Q = self._Q(dt)
            u_vec = np.array([[old.u[0]], [old.u[1]]], dtype=np.float64)
            x_pred = F @ prev.x_update + B @ u_vec
            p_pred = F @ prev.p_update @ F.T + Q
            self.history[i] = FilterStateNode(
                t=old.t,
                x_pred=x_pred,
                p_pred=p_pred,
                x_update=x_pred,
                p_update=p_pred,
                u=old.u,
                dt=dt,
                has_update=False,
            )
        current = self.history[-1]
        self.x = current.x_update.copy()
        self.P = current.p_update.copy()
        self.last_ts = current.t

    def _ensure_node_at(self, timestamp: float, u: tuple[float, float]) -> int:
        t = float(timestamp)
        eps = 1e-4
        for i, node in enumerate(self.history):
            if abs(node.t - t) <= eps:
                return i
        if t >= self.history[-1].t:
            self.predict_to(t, u)
            return len(self.history) - 1
        for i in range(len(self.history) - 1):
            prev = self.history[i]
            nxt = self.history[i + 1]
            if prev.t < t < nxt.t:
                dt = max(1e-4, min(0.5, t - prev.t))
                interval_u = nxt.u
                F = self._F(dt)
                B = self._B(dt)
                Q = self._Q(dt)
                u_vec = np.array([[interval_u[0]], [interval_u[1]]], dtype=np.float64)
                x_pred = F @ prev.x_update + B @ u_vec
                p_pred = F @ prev.p_update @ F.T + Q
                self.history.insert(
                    i + 1,
                    FilterStateNode(
                        t=t,
                        x_pred=x_pred,
                        p_pred=p_pred,
                        x_update=x_pred.copy(),
                        p_update=p_pred.copy(),
                        u=interval_u,
                        dt=dt,
                        has_update=False,
                    ),
                )
                self._replay_from(i + 1)
                return i + 1
        return 0

    def _reject_measurement(self, residual: np.ndarray, S: np.ndarray) -> bool:
        if self.gate_px > 0 and float(np.linalg.norm(residual)) > self.gate_px:
            self.last_reject_reason = "pixel_gate"
            return True
        if self.gate_mahalanobis > 0:
            d2 = float(residual.T @ np.linalg.inv(S) @ residual)
            if d2 > self.gate_mahalanobis:
                self.last_reject_reason = "mahalanobis_gate"
                return True
        return False

    def _measurement_noise(self, score: float, area_ratio: float | None) -> np.ndarray:
        score = max(0.05, min(1.0, float(score)))
        scale = 1.0 / score
        if area_ratio is not None and area_ratio > 0:
            scale *= max(1.0, min(4.0, 0.01 / float(area_ratio)))
        return np.eye(2, dtype=np.float64) * self.measurement_noise * scale

    def _F(self, dt: float) -> np.ndarray:
        return np.array([[1, 0, dt, 0], [0, 1, 0, dt], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=np.float64)

    def _B(self, dt: float) -> np.ndarray:
        return np.array(
            [[-self.yaw_px_per_cmd * dt, 0.0], [0.0, -self.pitch_px_per_cmd * dt], [0.0, 0.0], [0.0, 0.0]],
            dtype=np.float64,
        )

    def _Q(self, dt: float) -> np.ndarray:
        q = self.process_noise
        return np.diag([0.25 * q * dt * dt, 0.25 * q * dt * dt, q * dt, q * dt]).astype(np.float64)

    def _H(self) -> np.ndarray:
        return np.array([[1, 0, 0, 0], [0, 1, 0, 0]], dtype=np.float64)
