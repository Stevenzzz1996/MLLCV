from __future__ import annotations

import argparse
from pathlib import Path
import sys

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.asymtrack_tracker import AsymTrackTracker


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="0")
    parser.add_argument("--model", default="/home/mll/Downloads/AsymTrack_ep0500.pth.tar")
    parser.add_argument("--repo-root", default="third_party/AsymTrack")
    parser.add_argument("--yaml-name", default="tiny")
    args = parser.parse_args()
    source = 0 if args.source == "0" else args.source
    cap = cv2.VideoCapture(source)
    tracker = AsymTrackTracker(model=args.model, repo_root=args.repo_root, yaml_name=args.yaml_name)
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if tracker.initialized:
            bbox, score, track_ok = tracker.update(frame)
            if track_ok:
                x1, y1, x2, y2 = map(int, bbox)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (40, 240, 80), 2)
        cv2.imshow("AsymTrack click test", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("i"):
            roi = cv2.selectROI("AsymTrack click test", frame, False, False)
            x, y, w, h = roi
            if w > 0 and h > 0:
                tracker.init(frame, (x, y, x + w, y + h))
        elif key == 27:
            break
    cap.release()
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
