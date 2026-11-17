#!/usr/bin/env python3
"""Rank public channel uploads; optionally measure videos with explicit rights."""
from __future__ import annotations
import argparse
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import yt_dlp

ROOT = Path(__file__).resolve().parents[1]
RIGHTS_PHRASE = (
    "I own or have written permission to download and analyze every selected video, "
    "and this use is permitted by the platform terms."
)


def clean_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "_", value or "unknown")[:80]


def extract_channel(url: str, limit: int) -> dict[str, Any]:
    opts = {
        "quiet": True, "no_warnings": True, "skip_download": True,
        "extract_flat": False, "ignoreerrors": True,
        "playlistend": limit, "noplaylist": False,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    if not info:
        raise RuntimeError("yt-dlp could not retrieve channel metadata")
    entries = [x for x in (info.get("entries") or []) if isinstance(x, dict) and x.get("id")]
    if not entries and info.get("id"):
        entries = [info]
    return {"info": info, "entries": entries}


def compact(entry: dict, rank: int) -> dict:
    return {
        "rank_by_views": rank,
        "id": entry.get("id"),
        "title": entry.get("title"),
        "url": entry.get("webpage_url") or entry.get("original_url"),
        "view_count": entry.get("view_count"),
        "like_count": entry.get("like_count"),
        "duration_seconds": entry.get("duration"),
        "upload_date": entry.get("upload_date"),
        "channel": entry.get("channel") or entry.get("uploader"),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--channel-url", default="https://www.youtube.com/@ricksclips3000/videos")
    p.add_argument("--top-n", type=int, default=20)
    p.add_argument("--max-candidates", type=int, default=300)
    p.add_argument("--output-dir", type=Path, default=ROOT / "out/reference-lab")
    p.add_argument("--download-and-analyze", action="store_true")
    p.add_argument("--rights-attestation", default="")
    a = p.parse_args()
    if a.top_n < 1 or a.max_candidates < a.top_n:
        p.error("--top-n must be positive and --max-candidates must be >= --top-n")
    if a.download_and_analyze and RIGHTS_PHRASE not in a.rights_attestation:
        p.error("Downloads require the exact written-rights and platform-permission attestation.")
    a.output_dir.mkdir(parents=True, exist_ok=True)

    result = extract_channel(a.channel_url, a.max_candidates)
    entries = sorted(result["entries"],
                     key=lambda e: int(e.get("view_count") or -1), reverse=True)
    chosen = entries[:a.top_n]
    if not chosen:
        raise RuntimeError("No accessible channel videos were returned")
    info = result["info"]
    metadata = {
        "channel_title": info.get("title"),
        "channel_id": info.get("id"),
        "channel_url": a.channel_url,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "candidates_returned": len(entries),
        "selected_count": len(chosen),
        "ranking": "view_count descending among returned accessible uploads",
        "snapshot_note": "View counts/rankings change; this is a dated snapshot.",
        "download_enabled": bool(a.download_and_analyze),
        "frame_analysis_performed": False,
        "selected_videos": [compact(e, i + 1) for i, e in enumerate(chosen)],
    }
    metadata_path = a.output_dir / "top20-metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    summaries = []
    metrics_dir = a.output_dir / "frame-metrics"

    if a.download_and_analyze:
        metrics_dir.mkdir(exist_ok=True)
        analyzer = ROOT / "src/qa/analyze_reference_video.py"
        # Source media is confined to temporary storage and deleted after analysis.
        with tempfile.TemporaryDirectory(prefix="shortforge-reference-") as temp:
            for rank, entry in enumerate(chosen, start=1):
                url = entry.get("webpage_url") or entry.get("original_url")
                if not url and entry.get("id"):
                    url = f"https://www.youtube.com/watch?v={entry['id']}"
                if not url:
                    continue
                vid = clean_id(str(entry["id"]))
                opts = {
                    "quiet": True, "no_warnings": True, "noplaylist": True,
                    "format": "bv*[height<=1080]+ba/b[height<=1080]/b",
                    "merge_output_format": "mp4",
                    "outtmpl": str(Path(temp) / f"{vid}.%(ext)s"),
                    "retries": 3, "fragment_retries": 3,
                }
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url])
                found = next((x for x in Path(temp).glob(f"{vid}.*")
                              if x.suffix.lower() in {".mp4", ".mkv", ".webm", ".mov"}), None)
                if found is None:
                    print(f"SKIP {vid}: no merged video file found")
                    continue
                subprocess.run([
                    shutil.which("python") or "python", str(analyzer),
                    "--video", str(found), "--output-dir", str(metrics_dir)
                ], check=True)
                summary_path = metrics_dir / f"{vid}.summary.json"
                if summary_path.exists():
                    s = json.loads(summary_path.read_text(encoding="utf-8"))
                    s["channel_view_rank"] = rank
                    s["title"] = entry.get("title")
                    summary_path.write_text(json.dumps(s, indent=2), encoding="utf-8")
                    summaries.append(s)
                found.unlink(missing_ok=True)

    metadata["frame_analysis_performed"] = bool(summaries)
    metadata["analyzed_video_count"] = len(summaries)
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    metric_names = [
        "camera_translation_px_proxy", "camera_zoom_percent_proxy",
        "camera_roll_degrees_proxy", "optical_flow_mean_px",
        "optical_flow_p95_px", "edge_density_percent",
        "mean_luminance_0_255", "mean_saturation_0_255",
        "sharpness_laplacian_variance",
    ]
    aggregate = {}
    for key in metric_names:
        vals = sorted(float(s["metrics"][key]["median"]) for s in summaries
                      if s.get("metrics", {}).get(key, {}).get("median") is not None)
        if vals:
            aggregate[key] = {
                "video_medians_count": len(vals),
                "median_of_video_medians": vals[len(vals) // 2],
                "minimum": vals[0], "maximum": vals[-1],
            }
    report = {
        "channel_title": info.get("title"),
        "channel_url": a.channel_url,
        "frame_analysis_performed": bool(summaries),
        "analyzed_video_count": len(summaries),
        "aggregate_metrics": aggregate,
        "per_video_summaries": [s.get("source_id") for s in summaries],
        "originality_boundary": "Use aggregate technical patterns only; create original scripts, dialogue, characters, art, props, shots, branding and audio.",
        "limitations": [
            "Unavailable, private, deleted, age-restricted or blocked videos may not be returned.",
            "Top-ranked means most views in the accessible candidate set, not guaranteed all-time completeness.",
            "Computer-vision values are proxies and cannot quantify artistic quality by themselves.",
            "No source MP4, extracted frame, audio, caption or transcript is retained."
        ],
    }
    summary_path = a.output_dir / "analysis-summary.json"
    summary_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    zip_path = a.output_dir / "research-results.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(metadata_path, metadata_path.name)
        z.write(summary_path, summary_path.name)
        if a.download_and_analyze:
            for f in sorted(metrics_dir.glob("*")):
                if f.is_file():
                    z.write(f, f"frame-metrics/{f.name}")
    print(json.dumps({
        "channel": info.get("title"), "candidates": len(entries),
        "selected": len(chosen), "frame_analysis_performed": bool(summaries),
        "analyzed": len(summaries), "report": str(summary_path),
        "archive": str(zip_path),
    }, indent=2))


if __name__ == "__main__":
    main()
