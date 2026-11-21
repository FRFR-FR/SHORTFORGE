#!/usr/bin/env python3
"""Fetch only SHORTFORGE's two rigged CC0 humanoid source models for the debate.

Unlike the standard SHORTFORGE renderer this job does not download a 200–300 MB
Blender splash environment: the debate builds its own location-specific sets.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from fetch_assets import AVATARS, fetch_avatar


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", default=".cache/shortforge-assets")
    parser.add_argument("--output-manifest", required=True)
    args = parser.parse_args()
    cache = Path(args.cache_dir).resolve()
    output = Path(args.output_manifest).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    avatars = {gender: fetch_avatar(gender, info, cache) for gender, info in AVATARS.items()}
    manifest = {
        "source": "Quaternius Universal Base Characters Standard",
        "license": "CC0-1.0",
        "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
        "avatar_system": "SHORTFORGE 65-joint rig; PBR textures retained; 7 expression states and 8 pose presets",
        "avatars": avatars,
    }
    output.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({k: {"bytes": v["bytes"], "sha256": v["sha256"], "rig_joints": v["rig_joints"]}
                      for k, v in avatars.items()}, indent=2))


if __name__ == "__main__":
    main()
