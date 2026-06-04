"""JSONL writer for MLLCV VLA episode steps."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .schema import EpisodeStep


class EpisodeJSONLWriter:
    """Write VLA episode steps into a JSONL file.

    The JSONL format is simple, inspectable, and easy to convert later.
    Large images/videos should be stored as files, while the JSONL rows
    keep relative paths and synchronized metadata.
    """

    def __init__(self, output_path: str | Path) -> None:
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self._fp = self.output_path.open("w", encoding="utf-8")

    def write_step(self, step: EpisodeStep) -> None:
        self._fp.write(json.dumps(step.to_dict(), ensure_ascii=False) + "\n")
        self._fp.flush()

    def write_steps(self, steps: Iterable[EpisodeStep]) -> None:
        for step in steps:
            self.write_step(step)

    def close(self) -> None:
        if not self._fp.closed:
            self._fp.close()

    def __enter__(self) -> "EpisodeJSONLWriter":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
