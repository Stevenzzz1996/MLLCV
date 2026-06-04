"""VLA episode recorder for gimbal-based tracking tasks."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Dict, Optional

from .schema import Action, EpisodeStep, Observation
from .writer import EpisodeJSONLWriter


class VLAEpisodeRecorder:
    """Record synchronized observation-action steps.

    This recorder intentionally does not own the camera or gimbal.
    It receives observation/action objects from the existing tracking loop,
    then writes them as episode steps.
    """

    def __init__(
        self,
        output_dir: str | Path,
        episode_id: str,
        instruction: str = "Keep the target centered in the image.",
    ) -> None:
        self.output_dir = Path(output_dir)
        self.episode_id = episode_id
        self.instruction = instruction
        self.frame_id = 0
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.writer = EpisodeJSONLWriter(self.output_dir / f"{episode_id}.jsonl")

    def record(
        self,
        observation: Observation,
        action: Action,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict] = None,
    ) -> EpisodeStep:
        step = EpisodeStep(
            episode_id=self.episode_id,
            frame_id=self.frame_id,
            timestamp=time.time() if timestamp is None else timestamp,
            instruction=self.instruction,
            observation=observation,
            action=action,
            metadata=metadata or {},
        )
        self.writer.write_step(step)
        self.frame_id += 1
        return step

    def close(self) -> None:
        self.writer.close()
