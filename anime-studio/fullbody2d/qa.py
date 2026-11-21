#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageStat


def probe(path: Path) -> dict:
    result = subprocess.run([
        "ffprobe", "-v", "error", "-count_frames",
        "-show_entries", "stream=codec_name,codec_type,width,height,avg_frame_rate,nb_read_frames,pix_fmt",
        "-show_entries", "format=duration,size",
        "-of", "json", str(path)
    ], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--frames-dir", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    video = Path(args.video)
    frames_dir = Path(args.frames_dir)
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    data = probe(video)
    streams = data.get("streams", [])
    video_streams = [s for s in streams if s.get("codec_type") == "video"]
    audio_streams = [s for s in streams if s.get("codec_type") == "audio"]
    errors = []
    if len(video_streams) != 1:
        errors.append("Expected exactly one video stream.")
    if audio_streams:
        errors.append("The reference sample must contain no audio streams.")
    stream = video_streams[0] if len(video_streams) == 1 else {}

    expected_frames = int(manifest["frames"])
    actual_frames = int(stream.get("nb_read_frames") or 0)
    fps = stream.get("avg_frame_rate", "0/1")
    duration = float(data.get("format", {}).get("duration", 0.0))
    width, height = manifest["resolution"]
    frame_files = sorted(frames_dir.glob("frame_*.png"))
    required_anatomy = {
        "skull and jaw", "eyes and eyelids", "nose", "mouth", "neck",
        "shoulders", "ribcage", "pelvis", "hands", "fingers",
        "thighs", "knees", "calves", "feet", "boots"
    }
    character = manifest.get("character", {})
    anatomy = set(character.get("anatomy_parts", []))
    if not required_anatomy.issubset(anatomy):
        errors.append("Manifest is missing required full-body anatomy design elements.")
    if character.get("rendering", "").count("full colour") == 0:
        errors.append("Character must be full-colour and shaded, not line-only.")
    if manifest.get("stage") != "2D canvas only":
        errors.append("The final stage must be a 2D canvas.")
    if int(manifest.get("character_count", 0)) < 2:
        errors.append("At least two fully designed human characters are required.")
    if manifest.get("audio") != "none":
        errors.append("This reference test must not add soundtrack audio.")
    if manifest.get("reference_video_frames_in_final_output") is not False:
        errors.append("Reference footage must not appear in the released animation.")

    if stream.get("codec_name") != "h264":
        errors.append("Expected H.264 video.")
    if (stream.get("width"), stream.get("height")) != (width, height):
        errors.append("Incorrect output dimensions.")
    if actual_frames != expected_frames:
        errors.append(f"Expected {expected_frames} frames, got {actual_frames}.")
    if fps != f"{manifest['fps']}/1":
        errors.append(f"Expected {manifest['fps']} fps, got {fps}.")
    if abs(duration - float(manifest["seconds"])) > 0.15:
        errors.append(f"Incorrect duration: {duration:.3f}s.")
    if len(frame_files) != expected_frames:
        errors.append(f"Expected {expected_frames} rendered PNGs, got {len(frame_files)}.")

    brightness = []
    contrast = []
    for index in {0, max(0, len(frame_files)//3), max(0, 2*len(frame_files)//3), max(0, len(frame_files)-1)}:
        if not frame_files:
            break
        with Image.open(frame_files[index]).convert("RGB") as image:
            if image.size != (width, height):
                errors.append(f"Bad source frame dimensions in {frame_files[index].name}.")
            stats = ImageStat.Stat(image)
            means = sum(stats.mean) / 3.0
            std = sum(stats.stddev) / 3.0
            brightness.append(round(means, 2))
            contrast.append(round(std, 2))
            if means < 8 or means > 246 or std < 12:
                errors.append(f"Blank/near-flat image detected at {frame_files[index].name}.")

    # The beginning and action/recovery sample must not be identical.
    if len(frame_files) >= 3:
        with Image.open(frame_files[0]).convert("RGB") as first, Image.open(frame_files[-1]).convert("RGB") as last:
            diff = ImageChops.difference(first, last)
            motion_score = round(sum(ImageStat.Stat(diff).mean) / 3.0, 3)
            if motion_score < 1.0:
                errors.append("The opening and ending frames are too similar; visible animation motion is required.")
    else:
        motion_score = 0.0
        errors.append("Insufficient frames to verify motion.")

    report = {
        "status": "failed" if errors else "passed",
        "video": str(video.resolve()),
        "file_size_bytes": os.path.getsize(video),
        "codec": stream.get("codec_name"),
        "resolution": [stream.get("width"), stream.get("height")],
        "fps": fps,
        "frames": actual_frames,
        "duration_seconds": round(duration, 3),
        "source_png_frames": len(frame_files),
        "sample_brightness": brightness,
        "sample_contrast": contrast,
        "sampled_frame_difference_score": motion_score,
        "full_body_anatomy_manifest": sorted(anatomy),
        "stage": manifest.get("stage"),
        "errors": errors,
    }
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
