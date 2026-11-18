#!/usr/bin/env python3
"""Create a 10-second smoke-test project from an authored SHORTFORGE short."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_smoke_project(project: dict) -> dict:
    smoke = json.loads(json.dumps(project))
    duration = min(10, int(smoke.get("duration_seconds", 10)))
    if duration < 1:
        raise ValueError("Smoke project duration must be at least one second")

    selected = []
    for shot in smoke.get("shots", []):
        start = float(shot.get("start_seconds", 0))
        if start >= duration:
            continue
        copy = dict(shot)
        copy["duration_seconds"] = min(
            float(copy.get("duration_seconds", duration - start)),
            duration - start,
        )
        if copy["duration_seconds"] > 0:
            selected.append(copy)
    if not selected:
        raise ValueError("No shots overlap the first ten seconds of the project")

    smoke["shots"] = selected
    smoke["duration_seconds"] = duration
    smoke["width"] = 540
    smoke["height"] = 960
    smoke["quality"] = "smoke"
    render = smoke.setdefault("render", {})
    render.update({"samples": 24, "crf": 20, "preset": "veryfast"})
    smoke.pop("narration_file", None)
    smoke["smoke_test"] = True
    return smoke


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    source = Path(args.project)
    output = Path(args.output)
    project = json.loads(source.read_text(encoding="utf-8"))
    smoke = build_smoke_project(project)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(smoke, indent=2), encoding="utf-8")
    frames = smoke["duration_seconds"] * smoke["fps"]
    print(
        f"SHORTFORGE_SMOKE_PROJECT_OK duration={smoke['duration_seconds']}s "
        f"frames={frames} resolution={smoke['width']}x{smoke['height']}"
    )


if __name__ == "__main__":
    main()
