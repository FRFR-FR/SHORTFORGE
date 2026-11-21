#!/usr/bin/env python3
"""Fetch openly licensed anime references with yt-dlp, then remove soundtrack.

The source videos are direct Wikimedia Commons files. YouTube is intentionally
not used because anonymous GitHub runners are now challenged by YouTube. yt-dlp
downloads the direct source URLs; ffmpeg immediately creates video-only files.
Original muxed source files are deleted before reference frame sampling.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

SOURCES = [
    {
        "key": "morevna-episode-3",
        "title": "Morevna Episode 3.0.2 (English)",
        "url": "https://upload.wikimedia.org/wikipedia/commons/a/a7/Morevna_Episode_3.0.2_%28English%29.webm",
        "page": "https://commons.wikimedia.org/wiki/File:Morevna_Episode_3.0.2_(English).webm",
        "creator": "Morevna Project",
        "visual_license": "CC BY-SA 4.0 (conservatively recorded using the creator's own licence declaration)",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "sha1": "9eb7961b8cfa7e48b47163a99590ab5677ea248a",
        "attribution": "Animation by Morevna Project. Source soundtrack not used.",
        "notes": "Futuristic anime series, 10 min 18 sec, 1920x1080 WebM. Wikimedia Commons current file page lists CC BY 4.0; the creator's own description and official project page state CC BY-SA 4.0. This manifest conservatively follows the more restrictive creator-stated CC BY-SA terms.",
    },
    {
        "key": "peppercarrot-episode-6",
        "title": "Pepper & Carrot Motion Comic — Episode 6: The Potion Contest",
        "url": "https://upload.wikimedia.org/wikipedia/commons/7/79/Morevna_Project_-_Pepper%26Carrot_%28animated_comic%29_-_Episode_6_-_The_Potion_Contest.webm",
        "page": "https://commons.wikimedia.org/wiki/File:Morevna_Project_-_Pepper%26Carrot_(animated_comic)_-_Episode_6_-_The_Potion_Contest.webm",
        "creator": "Morevna Project; Gregoire Lourme; David Revoy",
        "visual_license": "CC BY-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "sha1": "165c1cfbbfc5983e1cbdfc93fcf3b8f5a8d258d0",
        "attribution": "Animation: Morevna Project; Music: Gregoire Lourme (not used); Illustrations: David Revoy.",
        "notes": "Animated motion comic, 7 min 35 sec, 1920x1080 WebM. Its Commons page records a VRT permission confirmation for the CC BY-SA 4.0 licence. The soundtrack is stripped before sampling.",
    },
]


def run(command: list[str]) -> str:
    try:
        completed = subprocess.run(command, check=True, text=True, capture_output=True)
    except subprocess.CalledProcessError as error:
        if error.stderr:
            print(error.stderr, file=sys.stderr)
        raise
    return completed.stdout.strip()


def sha1(path: Path) -> str:
    digest = hashlib.sha1()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe_audio(path: Path) -> bool:
    result = run([
        "ffprobe", "-v", "error", "-select_streams", "a",
        "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(path)
    ])
    return bool(result.strip())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    manifest = []

    for source in SOURCES:
        target = output / source["key"]
        target.mkdir(parents=True, exist_ok=True)
        clean = target / "reference-video-only.webm"

        # yt-dlp is deliberately used on the direct Commons file, not on YouTube.
        run([
            sys.executable, "-m", "yt_dlp", "--force-generic-extractor",
            "--no-warnings", "--no-playlist", "--no-progress",
            "--output", str(target / "source-original.%(ext)s"), source["url"],
        ])
        candidates = [item for item in target.glob("source-original.*") if item.is_file()]
        if len(candidates) != 1 or candidates[0].stat().st_size == 0:
            raise SystemExit(f"yt-dlp did not produce exactly one source file for {source['key']}.")
        raw = candidates[0]

        actual_sha1 = sha1(raw)
        if actual_sha1.lower() != source["sha1"].lower():
            raise SystemExit(
                f"SHA-1 mismatch for {source['key']}: expected {source['sha1']}, got {actual_sha1}. "
                "Refusing an unverified or changed source."
            )

        # Keep only the visual stream. The muxed source is deleted immediately.
        run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(raw), "-map", "0:v:0", "-c:v", "copy", "-an",
            str(clean),
        ])
        if probe_audio(clean):
            clean.unlink(missing_ok=True)
            raise SystemExit(f"Audio remains in video-only reference {clean}; refusing to continue.")
        raw.unlink()

        manifest.append({
            **source,
            "downloaded_file": str(clean),
            "source_sha1_verified": actual_sha1,
            "source_audio_stripped": True,
            "video_only_reference_verified": True,
            "original_muxed_file_deleted": True,
            "reference_video_in_final_render": False,
        })

    (output / "reference-attribution.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print("Downloaded and hash-verified licensed Morevna references with yt-dlp.")
    print("Source soundtracks were stripped before visual sampling.")
    for item in manifest:
        print(f"- {item['title']} — {item['visual_license']} — {item['downloaded_file']}")


if __name__ == "__main__":
    main()
