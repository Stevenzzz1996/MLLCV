from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import time
from pathlib import Path
from threading import Lock

from flask import Flask, Response, jsonify, request, send_file

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.gimbal_controller import A8MiniGimbal


def local_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("192.168.144.25", 37260))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


def make_app(args: argparse.Namespace) -> Flask:
    app = Flask(__name__)
    preview_path = Path(args.preview)
    command_path = Path(args.command_file)
    operator_state_path = Path(args.operator_state_file)
    gimbal = A8MiniGimbal(
        ip=args.ip,
        port=args.gimbal_port,
        yaw_sign=args.yaw_sign,
        pitch_sign=args.pitch_sign,
        dry_run=args.dry_run,
        need_ack=False,
    )
    lock = Lock()
    state = {
        "yaw": 0,
        "pitch": 0,
        "last_cmd_ts": 0.0,
        "last_cmd": "stop",
        "zoom": 1.0,
        "dry_run": bool(args.dry_run),
        "ip": args.ip,
        "port": args.gimbal_port,
        "track_mode": "manual",
        "recording": False,
    }

    def write_json_atomic(path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_name(f".{path.name}.tmp")
        tmp_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp_path, path)

    def write_command(action: str, **extra) -> None:
        payload = {"action": action, "time": time.time(), **extra}
        write_json_atomic(command_path, payload)
        state.update({"last_cmd": action, "last_cmd_ts": time.time()})

    def write_operator_action(action: str, **extra) -> None:
        now = time.time()
        payload = {
            "time": now,
            "source": "dashboard",
            "action": action,
            "yaw": int(state.get("yaw", 0)),
            "pitch": int(state.get("pitch", 0)),
            "zoom": float(state.get("zoom", 1.0)),
            "zoom_direction": 0,
            "track_mode": state.get("track_mode", "manual"),
            "recording": bool(state.get("recording", False)),
            **extra,
        }
        write_json_atomic(operator_state_path, payload)

    def send_speed(yaw: float, pitch: float, name: str = "speed") -> None:
        with lock:
            try:
                gimbal.set_speed(yaw, pitch)
            except Exception as exc:
                state["last_error"] = str(exc)
            state.update({"yaw": int(round(yaw)), "pitch": int(round(pitch)), "last_cmd": name, "last_cmd_ts": time.time()})
            write_operator_action(name, yaw=int(round(yaw)), pitch=int(round(pitch)), zoom_direction=0)

    def send_zoom(direction: int, name: str = "zoom") -> None:
        with lock:
            try:
                gimbal.zoom(direction)
            except Exception as exc:
                state["last_error"] = str(exc)
            state.update({"last_cmd": name, "last_cmd_ts": time.time()})
            write_operator_action(name, zoom_direction=int(direction))

    def set_zoom_multiple(value: float) -> None:
        multiple = max(1.0, min(6.0, float(value)))
        with lock:
            try:
                gimbal.set_zoom(multiple)
            except Exception as exc:
                state["last_error"] = str(exc)
            state.update({"zoom": round(multiple, 1), "last_cmd": "zoom_set", "last_cmd_ts": time.time()})
            write_operator_action("zoom_set", zoom=round(multiple, 1), zoom_direction=0)

    @app.get("/")
    def index() -> Response:
        return Response(INDEX_HTML, mimetype="text/html")

    @app.get("/preview.jpg")
    def preview():
        if preview_path.exists():
            return send_file(preview_path, mimetype="image/jpeg")
        return Response(status=404)

    @app.get("/stream.mjpg")
    def stream_mjpg():
        def gen():
            last_mtime = 0.0
            last_bytes = None
            frame_interval = 1.0 / max(1.0, float(args.stream_fps))
            while True:
                if preview_path.exists():
                    stat = preview_path.stat()
                    if stat.st_mtime != last_mtime or last_bytes is None:
                        last_bytes = preview_path.read_bytes()
                        last_mtime = stat.st_mtime
                    if last_bytes:
                        yield (
                            b"--frame\r\n"
                            b"Content-Type: image/jpeg\r\n"
                            b"Cache-Control: no-store\r\n\r\n"
                            + last_bytes
                            + b"\r\n"
                        )
                time.sleep(frame_interval)

        return Response(gen(), mimetype="multipart/x-mixed-replace; boundary=frame")

    @app.post("/api/speed")
    def api_speed():
        data = request.get_json(force=True, silent=True) or {}
        yaw = max(-100, min(100, float(data.get("yaw", 0))))
        pitch = max(-100, min(100, float(data.get("pitch", 0))))
        if state.get("track_mode") != "manual":
            write_command("manual_mode")
            state["track_mode"] = "manual"
        send_speed(yaw, pitch, "speed")
        return jsonify(state)

    @app.post("/api/stop")
    def api_stop():
        write_command("manual_mode")
        state["track_mode"] = "manual"
        send_speed(0, 0, "stop")
        return jsonify(state)

    @app.post("/api/center")
    def api_center():
        write_command("stop_track")
        state["track_mode"] = "manual"
        with lock:
            try:
                gimbal.center()
            except Exception as exc:
                state["last_error"] = str(exc)
            state.update({"yaw": 0, "pitch": 0, "last_cmd": "center", "last_cmd_ts": time.time()})
            write_operator_action("center", yaw=0, pitch=0)
        return jsonify(state)

    @app.post("/api/zoom")
    def api_zoom():
        data = request.get_json(force=True, silent=True) or {}
        action = str(data.get("action", "")).lower()
        if action in {"in", "zoom_in", "+"}:
            send_zoom(1, "zoom_in")
        elif action in {"out", "zoom_out", "-"}:
            send_zoom(-1, "zoom_out")
        else:
            send_zoom(0, "zoom_stop")
        return jsonify(state)

    @app.post("/api/zoom_set")
    def api_zoom_set():
        data = request.get_json(force=True, silent=True) or {}
        set_zoom_multiple(float(data.get("zoom", state.get("zoom", 1.0))))
        return jsonify(state)

    @app.post("/api/manual")
    def api_manual():
        write_command("manual_mode")
        state["track_mode"] = "manual"
        send_speed(0, 0, "manual")
        return jsonify(state)

    @app.post("/api/track_center")
    def api_track_center():
        data = request.get_json(force=True, silent=True) or {}
        write_command("center_track", box=str(data.get("box", args.center_box)))
        state["track_mode"] = "center_track"
        write_operator_action("center_track", box=str(data.get("box", args.center_box)))
        return jsonify(state)

    @app.post("/api/release_track")
    def api_release_track():
        write_command("stop_track")
        state["track_mode"] = "manual"
        send_speed(0, 0, "release")
        return jsonify(state)

    @app.post("/api/auto_track")
    def api_auto_track():
        write_command("auto_track")
        state["track_mode"] = "auto"
        write_operator_action("auto_track")
        return jsonify(state)

    @app.post("/api/record_start")
    def api_record_start():
        data = request.get_json(force=True, silent=True) or {}
        state["recording"] = True
        write_command("record_start", task=str(data.get("task", "human_scan")))
        write_operator_action("record_start")
        return jsonify(state)

    @app.post("/api/record_stop")
    def api_record_stop():
        state["recording"] = False
        write_command("record_stop")
        write_operator_action("record_stop")
        return jsonify(state)

    @app.get("/api/status")
    def api_status():
        out = dict(state)
        out["preview_mtime"] = preview_path.stat().st_mtime if preview_path.exists() else None
        out["now"] = time.time()
        return jsonify(out)

    return app


