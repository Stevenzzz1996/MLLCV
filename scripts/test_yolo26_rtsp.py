from __future__ import annotations

import argparse
import time
from pathlib import Path
import sys

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.common import load_config
from modules.latest_frame_rtsp import LatestFrameRTSP
from modules.yolo26_detector import YOLO26Detector


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config_low_latency.yaml")
    parser.add_argument("--source", default=None)
    args = parser.parse_args()
    cfg = load_config(args.config)
    source = args.source or cfg["video"]["source"]
    capture = LatestFrameRTSP(source, cfg["video"].get("rtsp_transport", "udp"))
    detector = YOLO26Detector(cfg["yolo26"]["model"], cfg["yolo26"].get("backend", "ultralytics"), cfg["yolo26"].get("imgsz", 640), cfg["yolo26"].get("conf", 0.35), cfg["yolo26"].get("classes"))
    capture.start()
    try:
        while True:
            ok, frame, ts = capture.read_latest()
            if not ok:
                time.sleep(0.01)
                continue
            for det in detector.detect(frame):
                x1, y1, x2, y2 = map(int, det.bbox_xyxy)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (50, 210, 255), 2)
            cv2.putText(frame, f"age_ms={(time.time() - ts) * 1000:.0f}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.imshow("YOLO26 RTSP test", frame)
            if (cv2.waitKey(1) & 0xFF) == 27:
                break
    finally:
        capture.stop()
        cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
