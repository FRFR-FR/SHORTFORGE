#!/usr/bin/env python3
"""Offline smoke test for the SHORTFORGE reference-frame analyzer."""
from __future__ import annotations
import csv
import tempfile
from pathlib import Path
import cv2
import numpy as np

from src.qa.analyze_reference_video import analyze


def main():
    with tempfile.TemporaryDirectory(prefix="shortforge-test-") as tmp:
        root = Path(tmp)
        video = root / "synthetic.mp4"
        writer = cv2.VideoWriter(
            str(video), cv2.VideoWriter_fourcc(*"mp4v"), 10.0, (180, 320)
        )
        if not writer.isOpened():
            raise RuntimeError("OpenCV could not create the synthetic MP4 test clip")
        yy, xx = np.indices((320, 180))
        for i in range(20):
            base = ((xx * 3 + yy * 2 + i * 4) % 220 + 20).astype(np.uint8)
            frame = np.dstack((base, np.roll(base, i, axis=1), np.roll(base, i, axis=0)))
            cv2.rectangle(frame, (12 + i, 24), (70 + i, 110), (20, 220, 245), -1)
            writer.write(frame)
        writer.release()

        out = root / "metrics"
        report = analyze(video, out, analysis_width=160)
        assert report["decoded_frames"] == 20, report
        assert report["source_video_retained"] is False
        assert report["fps"] == 10.0
        csv_file = out / "synthetic.frames.csv"
        assert csv_file.is_file()
        with csv_file.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        assert len(rows) == 20
        required = {
            "camera_translation_px_proxy",
            "optical_flow_mean_px",
            "edge_density_percent",
            "mean_luminance_0_255",
        }
        assert required.issubset(rows[0].keys())
        assert (out / "synthetic.summary.json").is_file()
        print("Reference analyzer smoke test passed: 20 frames measured.")


if __name__ == "__main__":
    main()
