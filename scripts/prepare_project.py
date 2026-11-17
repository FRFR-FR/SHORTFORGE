#!/usr/bin/env python3
"""Create a run-specific SHORTFORGE project from a quality profile or authored config."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--quality", choices=["smoke", "preview", "master", "one-minute"])
    source.add_argument("--project", help="Path to a complete authored project JSON, relative to repository root")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    if args.project:
        source_path = Path(args.project)
        if not source_path.is_absolute():
            source_path = ROOT / source_path
        if not source_path.is_file():
            raise SystemExit(f"Project config does not exist: {source_path}")
        config = json.loads(source_path.read_text(encoding="utf-8"))
        config.setdefault("quality", "custom")
    else:
        source_name = "one-minute.json" if args.quality == "one-minute" else (
            "smoke.json" if args.quality == "smoke" else "template.json"
        )
        config = json.loads((ROOT / "config" / source_name).read_text(encoding="utf-8"))
        config["quality"] = args.quality
        if args.quality == "smoke":
            config.update({"duration_seconds": 10, "width": 540, "height": 960})
            config["render"].update({"crf": 19, "preset": "veryfast", "samples": 24})
        elif args.quality == "preview":
            config.update({"duration_seconds": 30, "width": 720, "height": 1280})
            config["render"].update({"crf": 17, "preset": "fast", "samples": 64})
        elif args.quality == "master":
            config.update({"duration_seconds": 30, "width": 1080, "height": 1920})
            config["render"].update({"crf": 16, "preset": "medium", "samples": 96})
        else:
            config.update({"duration_seconds": 60, "width": 720, "height": 1280})
            config["render"].update({"crf": 16, "preset": "medium", "samples": 64})

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(config, indent=2), encoding="utf-8")
    print(f"Prepared {config.get('quality', 'custom')} project: {output}")


if __name__ == "__main__":
    main()
