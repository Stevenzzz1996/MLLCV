from __future__ import annotations

import socket
import struct
import threading
import time

from .common import clamp


def crc16_ccitt(data: bytes, crc: int = 0) -> int:
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def parse_packet(data: bytes) -> dict | None:
    if len(data) < 10 or data[:2] != b"\x55\x66":
        return None
    recv_crc = struct.unpack("<H", data[-2:])[0]
    if recv_crc != crc16_ccitt(data[:-2]):
        return None
    data_len = struct.unpack("<H", data[3:5])[0]
    if len(data) != 10 + data_len:
        return None
    return {
        "ctrl": data[2],
        "data_len": data_len,
        "seq": struct.unpack("<H", data[5:7])[0],
        "cmd_id": data[7],
        "payload": data[8 : 8 + data_len],
    }


class A8MiniGimbal:
    def __init__(
        self,
        ip: str = "192.168.144.25",
        port: int = 37260,
        yaw_sign: int = 1,
        pitch_sign: int = 1,
        dry_run: bool = False,
        need_ack: bool = False,
        timeout_sec: float = 0.02,
    ) -> None:
        self.addr = (ip, port)
        self.yaw_sign = 1 if yaw_sign >= 0 else -1
        self.pitch_sign = 1 if pitch_sign >= 0 else -1
        self.dry_run = dry_run
        self.need_ack = need_ack
        self.seq = 0
        self._lock = threading.Lock()
        self._last_speed = (0, 0)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(timeout_sec)
        self.last_error = ""
        self._last_error_ts = 0.0

    def _packet(self, cmd_id: int, payload: bytes = b"", need_ack: bool | None = None) -> bytes:
        ctrl = 0x01 if (self.need_ack if need_ack is None else need_ack) else 0x00
        with self._lock:
            seq = self.seq
            self.seq = (self.seq + 1) & 0xFFFF
        header = b"\x55\x66" + struct.pack("<BHHB", ctrl, len(payload), seq, cmd_id) + payload
        return header + struct.pack("<H", crc16_ccitt(header))

    def send(self, cmd_id: int, payload: bytes = b"", need_ack: bool | None = None) -> dict | None:
        packet = self._packet(cmd_id, payload, need_ack)
        if self.dry_run:
            return None
        try:
            self.sock.sendto(packet, self.addr)
        except (OSError, TimeoutError, socket.timeout) as exc:
            self.last_error = str(exc)
            now = time.time()
            if now - self._last_error_ts > 1.0:
                self._last_error_ts = now
                print(f"WARN: gimbal send failed: {exc}", flush=True)
            return None
        if not (self.need_ack if need_ack is None else need_ack):
            return None
        try:
            data, _ = self.sock.recvfrom(1024)
        except socket.timeout:
            return None
        return parse_packet(data)

    def set_speed(self, yaw_speed: float, pitch_speed: float) -> None:
        yaw = int(clamp(round(yaw_speed * self.yaw_sign), -100, 100))
        pitch = int(clamp(round(pitch_speed * self.pitch_sign), -100, 100))
        self._last_speed = (yaw, pitch)
        self.send(0x07, struct.pack("<bb", yaw, pitch))

    def set_angle(self, yaw_deg: float, pitch_deg: float) -> None:
        yaw = int(clamp(round(yaw_deg * 10.0), -1350, 1350))
        pitch = int(clamp(round(pitch_deg * 10.0), -900, 250))
        self.send(0x0E, struct.pack("<hh", yaw, pitch))

    def center(self) -> None:
        self.send(0x08, struct.pack("<B", 1))

    def zoom(self, direction: int) -> None:
        zoom_cmd = int(clamp(direction, -1, 1))
        self.send(0x05, struct.pack("<b", zoom_cmd))

    def zoom_in(self) -> None:
        self.zoom(1)

    def zoom_out(self) -> None:
        self.zoom(-1)

    def zoom_stop(self) -> None:
        self.zoom(0)

    def set_zoom(self, multiple: float) -> None:
        value = float(clamp(multiple, 1.0, 6.0))
        whole = int(value)
        frac = int(round((value - whole) * 10.0))
        if frac >= 10:
            whole += 1
            frac = 0
        self.send(0x0F, struct.pack("<BB", whole, frac))

    def stop(self) -> None:
        self.set_speed(0, 0)

    def close(self) -> None:
        try:
            self.stop()
            time.sleep(0.03)
        except (OSError, TimeoutError, socket.timeout):
            pass
        finally:
            self.sock.close()
