from __future__ import annotations

from .common import clamp


class VisualServo:
    def __init__(
        self,
        kp_yaw: float = 30,
        kp_pitch: float = 22,
        kd_yaw: float = 0,
        kd_pitch: float = 0,
        deadzone_x: float = 0.04,
        deadzone_y: float = 0.04,
        hold_deadzone_x: float = 0.06,
        hold_deadzone_y: float = 0.08,
        stationary_vel_norm: float = 0.08,
        min_speed_error_x: float = 0.08,
        min_speed_error_y: float = 0.10,
        smooth_alpha: float = 0.5,
        max_yaw_speed: float = 35,
        max_pitch_speed: float = 25,
        min_yaw_speed: float = 0,
        min_pitch_speed: float = 0,
        max_ff_yaw_speed: float = 18,
        max_ff_pitch_speed: float = 10,
        max_gain_scale: float = 1.8,
        center_lock_enter_x: float = 0.035,
        center_lock_enter_y: float = 0.045,
        center_lock_release_x: float = 0.085,
        center_lock_release_y: float = 0.105,
        overshoot_brake_error_x: float = 0.18,
        overshoot_brake_error_y: float = 0.22,
        yaw_sign: float = 1.0,
        pitch_sign: float = 1.0,
    ) -> None:
        self.kp_yaw = kp_yaw
        self.kp_pitch = kp_pitch
        self.kd_yaw = kd_yaw
        self.kd_pitch = kd_pitch
        self.deadzone_x = deadzone_x
        self.deadzone_y = deadzone_y
        self.hold_deadzone_x = max(float(hold_deadzone_x), float(deadzone_x))
        self.hold_deadzone_y = max(float(hold_deadzone_y), float(deadzone_y))
        self.stationary_vel_norm = max(0.0, float(stationary_vel_norm))
        self.min_speed_error_x = max(float(min_speed_error_x), float(deadzone_x))
        self.min_speed_error_y = max(float(min_speed_error_y), float(deadzone_y))
        self.smooth_alpha = clamp(smooth_alpha, 0.0, 1.0)
        self.max_yaw_speed = max_yaw_speed
        self.max_pitch_speed = max_pitch_speed
        self.min_yaw_speed = max(0.0, float(min_yaw_speed))
        self.min_pitch_speed = max(0.0, float(min_pitch_speed))
        self.max_ff_yaw_speed = max_ff_yaw_speed
        self.max_ff_pitch_speed = max_ff_pitch_speed
        self.max_gain_scale = max(1.0, float(max_gain_scale))
        self.center_lock_enter_x = max(0.0, float(center_lock_enter_x))
        self.center_lock_enter_y = max(0.0, float(center_lock_enter_y))
        self.center_lock_release_x = max(self.center_lock_enter_x, float(center_lock_release_x))
        self.center_lock_release_y = max(self.center_lock_enter_y, float(center_lock_release_y))
        self.overshoot_brake_error_x = max(0.0, float(overshoot_brake_error_x))
        self.overshoot_brake_error_y = max(0.0, float(overshoot_brake_error_y))
        self.yaw_sign = 1.0 if yaw_sign >= 0 else -1.0
        self.pitch_sign = 1.0 if pitch_sign >= 0 else -1.0
        self._last = (0.0, 0.0)
        self._last_err = (None, None)
        self._lock_x = False
        self._lock_y = False

    def compute(self, frame_shape, predicted_center, target_velocity=(0.0, 0.0), gain_scale: float = 1.0):
        if predicted_center is None:
            return 0, 0, 0.0, 0.0
        err_x, err_y = self.measure_error(frame_shape, predicted_center)
        if err_x is None or err_y is None:
            return 0, 0, 0.0, 0.0
        h, w = frame_shape[:2]
        vx, vy = target_velocity
        gain_scale = clamp(gain_scale, 0.0, self.max_gain_scale)
        vx_norm = vx / max(1.0, w * 0.5)
        vy_norm = vy / max(1.0, h * 0.5)
        stationary_x = abs(vx_norm) < self.stationary_vel_norm
        stationary_y = abs(vy_norm) < self.stationary_vel_norm
        self._lock_x = self._update_axis_lock(self._lock_x, stationary_x, err_x, self.center_lock_enter_x, self.center_lock_release_x)
        self._lock_y = self._update_axis_lock(self._lock_y, stationary_y, err_y, self.center_lock_enter_y, self.center_lock_release_y)
        hold_x = stationary_x and abs(err_x) < self.hold_deadzone_x
        hold_y = stationary_y and abs(err_y) < self.hold_deadzone_y
        if self._lock_x:
            hold_x = True
        if self._lock_y:
            hold_y = True
        yaw_p = 0.0 if hold_x or abs(err_x) < self.deadzone_x else self.kp_yaw * err_x
        pitch_p = 0.0 if hold_y or abs(err_y) < self.deadzone_y else self.kp_pitch * err_y
        yaw_ff = 0.0 if hold_x else clamp(self.kd_yaw * vx_norm, -self.max_ff_yaw_speed, self.max_ff_yaw_speed)
        pitch_ff = 0.0 if hold_y else clamp(self.kd_pitch * vy_norm, -self.max_ff_pitch_speed, self.max_ff_pitch_speed)
        yaw = self.yaw_sign * gain_scale * (yaw_p + yaw_ff)
        pitch = self.pitch_sign * gain_scale * (pitch_p + pitch_ff)
        if abs(yaw) > 0.0 and (abs(err_x) >= self.min_speed_error_x or not stationary_x):
            yaw = self._apply_min_speed(yaw, self.min_yaw_speed)
        if abs(pitch) > 0.0 and (abs(err_y) >= self.min_speed_error_y or not stationary_y):
            pitch = self._apply_min_speed(pitch, self.min_pitch_speed)
        yaw = clamp(yaw, -self.max_yaw_speed, self.max_yaw_speed)
        pitch = clamp(pitch, -self.max_pitch_speed, self.max_pitch_speed)
        alpha = clamp(self.smooth_alpha, 0.0, 1.0)
        last_yaw, last_pitch = self._last
        last_err_x, last_err_y = self._last_err
        if last_err_x is not None and err_x * last_err_x < 0.0 and abs(err_x) < self.overshoot_brake_error_x:
            yaw = 0.0
            last_yaw = 0.0
        if last_err_y is not None and err_y * last_err_y < 0.0 and abs(err_y) < self.overshoot_brake_error_y:
            pitch = 0.0
            last_pitch = 0.0
        if hold_x:
            yaw = 0.0
            last_yaw = 0.0
        if hold_y:
            pitch = 0.0
            last_pitch = 0.0
        yaw = alpha * last_yaw + (1.0 - alpha) * yaw
        pitch = alpha * last_pitch + (1.0 - alpha) * pitch
        self._last = (yaw, pitch)
        self._last_err = (err_x, err_y)
        return int(round(yaw)), int(round(pitch)), err_x, err_y

    def compute_bbox(self, frame_shape, bbox_xyxy, target_velocity=(0.0, 0.0), gain_scale: float = 1.0):
        center = self._bbox_center(bbox_xyxy)
        return self.compute(frame_shape, center, target_velocity, gain_scale)

    def measure_error(self, frame_shape, target_center):
        if frame_shape is None or len(frame_shape) < 2 or target_center is None:
            return None, None
        h, w = frame_shape[:2]
        if h <= 0 or w <= 0:
            return None, None
        cx, cy = target_center
        err_x = (cx - w * 0.5) / (w * 0.5)
        err_y = (cy - h * 0.5) / (h * 0.5)
        return err_x, err_y

    def reset(self) -> None:
        self._last = (0.0, 0.0)
        self._last_err = (None, None)
        self._lock_x = False
        self._lock_y = False

    def _update_axis_lock(self, locked: bool, stationary: bool, err: float, enter: float, release: float) -> bool:
        if not stationary:
            return False
        if locked:
            return abs(err) <= release
        return abs(err) <= enter

    def _apply_min_speed(self, value: float, min_speed: float) -> float:
        if min_speed <= 0.0 or abs(value) >= min_speed:
            return value
        return min_speed if value > 0.0 else -min_speed

    def _bbox_center(self, bbox_xyxy):
        if bbox_xyxy is None or len(bbox_xyxy) != 4:
            return None
        try:
            x1, y1, x2, y2 = map(float, bbox_xyxy)
        except Exception:
            return None
        if x2 <= x1 or y2 <= y1:
            return None
        return 0.5 * (x1 + x2), 0.5 * (y1 + y2)
