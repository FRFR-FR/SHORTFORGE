#!/usr/bin/env python3
"""Measure high-level visual signals in a locally authorised video.

Writes numeric CSV/JSON only. No extracted frames, audio, transcripts, or
reconstructed shot sequences are retained.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
from statistics import mean, median
import cv2
import numpy as np


def dist(values):
    values = [float(v) for v in values if v is not None and math.isfinite(float(v))]
    if not values:
        return {"median": None, "p90": None, "p95": None, "mean": None}
    return {
        "median": round(median(values), 4),
        "p90": round(float(np.percentile(values, 90)), 4),
        "p95": round(float(np.percentile(values, 95)), 4),
        "mean": round(mean(values), 4),
    }


def camera_proxy(prev, curr, source_scale):
    points = cv2.goodFeaturesToTrack(prev, maxCorners=250, qualityLevel=0.01,
                                     minDistance=7, blockSize=7)
    if points is None or len(points) < 8:
        return None, None, None, 0.0
    moved, status, _ = cv2.calcOpticalFlowPyrLK(
        prev, curr, points, None, winSize=(21, 21), maxLevel=3,
        criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))
    if moved is None or status is None:
        return None, None, None, 0.0
    valid = status.reshape(-1) == 1
    old, new = points[valid], moved[valid]
    if len(old) < 8:
        return None, None, None, 0.0
    matrix, inliers = cv2.estimateAffinePartial2D(
        old, new, method=cv2.RANSAC, ransacReprojThreshold=2.5)
    if matrix is None:
        return None, None, None, 0.0
    a, b = float(matrix[0, 0]), float(matrix[1, 0])
    scale = math.sqrt(a * a + b * b)
    rotation = math.degrees(math.atan2(b, a))
    dx = float(matrix[0, 2]) * source_scale
    dy = float(matrix[1, 2]) * source_scale
    confidence = float(np.mean(inliers)) if inliers is not None else 0.0
    return math.hypot(dx, dy), (scale - 1.0) * 100.0, rotation, confidence


def analyze(video: Path, out_dir: Path, analysis_width: int = 360):
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video}")
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    declared = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if fps <= 0 or width <= 0 or height <= 0:
        cap.release()
        raise RuntimeError("Video fps/dimensions are unavailable")
    scale = min(1.0, analysis_width / float(width))
    w, h = max(2, int(width * scale)), max(2, int(height * scale))
    source_scale = width / float(w)
    rows, cuts = [], []
    prev_gray = prev_hist = None
    frame_no = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame_no += 1
        small = cv2.resize(frame, (w, h), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
        edges = cv2.Canny(gray, 70, 150)
        hist = cv2.calcHist([gray], [0], None, [32], [0, 256])
        cv2.normalize(hist, hist, alpha=1.0, norm_type=cv2.NORM_L1)

        camera_px = zoom_pct = roll_deg = confidence = None
        flow_mean = flow_p95 = cut_score = None
        if prev_gray is not None:
            camera_px, zoom_pct, roll_deg, confidence = camera_proxy(
                prev_gray, gray, source_scale)
            flow = cv2.calcOpticalFlowFarneback(
                prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            magnitude = cv2.magnitude(flow[:, :, 0], flow[:, :, 1]) * source_scale
            flow_mean = float(np.mean(magnitude))
            flow_p95 = float(np.percentile(magnitude, 95))
            cut_score = float(cv2.compareHist(
                prev_hist, hist, cv2.HISTCMP_BHATTACHARYYA))
            if cut_score >= 0.55 and frame_no > 2:
                cuts.append(frame_no)

        rows.append({
            "frame": frame_no,
            "time_seconds": round((frame_no - 1) / fps, 5),
            "camera_translation_px_proxy": camera_px,
            "camera_zoom_percent_proxy": zoom_pct,
            "camera_roll_degrees_proxy": roll_deg,
            "camera_estimate_confidence": confidence,
            "optical_flow_mean_px": flow_mean,
            "optical_flow_p95_px": flow_p95,
            "scene_change_score": cut_score,
            "edge_density_percent": round(np.count_nonzero(edges) / edges.size * 100, 5),
            "mean_luminance_0_255": round(float(np.mean(gray)), 4),
            "mean_saturation_0_255": round(float(np.mean(hsv[:, :, 1])), 4),
            "sharpness_laplacian_variance": round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 4),
        })
        prev_gray, prev_hist = gray, hist
    cap.release()
    if not rows:
        raise RuntimeError("No frames could be decoded")

    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / f"{video.stem}.frames.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    metric_keys = [
        "camera_translation_px_proxy", "camera_zoom_percent_proxy",
        "camera_roll_degrees_proxy", "camera_estimate_confidence",
        "optical_flow_mean_px", "optical_flow_p95_px", "edge_density_percent",
        "mean_luminance_0_255", "mean_saturation_0_255",
        "sharpness_laplacian_variance",
    ]
    metrics = {key: dist([r[key] for r in rows]) for key in metric_keys}
    duration = len(rows) / fps
    summary = {
        "source_id": video.stem,
        "source_video_retained": False,
        "analysis_resolution": [w, h],
        "source_dimensions": [width, height],
        "fps": round(fps, 5),
        "duration_seconds": round(duration, 4),
        "declared_frames": declared,
        "decoded_frames": len(rows),
        "detected_cut_threshold": 0.55,
        "detected_cut_frames": cuts,
        "detected_cut_times_seconds": [round((n - 1) / fps, 4) for n in cuts],
        "estimated_shot_count": len(cuts) + 1,
        "estimated_average_shot_seconds": round(duration / (len(cuts) + 1), 4),
        "metrics": metrics,
        "limitations": [
            "Global affine camera movement is a proxy; subject motion, parallax and cuts can confound it.",
            "Optical flow measures all visible pixel movement, not camera movement alone.",
            "Edge density is not outline thickness or a direct art-style measurement.",
            "Histogram cuts can miss subtle edits or flag flashes.",
            "Metrics are quality indicators, not instructions to reproduce distinctive expression."
        ],
        "per_frame_csv": csv_path.name,
    }
    summary_path = out_dir / f"{video.stem}.summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--video", required=True, type=Path)
    p.add_argument("--output-dir", required=True, type=Path)
    p.add_argument("--analysis-width", type=int, default=360)
    a = p.parse_args()
    print(json.dumps(analyze(a.video, a.output_dir, a.analysis_width), indent=2))


if __name__ == "__main__":
    main()
