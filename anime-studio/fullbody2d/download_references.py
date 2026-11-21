#!/usr/bin/env python3
"""Download only creator-licensed Morevna anime visuals for temporary study.

Video-only yt-dlp format selection intentionally excludes the separately licensed
soundtracks. Downloads stay outside the repository and are never put in releases.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SOURCES = [
    {
        "key": "morevna-demo",
        "url": "https://www.youtube.com/watch?v=PThy9_RZQ8c",
        "title": "The Beautiful Queen Marya Morevna: Demo [HD version]",
        "creator": "Konstantin Dmitriev / Morevna Project",
        "visual_license": "CC BY 3.0",
        "required_description_text": "all visual footage of the demo are provided under the terms of creativecommons attribution 3.0",
        "credit": "Animation by Morevna Project",
        "license_url": "https://creativecommons.org/licenses/by/3.0/",
    },
    {
        "key": "morevna-episode-3",
        "url": "https://www.youtube.com/watch?v=ecVv2IB7f5k",
        "title": "Morevna Episode 3.0.2 (English)",
        "creator": "Morevna Project",
        "visual_license": "CC BY-SA 4.0",
        "required_description_text": "license: creative commons attribution-sharealike 4.0",
        "credit": "Morevna Project",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
    },
]


def run(command: list[str]) -> str:
    completed = subprocess.run(command, check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    manifest = []

    for source in SOURCES:
        metadata_text = run([
            sys.executable, "-m", "yt_dlp", "--no-warnings", "--no-playlist",
            "--dump-single-json", source["url"]
        ])
        metadata = json.loads(metadata_text)
        description = (metadata.get("description") or "").lower()
        expected = source["required_description_text"].lower()
        if expected not in description:
            raise SystemExit(
                f"Refusing {source['key']}: the expected visual licence declaration "
                "was not found in the current creator description."
            )

        target = output / source["key"]
        target.mkdir(parents=True, exist_ok=True)
        run([
            sys.executable, "-m", "yt_dlp", "--no-warnings", "--no-playlist",
            "--format", "bv[height<=1080]/bv",
            "--remux-video", "mp4",
            "--output", str(target / "source.%(ext)s"),
            source["url"],
        ])
        candidates = [p for p in target.glob("source.*") if p.suffix.lower() in {".mp4", ".mkv", ".webm", ".mov"}]
        if not candidates:
            raise SystemExit(f"No video-only download was produced for {source['key']}.")
        video = candidates[0]
        audio_streams = run([
            "ffprobe", "-v", "error", "-select_streams", "a",
            "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(video)
        ])
        if audio_streams:
            raise SystemExit(f"Unexpected audio stream in {video}; deleting it and failing.")
        (target / "creator-metadata.json").write_text(
            json.dumps(metadata, indent=2), encoding="utf-8"
        )
        manifest.append({
            **source,
            "downloaded_file": str(video),
            "video_only": True,
            "audio_downloaded": False,
            "license_description_verified": True,
        })

    (output / "reference-attribution.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print("Verified and downloaded video-only Morevna reference files:")
    for item in manifest:
        print(f"- {item['title']} — {item['visual_license']} — {item['downloaded_file']}")


if __name__ == "__main__":
    main()
