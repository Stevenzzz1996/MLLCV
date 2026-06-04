"""Conversion stub from MLLCV JSONL episodes to LeRobot-style datasets.

This module is intentionally conservative. It validates that an MLLCV
episode exists and explains the planned mapping to LeRobotDataset fields.
A full converter will be implemented after real data collection stabilizes.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Iterable


def iter_jsonl(path: Path) -> Iterable[Dict]:
    with path.open("r", encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if line:
                yield json.loads(line)


def validate_episode(jsonl_path: str | Path) -> int:
    path = Path(jsonl_path)
    if not path.exists():
        raise FileNotFoundError(f"Episode file not found: {path}")

    count = 0
    required = {"episode_id", "frame_id", "timestamp", "instruction", "observation", "action"}
    for row in iter_jsonl(path):
        missing = required - set(row.keys())
        if missing:
            raise ValueError(f"Missing fields at row {count}: {missing}")
        count += 1

    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to an MLLCV episode JSONL file.")
    args = parser.parse_args()

    count = validate_episode(args.input)
    print(f"Validated {count} steps from {args.input}")
    print("LeRobot conversion is planned but not fully implemented yet.")
    print("Planned mapping:")
    print("- observation.rgb_image -> observation.images.rgb")
    print("- observation.tracking.* -> observation.state")
    print("- observation.gimbal.* -> observation.state")
    print("- instruction -> task language instruction")
    print("- action.yaw_rate_deg_s / pitch_rate_deg_s / zoom_cmd -> action")


if __name__ == "__main__":
    main()
