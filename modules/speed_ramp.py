from __future__ import annotations

import threading
import time

from .common import clamp


class GimbalSpeedRamp:
    def __init__(
        self,
        gimbal,
        hz: float = 120.0,
        max_yaw_delta_per_sec: float = 300.0,
        max_pitch_delta_per_sec: float = 180.0,
        idle_resend_sec: float = 0.2,
    ) -> None:
        self.gimbal = gimbal
        self.period = 1.0 / max(1.0, float(hz))
        self.max_yaw_delta_per_sec = max(0.0, float(max_yaw_delta_per_sec))
        self.max_pitch_delta_per_sec = max(0.0, float(max_pitch_delta_per_sec))
        self.idle_resend_sec = max(self.period, float(idle_resend_sec))
        self._lock = threading.Lock()
        self._target = (0.0, 0.0)
        self._current = (0.0, 0.0)
        self._last_sent = (None, None)
        self._last_send_ts = 0.0
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, name="GimbalSpeedRamp", daemon=True)
        self._thread.start()

    def set_target(self, yaw_speed: float, pitch_speed: float) -> None:
        with self._lock:
            self._target = (float(yaw_speed), float(pitch_speed))

    def stop(self, immediate: bool = True) -> None:
        with self._lock:
            self._target = (0.0, 0.0)
            if immediate:
                self._current = (0.0, 0.0)
        if immediate:
            self.gimbal.stop()
            self._last_sent = (0, 0)
            self._last_send_ts = time.time()

    def close(self) -> None:
        self.stop(immediate=True)
        self._stop.set()
        self._thread.join(timeout=1.0)

    def _loop(self) -> None:
        last_ts = time.time()
        while not self._stop.is_set():
            now = time.time()
            dt = max(1e-3, now - last_ts)
            last_ts = now
            with self._lock:
                target_yaw, target_pitch = self._target
                current_yaw, current_pitch = self._current
                yaw_step = self.max_yaw_delta_per_sec * dt
                pitch_step = self.max_pitch_delta_per_sec * dt
                if yaw_step > 0.0:
                    current_yaw = clamp(target_yaw, current_yaw - yaw_step, current_yaw + yaw_step)
                else:
                    current_yaw = target_yaw
                if pitch_step > 0.0:
                    current_pitch = clamp(target_pitch, current_pitch - pitch_step, current_pitch + pitch_step)
                else:
                    current_pitch = target_pitch
                self._current = (current_yaw, current_pitch)
            self._send_if_needed(current_yaw, current_pitch, now)
            time.sleep(self.period)

    def _send_if_needed(self, yaw_speed: float, pitch_speed: float, now: float) -> None:
        yaw = int(round(yaw_speed))
        pitch = int(round(pitch_speed))
        if (yaw, pitch) == self._last_sent and now - self._last_send_ts < self.idle_resend_sec:
            return
        self.gimbal.set_speed(yaw, pitch)
        self._last_sent = (yaw, pitch)
        self._last_send_ts = now
