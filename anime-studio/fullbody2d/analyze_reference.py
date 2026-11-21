#!/usr/bin/env python3
"""Extract an abstract colour/contrast guide from openly licensed anime references.

No source frame is copied into the generated animation. Only numeric palette and
image-statistics measurements are written. This is used to inform original art
direction, not to trace compositions, characters or shots.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from PIL import Image, ImageStat


def rgb_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def analyse(paths: list[Path]) -> dict:
    bins: Counter[tuple[int, int, int]] = Counter()
    means = []
    contrasts = []
    image_count = 0

    for path in paths:
        with Image.open(path).convert("RGB") as image:
            image.thumbnail((480, 320))
            stats = ImageStat.Stat(image)
            means.append(round(sum(stats.mean) / 3.0, 2))
            contrasts.append(round(sum(stats.stddev) / 3.0, 2))
            image_count += 1

            for r, g, b in image.resize((240, 160)).getdata():
                # Exclude near-monochrome and very dark/bright extremes so the
                # accent set reflects designed colour, not black borders.
                if max(r, g, b) - min(r, g, b) < 38:
                    continue
                if (r + g + b) / 3 < 36 or (r + g + b) / 3 > 236:
                    continue
                # 5-bit buckets suppress tiny pixel/noise variations.
                bins[(r >> 3, g >> 3, b >> 3)] += 1

    ranked = []
    for (r, g, b), count in bins.most_common(80):
        color = (r * 8 + 4, g * 8 + 4, b * 8 + 4)
        # Greedy colour distance makes palette entries visually distinct.
        if all(sum((color[i] - prev[i]) ** 2 for i in range(3)) >= 58 ** 2 for prev in ranked):
            ranked.append(color)
        if len(ranked) >= 6:
            break

    if not ranked:
        ranked = [(63, 227, 240), (255, 85, 152), (239, 193, 130), (116, 111, 202)]
    while len(ranked) < 2:
        ranked.append((255, 85, 152) if len(ranked) == 1 else (63, 227, 240))

    return {
        "method": "sampled contact-sheet palette and luminance/contrast statistics",
        "source_frames_used": image_count,
        "accent_colors": [rgb_hex(c) for c in ranked[:4]],
        "mean_luminance_samples": means,
        "contrast_samples": contrasts,
        "guidance": [
            "Use the measured colour relationships as original palette guidance only.",
            "Do not reproduce reference characters, costumes, props, layouts or shot composition.",
            "Keep each rendered character's own silhouette, face, outfit and asset design original."
        ]
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--images", nargs="+", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    paths = [Path(value) for value in args.images]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise SystemExit("Missing reference contact sheets: " + ", ".join(missing))
    report = analyse(paths)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
