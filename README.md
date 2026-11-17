# SHORTFORGE — Blender + Three.js Animated Shorts Pipeline

A fresh, code-first production pipeline for original vertical animated shorts. Blender is the **final renderer**; Three.js is the interactive previs tool. Frames are rendered directly by headless Blender and encoded by FFmpeg, avoiding browser-based frame rendering. Finished videos are published as GitHub Release assets, not Actions artifacts, so the workflow does not consume the Actions artifact-storage quota.

## What it does

- Imports complete, prebuilt Blender Studio environments with recorded licences and SHA-256 provenance; no cubes-and-spheres blockout is the default production environment.
- Builds reusable textured male and female humanoid avatars before rendering. Each is a 65-joint Quaternius CC0 rig with PBR skin/hair/eye textures, seven facial emotions and eight reusable poses.
- Animates a character, camera and scene at a fixed **30 fps**.
- Uses **9:16 vertical** delivery: 720×1280 preview/production and optional 1080×1920 master; 540×960 ten-second smoke test.
- Provides a separate Three.js browser previs so shots can be inspected interactively before final rendering.
- Optionally generates English narration through Kokoro TTS and burns in a supplied SRT caption file; narration/captions are off by default and no music is added by default.
- Validates project settings, analyzes every rendered frame for blank/black/white frames and excessive duplicates, creates a contact sheet, and verifies the final MP4 with `ffprobe`.
- Includes a ChatGPT skill, style bible, ten-reference research worksheet, and seven specialist review passes.
- Publishes MP4 and compact QA files as a GitHub Release when requested. **It never uses `actions/upload-artifact`.**

## Why this replaces the failed prototype

| Previous failure | SHORTFORGE design |
|---|---|
| Remotion/Chrome renderer stalled at frame 3 with a 30-second protocol timeout | No Remotion, Puppeteer or Chrome in the final-render path. Blender renders numbered PNG frames directly. |
| GitHub Actions artifact storage quota blocked MP4 upload | No Actions artifacts. A manual run can publish the MP4, QA JSON and contact sheet as GitHub Release assets. |
| Blender Python could not import system NumPy | Blender scene builder uses Blender's bundled Python API and standard library only. NumPy is not required. |
| Prototype had a browser render dependency in its critical path | Three.js is optional previs only; the final MP4 is created independently by Blender + FFmpeg. |

## Quick start on a local Linux machine

Requirements: Blender 4.x, FFmpeg/ffprobe, Python 3.10+, and Pillow.

```bash
sudo apt-get update
sudo apt-get install -y blender ffmpeg python3-pil
python3 scripts/validate_project.py config/smoke.json
python3 scripts/render.py --project config/smoke.json --output-dir out/smoke
```

The renderer writes intermediate frames to a temporary directory, runs frame-level QA, encodes `out/smoke/shortforge-smoke.mp4`, and creates `qa-report.json` plus `contact-sheet.jpg`.

For a larger render:

```bash
python3 scripts/render.py --project config/template.json --output-dir out/episode-001
```

Change `config/template.json` to your original story, scene length, resolution, narration and shot cues. Read `docs/PROJECT_CONFIG.md` before editing the schema.

## Interactive Three.js previs

```bash
cd preview
npm install
npm run dev
```

The preview is for shot blocking, camera framing and timing. It is deliberately not part of the final-render workflow, so a browser crash cannot prevent the MP4 from being rendered.

## GitHub Actions

1. Create a new repository and push this project to its `main` branch.
2. Open **Actions → SHORTFORGE render**.
3. Choose `smoke`, `preview` or `master`.
4. Enable `publish_release` to attach the MP4 and QA outputs to a new GitHub Release.

Required workflow permission: **Contents: read and write**. The workflow uses the built-in `GITHUB_TOKEN`; no PAT or YouTube API key is required for rendering. A YouTube API key is not used by this project because the short-form research stage is a human/ChatGPT-assisted review process, not automated scraping.

The smoke setting is exactly 10 seconds × 30 fps = 300 frames. Preview defaults to 30 seconds at 720×1280. Master defaults to 30 seconds at 1080×1920. One-minute renders 60 seconds at 720×1280 / 30 fps = 1,800 frames.

### Release storage

