from __future__ import annotations

import importlib
import sys
from pathlib import Path


MODULES = [
    "modules.common",
    "modules.gimbal_controller",
    "modules.speed_ramp",
    "modules.visual_servo",
    "modules.dkf_filter",
    "modules.target_predictor",
    "modules.target_selector",
    "mllcv.vla.schema",
    "mllcv.vla.writer",
    "mllcv.vla.recorder",
    "mllcv.vla.convert_to_lerobot",
]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))

    for module_name in MODULES:
        importlib.import_module(module_name)
        print(f"import ok: {module_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
