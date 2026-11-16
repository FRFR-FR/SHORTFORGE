#!/usr/bin/env python3
"""Fail-fast validation for a SHORTFORGE project JSON."""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def validate(config: dict) -> list[str]:
    errors = []
    required = ["title", "duration_seconds", "fps", "width", "height", "render", "story", "character"]
    for key in required:
        if key not in config:
            errors.append(f"Missing required key: {key}")
    if errors:
        return errors
    if not isinstance(config["title"], str) or not config["title"].strip():
        errors.append("title must be a non-empty string")
    if not isinstance(config["duration_seconds"], int) or not 1 <= config["duration_seconds"] <= 180:
        errors.append("duration_seconds must be an integer between 1 and 180")
    if config["fps"] != 30:
        errors.append("fps must be exactly 30")
    width, height = config["width"], config["height"]
    if not isinstance(width, int) or not isinstance(height, int) or width < 180 or height < 320:
        errors.append("width/height must be integers of at least 180×320")
    elif width % 2 or height % 2:
        errors.append("width and height must be even for H.264 yuv420p")
    elif width * 16 != height * 9:
        errors.append("frame dimensions must be exactly 9:16 vertical")
    if not isinstance(config.get("render"), dict):
        errors.append("render must be an object")
    else:
        crf = config["render"].get("crf", 18)
        if not isinstance(crf, int) or not 14 <= crf <= 28:
            errors.append("render.crf must be an integer between 14 and 28")
    if not isinstance(config.get("story"), dict) or not isinstance(config["story"].get("beats"), list):
        errors.append("story.beats must be an array")
    shots = config.get("shots", [])
    if shots:
        if not isinstance(shots, list):
            errors.append("shots must be an array when supplied")
        else:
            profiles = {"wide", "push_in", "close", "side", "low"}
            expected_start = 0.0
            for index, shot in enumerate(shots):
                if not isinstance(shot, dict):
                    errors.append(f"shots[{index}] must be an object")
                    continue
                start = shot.get("start_seconds")
                duration = shot.get("duration_seconds")
                if not isinstance(start, (int, float)) or not isinstance(duration, (int, float)) or duration <= 0:
                    errors.append(f"shots[{index}] needs numeric start_seconds and positive duration_seconds")
                    continue
                if abs(float(start) - expected_start) > 0.001:
                    errors.append(f"shots[{index}] must start at {expected_start:g}s to avoid an uncovered/overlapped interval")
                if shot.get("camera", "wide") not in profiles:
                    errors.append(f"shots[{index}].camera must be one of {sorted(profiles)}")
                expected_start = float(start) + float(duration)
            if abs(expected_start - float(config["duration_seconds"])) > 0.001:
                errors.append("shots must cover the complete project duration")
    if not isinstance(config.get("character"), dict):
        errors.append("character must be an object")
    else:
        for color_key in ("primary_color", "accent_color"):
            value = config["character"].get(color_key)
            if value is not None and (not isinstance(value, list) or len(value) != 4 or any(not isinstance(x, (int, float)) or x < 0 or x > 1 for x in value)):
                errors.append(f"character.{color_key} must be four RGBA values between 0 and 1")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project")
    args = parser.parse_args()
    path = Path(args.project)
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"Unable to read project JSON: {exc}")
    errors = validate(config)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    frames = config["duration_seconds"] * config["fps"]
    print(f"SHORTFORGE project valid: {path}")
    print(f"Duration: {config['duration_seconds']} seconds | {frames} frames | {config['fps']} fps")
    print(f"Output: {config['width']}×{config['height']} (9:16)")


if __name__ == "__main__":
    main()