The workflow intentionally does not call `actions/upload-artifact`. When `publish_release` is enabled it uses `gh release create` to attach the MP4 and compact QA files to a release. This bypasses the **Actions artifact quota** that blocked the previous run; it does not mean GitHub Releases have unlimited storage or that a release asset can be larger than GitHub's applicable limits.

## Audio

Kokoro narration is opt-in. Set `narration_text` and `kokoro_voice` in the project JSON or enable the `enable_kokoro` workflow input. The default voice is `am_michael` as a configurable starting point, not a claim that one voice is universally best. The pipeline adds narration only; it does not add background music.

## Production quality gates

A render is not marked successful until all of these pass:

1. Project schema and dimensions validate.
2. Blender completes the full frame range.
3. Expected frame count and dimensions are correct.
4. Per-frame luminance/variance checks find no blank frames or long frozen stretches.
5. Contact sheet is generated.
6. FFmpeg successfully encodes H.264 MP4 at 30 fps and `ffprobe` confirms duration, dimensions and codec.
7. Optional narration is muxed and audio stream is verified.
8. If publishing is requested, the release upload completes.

Automated pixel checks cannot judge story quality, model anatomy, emotional performance or continuity by themselves. Complete the seven specialist reviews in `docs/REVIEW_TEAM.md` and visually inspect the contact sheet/sequence before calling a video production-ready.

## Originality and rights

Reference research is for high-level format analysis only: hooks, average shot duration, pacing, framing, captions, visual density, tone and sound design. Do not reproduce another creator's script, characters, artwork, exact scene order, signature assets or distinctive shot sequence. Use original characters, environments, dialogue and licensed assets. See `docs/REFERENCE_RESEARCH.md`.

## YouTube Reference Lab (yt-dlp)

The optional research stack lives in `requirements-research.txt` so it does not add computer-vision dependencies to the Blender renderer.

Install locally with Python 3.12:

```bash
python3.12 -m pip install -r requirements-research.txt
python scripts/research_channel.py --channel-url https://www.youtube.com/@ricksclips3000/videos --top-n 20 --max-candidates 300 --output-dir out/reference-lab
```

The default run is metadata-only. The manual **Actions → SHORTFORGE reference lab** workflow can rank the channel's accessible uploads by visible view count. Frame-level downloads and measurements are disabled unless the operator attests to ownership or written permission and confirms the use is permitted by platform terms. Temporary source files are deleted after measurement; releases contain only metadata and numeric reports.

See `docs/CHANNEL_REFERENCE_LAB.md` for installation, per-frame metrics and rights requirements, and `skills/shortforge-reference-lab/SKILL.md` for the single-topic original video workflow. The companion Claude tutorial workflow is attributed in `docs/CLAUDE_TUTORIAL_ADAPTATION.md`.

## First original Reference Lab test: Window Tax

The first sample episode is an original 60-second history short titled **Britain Once Taxed Sunlight**. Its authored project config is `production/window-tax-project.json`; the render-trigger config is `production/launch-short.json`. The Three.js previs is in `preview/`, and the final render remains Blender + FFmpeg at 720×1280 / 30 fps.

- Script and fact notes: `production/window-tax-script.md`
- Timed captions: `production/window-tax.srt`
- Visual, screen, animation and delivery checks: `production/window-tax-production-checklist.md`

Historical nuance is intentional: some owners closed windows in response to the tax, but a blank window is not automatically proof of tax avoidance; symmetry and architectural design also matter.

## Repository map

```text
config/                 Project, style-bible and smoke-test configs
src/blender/avatar_system.py   Reusable 7-emotion / 8-pose humanoid avatars
src/blender/            Procedural scene builder and direct frame renderer
src/qa/                 Output QA and reference-video frame analyzer
src/audio/              Optional Kokoro narration adapter
preview/                Interactive Three.js shot previs
scripts/                Validation, render orchestration, channel research and tests
prompts/                Storyboard and review prompts
skills/                 ChatGPT production and reference-lab skills
.github/workflows/      Render and reference-lab GitHub Actions workflows
docs/                   Architecture, schema, research and review guides
```

## Status

This repository package is a new implementation. Its local validation suite can be run with `python3 -m unittest discover -s tests -v`. A GitHub Actions render can only be verified after this project is pushed to a GitHub repository and the workflow is run there.
