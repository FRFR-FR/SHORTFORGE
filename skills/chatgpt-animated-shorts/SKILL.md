---
name: shortforge-animated-shorts
description: Plan, author, render and quality-check original vertical animated shorts using Blender final rendering and Three.js previs.
---

# SHORTFORGE animated shorts skill

Use this skill for original code-first animated shorts in this repository.

## Non-negotiable production defaults

- 9:16 vertical output, 30 fps.
- Preview 720×1280; optional master 1080×1920; ten-second smoke test 540×960.
- Blender is the authoritative final renderer. Three.js is for interactive previs only.
- Render image sequences directly with Blender, then encode with FFmpeg. Do not add Remotion, Puppeteer or Chrome to the final render path.
- Narration is optional through Kokoro. No background music by default.
- Use original characters, props, environments, scripts and dialogue. External assets must be owned, public-domain or properly licensed.

## Workflow

1. **Brief:** clarify the viewer, premise, emotional outcome, platform and target duration. Write one sentence describing the short's original central idea.
2. **Reference research:** when the user supplies references or asks for competitor analysis, inspect ten suitable public examples where access permits. Record metadata and abstract production patterns in `docs/REFERENCE_RESEARCH.md`. Never download or copy protected material; do not imitate an exact creator or sequence.
3. **Style bible:** update `config/style-bible.json` with palette, lighting, materials, character design language, camera rules, motion rules and caption-safe areas. Keep this stable across the full short.
4. **Script and storyboard:** produce a word-for-word narration script (or state none), beat sheet, timestamped shot list, staging, camera moves, props, environment and sound plan. Create a visible action change every few seconds where appropriate.
5. **Previs:** use `preview/` to check vertical composition, camera positions and rough timing in Three.js. Do not depend on the preview browser to produce the final MP4.
6. **Build and animate:** create purpose-built environments and characters procedurally in Blender. Check every model for missing or duplicated facial parts, proportion errors, bad pivots, ground contact and intersections. Animate with anticipation, weight, foot planting and follow-through.
7. **Smoke render:** run the ten-second, 300-frame smoke profile first. Review `contact-sheet.jpg` and `qa-report.json`. Do not proceed if render, encoding or QA fails.
8. **Production render:** use preview or master profile after smoke passes. Render frames, analyze every frame, encode with FFmpeg and verify via ffprobe.
9. **Seven reviews:** complete each specialist pass from `docs/REVIEW_TEAM.md` independently. Log frame/timestamp references and fixes. Re-render affected ranges or the full short as needed.
10. **Delivery:** supply MP4, QA report, contact sheet, manifest, narration script and shot list. Clearly state remaining caveats; never call the video finished without a verified MP4.

## Troubleshooting rules

- If Chromium/Remotion appears in the final-render path, remove that dependency; final render belongs to Blender.
- If Blender imports fail, remove unnecessary third-party imports from the Blender script; prefer Blender's bundled API and standard library. Do not assume system NumPy is visible to Blender Python.
- If a render stalls, inspect the failing frame and Blender log; reduce samples or scene complexity only after checking for a scene bug. Do not hide timeouts by setting an unbounded timeout.
- Do not upload MP4s using `actions/upload-artifact`. Keep frames in temporary storage. Publish the final MP4 and small QA files as a GitHub Release when the workflow's publish option is enabled.
- If release publishing fails, keep the local render and report the release failure separately. Do not claim cloud delivery succeeded.

## Completion criteria

A deliverable counts as complete only when the expected frame count exists, frame QA passes, the MP4 exists, `ffprobe` confirms 30 fps/resolution/duration, the seven review passes are recorded, and requested release publishing succeeds. A successful setup/build step alone is not a completed video.
