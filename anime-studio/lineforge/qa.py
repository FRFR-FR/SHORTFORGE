#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys

def probe(path):
    result = subprocess.run([
        "ffprobe", "-v", "error", "-count_frames",
        "-show_entries", "stream=codec_name,codec_type,width,height,r_frame_rate,avg_frame_rate,nb_read_frames,pix_fmt",
        "-show_entries", "format=duration,size",
        "-of", "json", path
    ], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    with open(args.manifest, encoding="utf-8") as handle:
        manifest = json.load(handle)
    data = probe(args.video)
    streams = [s for s in data.get("streams", []) if s.get("codec_type") == "video"]
    errors = []
    if len(streams) != 1:
        errors.append("Expected exactly one video stream.")
        video = {}
    else:
        video = streams[0]

    expected_frames = int(manifest["frames"])
    fps = int(manifest["fps"])
    width, height = manifest["resolution"]
    actual_frames = int(video.get("nb_read_frames", 0) or 0)
    actual_fps = video.get("avg_frame_rate", "0/1")
    duration = float(data.get("format", {}).get("duration", 0.0))
    size = os.path.getsize(args.video)

    if video.get("codec_name") != "h264":
        errors.append("Expected H.264 output.")
    if (video.get("width"), video.get("height")) != (width, height):
        errors.append("Incorrect output dimensions.")
    if actual_frames != expected_frames:
        errors.append("Expected %d frames, got %d." % (expected_frames, actual_frames))
    if actual_fps != "%d/1" % fps:
        errors.append("Incorrect frame rate: %s" % actual_fps)
    if abs(duration - float(manifest["seconds"])) > 0.15:
        errors.append("Incorrect video duration: %.3f seconds." % duration)
    if manifest.get("character_mesh_objects") != 0:
        errors.append("Character mesh objects are forbidden in this production.")
    if manifest.get("character_image_planes") != 0 or manifest.get("character_svg_layers") != 0:
        errors.append("Character image planes and SVG cut-outs are forbidden.")
    if manifest.get("character_cutout_parts") != 0:
        errors.append("Character cut-out parts are forbidden.")
    frame_drawings = manifest.get("per_frame_drawings", 0)
    if frame_drawings != expected_frames:
        errors.append("There must be one newly authored Grease Pencil drawing for every rendered frame.")
    counts = [int(item["strokes"]) for item in manifest.get("per_frame_stroke_counts", [])]
    min_strokes = min(counts) if counts else 0
    average_strokes = (sum(counts) / len(counts)) if counts else 0.0
    authored_templates = int(manifest.get("hand_authored_stroke_templates", 0))
    if authored_templates < 100:
        errors.append("Insufficient individually authored line templates: %d." % authored_templates)
    if min_strokes < 140:
        errors.append("Too few ink strokes in at least one frame: minimum %d." % min_strokes)

    report = {
        "status": "failed" if errors else "passed",
        "video": os.path.abspath(args.video),
        "file_size_bytes": size,
        "file_size_mb": round(size / 1_000_000, 3),
        "codec": video.get("codec_name"),
        "resolution": [video.get("width"), video.get("height")],
        "fps": actual_fps,
        "frames": actual_frames,
        "duration_seconds": round(duration, 3),
        "grease_pencil_drawings": frame_drawings,
        "hand_authored_stroke_templates": authored_templates,
        "minimum_strokes_per_frame": min_strokes,
        "average_strokes_per_frame": round(average_strokes, 1),
        "character_mesh_objects": manifest.get("character_mesh_objects"),
        "character_image_planes": manifest.get("character_image_planes"),
        "character_svg_layers": manifest.get("character_svg_layers"),
        "errors": errors
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.report)), exist_ok=True)
    with open(args.report, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
    print(json.dumps(report, indent=2))
    if errors:
        sys.exit(1)

if __name__ == "__main__":
    main()
