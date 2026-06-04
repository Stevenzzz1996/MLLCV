from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default="/tmp/source_track_preview.jpg")
    parser.add_argument("--title", default="A8 TensorRT tracking preview")
    parser.add_argument("--fps", type=float, default=30.0)
    args = parser.parse_args()

    path = Path(args.path)
    delay = 1.0 / max(1.0, args.fps)
    cv2.namedWindow(args.title, cv2.WINDOW_NORMAL)
    last_mtime = 0.0

    while True:
        if path.exists():
            mtime = path.stat().st_mtime
            if mtime != last_mtime:
                frame = cv2.imread(str(path))
                if frame is not None:
                    cv2.imshow(args.title, frame)
                    last_mtime = mtime
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break
        time.sleep(delay)

    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
