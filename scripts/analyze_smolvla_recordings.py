from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def analyze_episode(episode_dir: Path) -> dict:
    metadata = load_json(episode_dir / "metadata.json")
    data_path = episode_dir / "data.jsonl"
    frames = 0
    nonzero_actions = 0
    states: Counter[str] = Counter()
    classes: Counter[str] = Counter()
    yaw_abs_sum = 0.0
    pitch_abs_sum = 0.0
    zoom_nonzero = 0
    if data_path.exists():
        with data_path.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                frames += 1
                states[str(row.get("state", ""))] += 1
                target_class = row.get("target_class") or {}
                cls_name = target_class.get("cls_name") or target_class.get("cls_id")
                if cls_name not in (None, ""):
                    classes[str(cls_name)] += 1
                action = row.get("action_vector") or [0.0, 0.0, 0.0]
                yaw = float(action[0]) if len(action) > 0 else 0.0
                pitch = float(action[1]) if len(action) > 1 else 0.0
                zoom = float(action[2]) if len(action) > 2 else 0.0
                yaw_abs_sum += abs(yaw)
                pitch_abs_sum += abs(pitch)
                if abs(zoom) > 1e-6:
                    zoom_nonzero += 1
                if abs(yaw) > 1e-6 or abs(pitch) > 1e-6 or abs(zoom) > 1e-6:
                    nonzero_actions += 1
    fps = float(metadata.get("fps") or 25.0)
    return {
        "episode": episode_dir.name,
        "schema": metadata.get("schema", "-"),
        "task": metadata.get("task", "-"),
        "frames": frames,
        "seconds": frames / max(1e-6, fps),
        "nonzero_ratio": nonzero_actions / max(1, frames),
        "mean_abs_yaw": yaw_abs_sum / max(1, frames),
        "mean_abs_pitch": pitch_abs_sum / max(1, frames),
        "zoom_nonzero": zoom_nonzero,
        "top_state": states.most_common(1)[0][0] if states else "-",
        "states": dict(states),
        "classes": dict(classes),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default="recordings/smolvla_scan")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    root = Path(args.root)
    episodes = sorted([p for p in root.glob("episode_*") if p.is_dir()])
    if args.limit > 0:
        episodes = episodes[-args.limit :]
    rows = [analyze_episode(p) for p in episodes]

    print(
        f"{'episode':<24} {'schema':<16} {'frames':>7} {'sec':>7} "
        f"{'nz%':>6} {'|yaw|':>7} {'|pit|':>7} {'top_state':<12} classes"
    )
    for row in rows:
        classes = ",".join(f"{k}:{v}" for k, v in sorted(row["classes"].items())) or "-"
        print(
            f"{row['episode']:<24} {row['schema']:<16} {row['frames']:>7} "
            f"{row['seconds']:>7.1f} {row['nonzero_ratio'] * 100:>5.1f}% "
            f"{row['mean_abs_yaw']:>7.3f} {row['mean_abs_pitch']:>7.3f} "
            f"{row['top_state']:<12} {classes}"
        )

    if rows:
        total_frames = sum(r["frames"] for r in rows)
        total_nonzero = sum(round(r["nonzero_ratio"] * r["frames"]) for r in rows)
        print()
        print(f"episodes={len(rows)} frames={total_frames} nonzero_action_ratio={total_nonzero / max(1, total_frames):.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