INDEX_HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>A8 云台控制</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f4f6f3;
      --ink: #202522;
      --muted: #66706a;
      --line: #c8d0c8;
      --panel: #ffffff;
      --accent: #0f8b6f;
      --danger: #b83232;
      --shadow: 0 10px 30px rgba(30, 40, 35, 0.12);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--ink);
      font-family: Arial, "Microsoft YaHei", sans-serif;
    }
    main {
      display: grid;
      grid-template-columns: minmax(420px, 1fr) 360px;
      gap: 16px;
      padding: 16px;
      min-height: 100vh;
    }
    .preview {
      min-width: 0;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .video {
      width: 100%;
      aspect-ratio: 16 / 9;
      background: #111;
      border: 1px solid var(--line);
      object-fit: contain;
      box-shadow: var(--shadow);
    }
    .bar, .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      box-shadow: var(--shadow);
    }
    .bar {
      min-height: 44px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 10px 12px;
      font-size: 14px;
      color: var(--muted);
    }
    .panel {
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    h1 {
      font-size: 20px;
      line-height: 1.2;
      margin: 0;
      letter-spacing: 0;
    }
    .status {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      font-size: 13px;
    }
    .metric {
      border: 1px solid var(--line);
      padding: 10px;
      min-height: 54px;
      background: #fbfcfb;
    }
    .metric b {
      display: block;
      font-size: 18px;
      color: var(--ink);
      line-height: 1.2;
      margin-top: 3px;
    }
    .pad {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      grid-template-rows: repeat(3, 74px);
      gap: 10px;
    }
    button {
      border: 1px solid var(--line);
      background: #ffffff;
      color: var(--ink);
      font-size: 28px;
      font-weight: 700;
      border-radius: 6px;
      cursor: pointer;
      user-select: none;
      touch-action: none;
      transition: transform 0.08s ease, background 0.12s ease, border-color 0.12s ease;
    }
    button:hover { border-color: var(--accent); }
    button:active, button.active {
      transform: translateY(1px);
      background: #e8f6f1;
      border-color: var(--accent);
    }
    .stop {
      background: #fff0ef;
      color: var(--danger);
      font-size: 18px;
    }
    .center {
      background: #edf7f4;
      color: var(--accent);
      font-size: 18px;
    }
    .wide {
      width: 100%;
      min-height: 48px;
      font-size: 17px;
    }
    .track-actions {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }
    .zoom-actions {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 10px;
    }
    .record-actions {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }
    .mode {
      background: #f8faf8;
      color: var(--ink);
      font-size: 15px;
    }
    .lock {
      background: #e8f6f1;
      color: var(--accent);
      font-size: 15px;
    }
    .slider {
      display: grid;
      gap: 8px;
      font-size: 14px;
      color: var(--muted);
    }
    input[type="range"] { width: 100%; accent-color: var(--accent); }
    @media (max-width: 900px) {
      main { grid-template-columns: 1fr; }
      .panel { order: -1; }
    }
  </style>
</head>
<body>
  <main>
    <section class="preview">
      <img class="video" id="preview" src="/stream.mjpg" alt="preview" />
      <div class="bar">
        <span id="link">preview</span>
        <span id="time">-</span>
      </div>
    </section>
    <aside class="panel">
      <h1>A8 云台控制</h1>
      <div class="status">
        <div class="metric">Yaw<b id="yaw">0</b></div>
        <div class="metric">Pitch<b id="pitch">0</b></div>
        <div class="metric">速度<b id="speedLabel">30</b></div>
        <div class="metric">Zoom<b id="zoomLabel">1.0x</b></div>
        <div class="metric">状态<b id="cmd">stop</b></div>
      </div>
      <div class="track-actions">
        <button class="wide mode" id="manualMode" title="手动控制">MANUAL</button>
        <button class="wide lock" id="trackCenter" title="中心框锁定跟踪">CENTER TRACK</button>
        <button class="wide mode" id="autoTrack" title="自动检测跟踪">AUTO DETECT</button>
        <button class="wide stop" id="releaseTrack" title="释放跟踪">RELEASE</button>
      </div>
      <div class="record-actions">
        <button class="wide lock" id="recordStart" title="开始记录示教数据">REC START</button>
        <button class="wide stop" id="recordStop" title="停止记录示教数据">REC STOP</button>
      </div>
      <div class="slider">
        <label for="speed">速度</label>
        <input id="speed" type="range" min="5" max="80" value="30" />
      </div>
      <div class="zoom-actions">
        <button class="wide mode" data-zoom="out" title="拉远">ZOOM -</button>
        <button class="wide stop" id="zoomStop" title="停止变焦">STOP</button>
        <button class="wide mode" data-zoom="in" title="拉近">ZOOM +</button>
      </div>
      <div class="slider">
        <label for="zoom">变焦</label>
        <input id="zoom" type="range" min="1" max="6" step="0.1" value="1" />
      </div>
      <div class="pad">
        <div></div>
        <button data-yaw="0" data-pitch="-1" title="上">↑</button>
        <div></div>
        <button data-yaw="-1" data-pitch="0" title="左">←</button>
        <button class="stop" id="stop" title="停止">STOP</button>
        <button data-yaw="1" data-pitch="0" title="右">→</button>
        <div></div>
        <button data-yaw="0" data-pitch="1" title="下">↓</button>
        <div></div>
      </div>
      <button class="center wide" id="center" title="回中">CENTER</button>
    </aside>
  </main>
  <script>
    const speed = document.getElementById('speed');
    const zoom = document.getElementById('zoom');
    const speedLabel = document.getElementById('speedLabel');
    const zoomLabel = document.getElementById('zoomLabel');
    const yawEl = document.getElementById('yaw');
    const pitchEl = document.getElementById('pitch');
    const cmdEl = document.getElementById('cmd');
    const timeEl = document.getElementById('time');
    let repeat = null;

    function post(path, body = {}) {
      return fetch(path, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)})
        .then(r => r.json()).then(update);
    }
    function update(s) {
      yawEl.textContent = s.yaw ?? 0;
      pitchEl.textContent = s.pitch ?? 0;
      if (s.zoom !== undefined) {
        zoomLabel.textContent = `${Number(s.zoom).toFixed(1)}x`;
      }
      cmdEl.textContent = s.last_cmd ?? '-';
      timeEl.textContent = new Date().toLocaleTimeString();
    }
    function sendDir(yawSign, pitchSign) {
      const v = Number(speed.value);
      post('/api/speed', {yaw: yawSign * v, pitch: pitchSign * v});
    }
    function startButton(btn) {
      const y = Number(btn.dataset.yaw);
      const p = Number(btn.dataset.pitch);
      btn.classList.add('active');
      sendDir(y, p);
      repeat = setInterval(() => sendDir(y, p), 140);
    }
    function releaseButtons() {
      if (document.querySelector('button[data-zoom].active')) return;
      const activeDrive = document.querySelector('button[data-yaw].active');
      if (!activeDrive && !repeat) return;
      document.querySelectorAll('button[data-yaw].active').forEach(b => b.classList.remove('active'));
      if (repeat) clearInterval(repeat);
      repeat = null;
      post('/api/stop');
    }
    function startZoom(action, btn) {
      btn.classList.add('active');
      post('/api/zoom', {action});
      repeat = setInterval(() => post('/api/zoom', {action}), 180);
    }
    function releaseZoom() {
      document.querySelectorAll('button.active').forEach(b => b.classList.remove('active'));
      if (repeat) clearInterval(repeat);
      repeat = null;
      post('/api/zoom', {action: 'stop'});
    }
    document.querySelectorAll('button[data-yaw]').forEach(btn => {
      btn.addEventListener('pointerdown', e => { e.preventDefault(); startButton(btn); });
    });
    document.querySelectorAll('button[data-zoom]').forEach(btn => {
      btn.addEventListener('pointerdown', e => { e.preventDefault(); e.stopPropagation(); startZoom(btn.dataset.zoom, btn); });
      btn.addEventListener('pointerup', e => { e.preventDefault(); e.stopPropagation(); releaseZoom(); });
      btn.addEventListener('pointercancel', e => { e.preventDefault(); e.stopPropagation(); releaseZoom(); });
    });
    window.addEventListener('pointerup', releaseButtons);
    window.addEventListener('pointercancel', releaseButtons);
    document.getElementById('stop').onclick = () => releaseButtons();
    document.getElementById('zoomStop').onclick = () => releaseZoom();
    document.getElementById('center').onclick = () => post('/api/center');
    document.getElementById('manualMode').onclick = () => post('/api/manual');
    document.getElementById('trackCenter').onclick = () => post('/api/track_center', {box: '260x180'});
    document.getElementById('autoTrack').onclick = () => post('/api/auto_track');
    document.getElementById('releaseTrack').onclick = () => post('/api/release_track');
    document.getElementById('recordStart').onclick = () => post('/api/record_start', {task: 'human_scan'});
    document.getElementById('recordStop').onclick = () => post('/api/record_stop');
    speed.oninput = () => speedLabel.textContent = speed.value;
    zoom.oninput = () => zoomLabel.textContent = `${Number(zoom.value).toFixed(1)}x`;
    zoom.onchange = () => post('/api/zoom_set', {zoom: Number(zoom.value)});
    window.addEventListener('keydown', e => {
      if (repeat) return;
      const map = {ArrowLeft: [-1,0], ArrowRight: [1,0], ArrowUp: [0,-1], ArrowDown: [0,1], a: [-1,0], d: [1,0], w: [0,-1], s: [0,1]};
      const v = map[e.key];
      if (v) { e.preventDefault(); sendDir(v[0], v[1]); repeat = setInterval(() => sendDir(v[0], v[1]), 140); }
      if (e.key === ' ') { e.preventDefault(); releaseButtons(); }
    });
    window.addEventListener('keyup', e => {
      if (['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','a','d','w','s'].includes(e.key)) releaseButtons();
    });
    setInterval(() => {
      fetch('/api/status').then(r => r.json()).then(update).catch(() => {});
    }, 500);
  </script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=7860)
    parser.add_argument("--ip", default="192.168.144.25")
    parser.add_argument("--gimbal-port", type=int, default=37260)
    parser.add_argument("--yaw-sign", type=int, default=1)
    parser.add_argument("--pitch-sign", type=int, default=-1)
    parser.add_argument("--preview", default="/tmp/source_track_preview.jpg")
    parser.add_argument("--stream-fps", type=float, default=25.0)
    parser.add_argument("--command-file", default="/tmp/source_track_command.json")
    parser.add_argument("--operator-state-file", default="/tmp/source_track_operator_action.json")
    parser.add_argument("--center-box", default="260x180")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    app = make_app(args)
    print(f"dashboard http://{local_ip()}:{args.port}", flush=True)
    app.run(host=args.host, port=args.port, threaded=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
