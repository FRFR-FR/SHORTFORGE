# Explainer3D Debate mode

SHORTFORGE's existing short-form renderer remains portrait-first. The Explainer3D Debate branch adds an isolated 16:9 long-form production path to avoid weakening the original Shorts pipeline or its 9:16 validator.

## Project contract

- 300 seconds, 1280×720, 30 fps, 9,000 frames.
- Blender EEVEE Next renders PNG sequences; the existing SHORTFORGE frame analyser checks all frames; FFmpeg produces H.264/AAC.
- The renderer reuses the repository's prebuilt, textured, rigged Quaternius male/female avatars and the shared avatar expression/pose system.
- The episode has 28 authored speaking turns, 736 words, 3 distinct voices, 7 set locations and multiple camera perspectives.
- Full dialogue is not burned into the picture; a sidecar SRT is delivered.
- No music.

## Files

- skills/explainer3d-debate/SKILL.md — source-derived long-form debate skill.
- skills/explainer3d-debate/references/ — source skill, original style Bible and adapted episode style Bible.
- production/glasswing-debate/ — project config, dialogue, production script and fact-check.
- scripts/fetch_debate_assets.py — retrieves only the existing CC0 rigged character assets; it skips the large demo splash environment.
- scripts/generate_debate_audio.py — Kokoro Liam and Kyutai Pocket TTS George/Eponine line synthesis, speaker stems, SRT and timing manifest.
- src/blender/render_debate.py — dedicated landscape stage builder, scene-specific blocking, rigged cast, camera system and keyword overlays.
- .github/workflows/glasswing-debate.yml — 10-second smoke gate, full 9,000-frame render, QA, encoding, ffprobe verification and GitHub Release delivery.

## Voice mapping

- Liam: Kokoro am_liam.
- George: Kyutai Pocket TTS prompt p315_023_enhanced.wav.
- Eponine: Kyutai Pocket TTS prompt p262_023_enhanced.wav.

The workflow requires the repository Action secret HF_TOKEN if the selected Pocket TTS voice prompts require authenticated Hugging Face access. The workflow intentionally fails on voice generation errors rather than silently substituting a different voice.

## Run

Open GitHub Actions → “SHORTFORGE — Explainer3D Project Glasswing Debate” → Run workflow. The workflow first synthesizes and validates all three voices, then runs a 300-frame smoke render. A smoke QA failure stops the full five-minute job. On success, it renders all 9,000 frames, verifies the MP4 with ffprobe and publishes the deliverables as a GitHub Release.

A successful branch commit or workflow dispatch is not proof of a completed video. Check the job summary, final QA JSON and release assets.