# MLLCV VLA Module

This module provides the early data-recording layer for Vision-Language-Action and imitation-learning experiments in gimbal-based robotic perception.

## Current Scope

The current implementation focuses on:

- episode-based observation-action recording
- JSONL-friendly schema
- tracking state and gimbal telemetry logging
- language instruction attachment
- mock demo without hardware
- future LeRobot-compatible conversion

## Not Yet Included

This module does not yet provide a full VLA model or large-scale policy training. The first milestone is to make the data recording format stable and reproducible.

## Data Unit

Each row is one synchronized step:

```text
image/state/instruction/action/timestamp
```

## Quick Check

```bash
python examples/vla_record_demo.py
python -m mllcv.vla.convert_to_lerobot --input data/mock_vla_episode/episode_mock_000001.jsonl
```
