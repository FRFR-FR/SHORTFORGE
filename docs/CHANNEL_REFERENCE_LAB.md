# SHORTFORGE Channel Reference Lab

## Purpose

The Reference Lab ranks accessible public channel uploads by visible view count. If the operator owns the videos or has written permission and the platform terms permit the use, it can temporarily process the selected videos and measure every decoded frame.

This is a benchmarking system, not a one-click clone. Use aggregate production patterns only. Do not reproduce another creator's scripts, dialogue, characters, artwork, signature props, branding, audio, or distinctive shot sequence.

## Install

Research dependencies are isolated from Blender rendering:

    python3.12 -m pip install -r requirements-research.txt

The requirements install yt-dlp, OpenCV headless and NumPy. Adding the requirements file does not install packages into GitHub immediately; the Action installs them when run.

## Metadata-only run (default)

    python scripts/research_channel.py \
      --channel-url https://www.youtube.com/@ricksclips3000/videos \
      --top-n 20 --max-candidates 300 \
      --output-dir out/reference-lab

This ranks accessible uploads by view count and writes a metadata snapshot. It does not download video files.

## Full-frame measurement (rights required)

Downloads are disabled by default. Enable them only for videos you own or have written permission to use, and only where downloading and analysis are permitted by the platform terms.

    python scripts/research_channel.py \
      --channel-url https://www.youtube.com/@ricksclips3000/videos \
      --top-n 20 --max-candidates 300 \
      --download-and-analyze \
      --rights-attestation "I own or have written permission to download and analyze every selected video, and this use is permitted by the platform terms." \
      --output-dir out/reference-lab

The same options are available in Actions → SHORTFORGE reference lab. Metadata-only is the default. The download switch requires the exact attestation. Do not commit or release source MP4s or extracted frames.

## Frame-level measurements

The frame analyzer decodes every source frame. To keep compute reasonable, computer-vision work runs on a resized copy (360 px wide); source dimensions, fps, duration and decoded frame count are reported.

- Dominant translation proxy: estimated pixel displacement from tracked features.
- Zoom proxy: frame-to-frame global affine scale change.
- Roll proxy: estimated frame rotation.
- Optical flow: mean and 95th-percentile apparent pixel motion.
- Scene-change score: grayscale histogram difference used to flag likely cuts.
- Edge density: fraction of pixels identified as edges (not true outline width).
- Luminance and saturation: average grayscale and HSV values.
- Sharpness proxy: Laplacian variance.

Camera estimates may be confounded by subject movement, parallax, animated backgrounds and edits. Optical flow includes all visible movement, not only camera motion. Edge density is not a measurement of outline thickness. These statistics are useful signals, not ground truth or subjective quality scores.

## Single-topic video creation

Start with one topic and write a new story. Use aggregate values as broad constraints: hook legibility, a useful shot-duration range, purposeful camera movement, consistent contrast and visual hierarchy. Build new characters, materials, sets, lighting, transitions and shot order.

SHORTFORGE still uses Blender for final rendering, Three.js for optional previs, FFmpeg for encoding, frame-level QA and the seven independent reviews. Review every output against the existing style bible and inspect the contact sheet.

## Outputs

- top20-metadata.json: ranked public metadata snapshot.
- analysis-summary.json: aggregate measurements and caveats.
- frame-metrics/<id>.frames.csv: numeric values per decoded frame.
- frame-metrics/<id>.summary.json: per-video distributions.
- research-results.zip: compact report bundle.

Downloaded source media is kept in a temporary directory and deleted after analysis. Releases contain report files only.

## Tutorial attribution

The supplied tutorial is titled “How to Make Viral Animated Shorts Using Claude (Full Workflow)”. Its companion project, mromidev/claude-animated-shorts, is published under the MIT License. SHORTFORGE adapts general workflow ideas—research, a style document, original story development, specialist reviews and iterative QA—while retaining its own Blender final-render architecture. The tutorial MP4 and companion reference frames are not copied into this repository.
