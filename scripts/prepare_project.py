#!/usr/bin/env python3
"""Create a run-specific project config from one of the supported quality presets."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quality", choices=["smoke", "preview", "master"], required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    source = ROOT / ("config/smoke.json" if args.quality == "smoke" else "config/template.json")
    config = json.loads(source.read_text(encoding="utf-8"))
    config["quality"] = args.quality
    if args.quality == "smoke":
        config.update({"duration_seconds": 10, "width": 540, "height": 960})
        config["render"].update({"crf": 19, "preset": "veryfast", "samples": 24})
    elif args.quality == "preview":
        config.update({"duration_seconds": 30, "width": 720, "height": 1280})
        config["render"].update({"crf": 19, "preset": "fast", "samples": 48})
    else:
        config.update({"duration_seconds": 30, "width": 1080, "height": 1920})
        config["render"].update({"crf": 18, "preset": "medium", "samples": 64})
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(config, indent=2), encoding="utf-8")
    print(f"Prepared {args.quality} project: {output}")


if __name__ == "__main__":
    main()
