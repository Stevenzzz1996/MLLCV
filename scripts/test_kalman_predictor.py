from __future__ import annotations

import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.target_predictor import KalmanTargetPredictor


def main() -> int:
    predictor = KalmanTargetPredictor()
    start = time.time()
    for i in range(20):
        ts = start + i * 0.04
        bbox = (100 + i * 4, 80 + i * 2, 150 + i * 4, 130 + i * 2)
        predictor.update(bbox, ts)
        print(i, "center=", predictor.get_center(), "future=", predictor.predict_future(0.1), "vel=", predictor.get_velocity())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
