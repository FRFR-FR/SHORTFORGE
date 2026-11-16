"""Analyze every output frame and create a compact contact sheet + JSON report."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from statistics import mean

from PIL import Image, ImageDraw, ImageStat


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames-dir", required=True)
    parser.add_argument("--expected-frames", required=True, type=int)
    parser.add_argument("--width", required=True, type=int)
    parser.add_argument("--height", required=True, type=int)
    parser.add_argument("--report", required=True)
    parser.add_argument("--contact-sheet", required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    frames_dir = Path(args.frames_dir)
    frames = sorted(frames_dir.glob("frame_*.png"))
    errors = []
    warnings = []
    if len(frames) != args.expected_frames:
        errors.append(f"Expected {args.expected_frames} frames, found {len(frames)}")

    rows = []
    hashes = []
    black_frames = []
    white_frames = []
    low_variance_frames = []
    dimensions_ok = True
    for index, path in enumerate(frames, start=1):
        with Image.open(path) as source:
            image = source.convert("RGB")
            if image.size != (args.width, args.height):
                dimensions_ok = False
                errors.append(f"Frame {index} dimensions {image.size} != {(args.width, args.height)}")
            stat = ImageStat.Stat(image.resize((min(160, image.width), min(160, image.height))))
            channel_means = stat.mean
            luminance = 0.2126 * channel_means[0] + 0.7152 * channel_means[1] + 0.0722 * channel_means[2]
            variance = mean(stat.var)
            digest = hashlib.sha1(image.tobytes()).hexdigest()
            hashes.append(digest)
            rows.append({"frame": index, "mean_luminance": round(luminance, 2), "mean_channel_variance": round(variance, 2)})
            if luminance < 2.0:
                black_frames.append(index)
            if luminance > 253.0:
                white_frames.append(index)
            if variance < 1.2:
                low_variance_frames.append(index)

    # Flag long freezes, not isolated repeated frames caused by brief holds.
    longest_duplicate_run = 1 if hashes else 0
    current_run = 1
    for previous, current in zip(hashes, hashes[1:]):
        if current == previous:
            current_run += 1
            longest_duplicate_run = max(longest_duplicate_run, current_run)
        else:
            current_run = 1

    if black_frames:
        errors.append(f"Black/near-black frames detected: {black_frames[:20]}")
    if white_frames:
        errors.append(f"White/near-white frames detected: {white_frames[:20]}")
    if longest_duplicate_run >= 12:
        errors.append(f"Possible frozen video: {longest_duplicate_run} identical consecutive frames")
    if low_variance_frames and len(low_variance_frames) > max(3, len(frames) // 20):
        warnings.append(f"Low-detail frames: {len(low_variance_frames)}")
    if not dimensions_ok:
        errors.append("One or more frames have incorrect dimensions")

    # Sample across the whole clip for the visual contact sheet.
    sample_count = min(16, len(frames))
    sample_indices = sorted(set(round(i * (len(frames) - 1) / max(1, sample_count - 1)) for i in range(sample_count))) if frames else []
    thumb_w = 180
    thumb_h = max(1, round(thumb_w * args.height / args.width))
    label_h = 24
    cols = 4
    rows_count = max(1, (len(sample_indices) + cols - 1) // cols)
    sheet = Image.new("RGB", (cols * thumb_w, rows_count * (thumb_h + label_h)), (24, 28, 34))
    draw = ImageDraw.Draw(sheet)
    for position, frame_index in enumerate(sample_indices):
        with Image.open(frames[frame_index]) as source:
            thumb = source.convert("RGB")
            thumb.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            x = (position % cols) * thumb_w
            y = (position // cols) * (thumb_h + label_h)
            sheet.paste(thumb, (x, y))
            draw.text((x + 6, y + thumb_h + 4), f"Frame {frame_index + 1}", fill=(245, 245, 245))
    Path(args.contact_sheet).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.contact_sheet, quality=88)

    report = {
        "status": "passed" if not errors else "failed",
        "expected_frames": args.expected_frames,
        "rendered_frames": len(frames),
        "dimensions": [args.width, args.height],
        "frames_analyzed": len(rows),
        "longest_identical_frame_run": longest_duplicate_run,
        "black_frames": black_frames,
        "white_frames": white_frames,
        "low_variance_frames": low_variance_frames,
        "warnings": warnings,
        "errors": errors,
        "per_frame_metrics": rows,
        "note": "Pixel heuristics do not replace a human visual/story/continuity review.",
    }
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["status", "rendered_frames", "dimensions", "errors", "warnings"]}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
