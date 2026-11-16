#!/usr/bin/env python3
"""Render with Blender, run frame QA, encode with FFmpeg, and verify the MP4."""
from __future__ import annotations
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command, **kwargs):
    print("$", " ".join(str(x) for x in command), flush=True)
    subprocess.run(command, check=True, **kwargs)


def probe(path: Path) -> dict:
    output = subprocess.check_output([
        "ffprobe", "-v", "error", "-count_frames", "-show_entries",
        "stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,nb_read_frames",
        "-show_entries", "format=duration,size", "-of", "json", str(path)
    ], text=True)
    return json.loads(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--blender", default=os.environ.get("BLENDER_BIN", "blender"))
    parser.add_argument("--keep-frames", action="store_true")
    parser.add_argument("--save-blend", action="store_true")
    args = parser.parse_args()

    project_path = Path(args.project).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    validation = subprocess.run([sys.executable, str(ROOT / "scripts/validate_project.py"), str(project_path)])
    if validation.returncode:
        raise SystemExit(validation.returncode)
    config = json.loads(project_path.read_text(encoding="utf-8"))
    expected = int(config["duration_seconds"]) * int(config["fps"])
    width, height = int(config["width"]), int(config["height"])
    blender = shutil.which(args.blender)
    if not blender:
        raise SystemExit(f"Blender executable not found: {args.blender}")
    for executable in ("ffmpeg", "ffprobe"):
        if not shutil.which(executable):
            raise SystemExit(f"Required executable not found: {executable}")

    keep_dir = output_dir / "frames" if args.keep_frames else None
    if keep_dir:
        frames_dir = keep_dir
        frames_dir.mkdir(parents=True, exist_ok=True)
        temp_context = None
    else:
        temp_context = tempfile.TemporaryDirectory(prefix="shortforge-frames-")
        frames_dir = Path(temp_context.name) / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "qa-report.json"
    contact_path = output_dir / "contact-sheet.jpg"
    video_path = output_dir / "shortforge.mp4"
    blend_path = output_dir / "scene.blend" if args.save_blend else Path("")
    command = [blender, "--background", "--python", str(ROOT / "src/blender/render_scene.py"), "--",
               "--project", str(project_path), "--frames-dir", str(frames_dir)]
    if args.save_blend:
        command.extend(["--save-blend", str(blend_path)])
    env = os.environ.copy()
    env.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")
    env.setdefault("MESA_GL_VERSION_OVERRIDE", "4.5")
    run(command, env=env)

    run([sys.executable, str(ROOT / "src/qa/analyze_frames.py"),
         "--frames-dir", str(frames_dir), "--expected-frames", str(expected),
         "--width", str(width), "--height", str(height),
         "--report", str(report_path), "--contact-sheet", str(contact_path)])

    pattern = str(frames_dir / "frame_%06d.png")
    crf = str(config.get("render", {}).get("crf", 18))
    preset = str(config.get("render", {}).get("preset", "medium"))
    narration = config.get("narration_file", "")
    narration_path = Path(narration).resolve() if narration else None
    captions = config.get("captions_file", "")
    captions_path = Path(captions).resolve() if captions else None
    if narration_path and not narration_path.is_file():
        raise SystemExit(f"narration_file was configured but does not exist: {narration_path}")
    if captions_path and not captions_path.is_file():
        raise SystemExit(f"captions_file was configured but does not exist: {captions_path}")
    subtitle_filter = ["-vf", f"subtitles={captions_path}"] if captions_path else []
    if narration_path and narration_path.exists():
        run(["ffmpeg", "-hide_banner", "-y", "-framerate", str(config["fps"]), "-i", pattern,
             "-i", str(narration_path), "-map", "0:v:0", "-map", "1:a:0", *subtitle_filter, "-c:v", "libx264",
             "-preset", preset, "-crf", crf, "-pix_fmt", "yuv420p", "-r", str(config["fps"]),
             "-af", "apad", "-c:a", "aac", "-b:a", "192k", "-t", str(config["duration_seconds"]),
             "-movflags", "+faststart", str(video_path)])
    else:
        run(["ffmpeg", "-hide_banner", "-y", "-framerate", str(config["fps"]), "-i", pattern,
             *subtitle_filter, "-an", "-c:v", "libx264", "-preset", preset, "-crf", crf, "-pix_fmt", "yuv420p",
             "-r", str(config["fps"]), "-movflags", "+faststart", str(video_path)])

    media = probe(video_path)
    video_streams = [s for s in media.get("streams", []) if s.get("codec_type") == "video"]
    if not video_streams:
        raise SystemExit("ffprobe did not find a video stream")
    stream = video_streams[0]
    if (stream.get("width"), stream.get("height")) != (width, height):
        raise SystemExit(f"Encoded dimensions are incorrect: {stream.get('width')}×{stream.get('height')}")
    if stream.get("r_frame_rate") != "30/1":
        raise SystemExit(f"Encoded frame rate is not 30 fps: {stream.get('r_frame_rate')}")
    duration = float(media.get("format", {}).get("duration", 0))
    if abs(duration - config["duration_seconds"]) > 0.1:
        raise SystemExit(f"Encoded duration is incorrect: {duration:.3f}s")
    frame_count = int(stream.get("nb_read_frames", 0))
    if frame_count != expected:
        raise SystemExit(f"Encoded frame count is incorrect: expected {expected}, found {frame_count}")
    audio_streams = [s for s in media.get("streams", []) if s.get("codec_type") == "audio"]
    if narration_path and narration_path.exists() and not audio_streams:
        raise SystemExit("Narration file was configured but no audio stream was found in the MP4")
    if video_path.stat().st_size < 1000:
        raise SystemExit("Encoded MP4 is unexpectedly small")

    manifest = {
        "title": config["title"],
        "quality": config.get("quality", "custom"),
        "duration_seconds": config["duration_seconds"],
        "fps": config["fps"],
        "expected_frames": expected,
        "dimensions": [width, height],
        "video": video_path.name,
        "video_bytes": video_path.stat().st_size,
        "ffprobe": media,
        "qa_report": report_path.name,
        "contact_sheet": contact_path.name,
        "captions_burned_in": bool(captions_path),
        "narration_muxed": bool(narration_path),
        "render_engine": "Blender native renderer",
        "encoder": "FFmpeg libx264",
        "actions_artifacts_used": False
    }
    (output_dir / "render-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    if temp_context:
        temp_context.cleanup()
    print(f"SHORTFORGE_RENDER_OK {video_path}")


if __name__ == "__main__":
    main()
