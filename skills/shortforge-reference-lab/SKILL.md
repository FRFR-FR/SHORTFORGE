---
name: shortforge-reference-lab
description: Turn one topic into an original vertical animated short using SHORTFORGE's Blender renderer, aggregate reference metrics, frame-level QA and seven reviews.
---

# SHORTFORGE Reference Lab — single-topic production skill

Use when the user supplies one topic and requests an original animated short.

## Non-negotiable rules

- Reference measurements are production benchmarks, not a template to copy.
- Never reproduce another creator's script, dialogue, characters, artwork, signature props, branding, exact shot sequence, distinctive compositions, voice or music.
- Use only owned, public-domain or properly licensed assets.
- Blender is the final renderer; Three.js is previs only.
- Default to 9:16, 30 fps and 720×1280. Use 1080×1920 only when requested and compute permits.
- No background music by default. Narration and captions follow the brief.
- Never claim completion without a verified MP4, passing frame QA and seven review records.

## One-topic workflow

1. Research the subject and verify important claims. Find one surprising cause-and-effect or useful visual explanation.
2. Write an original one-sentence hook, followed by setup, escalation, reveal/explanation and payoff. Do not reuse a reference premise or wording.
3. Read the existing style bible and, when present, the Reference Lab aggregate report. Translate aggregate measurements into broad decisions about pacing, camera-motion envelope, contrast, edge density, cut frequency and image clarity.
4. Draft original narration and align visual events to word or beat timing. Do not narrate what the viewer can already see.
5. Create an original storyboard: frame ranges, camera intent, character blocking, environment, focal point, lighting, props, transitions and sound cues.
6. Use Three.js previs to inspect vertical composition, camera paths, scale and eyelines.
7. Build and animate with the existing Blender scene and avatar systems. Prioritize readable silhouettes, planted contacts, anticipation, weight transfer, overlap, follow-through and continuity.
8. Run the ten-second smoke render. Inspect contact sheet and QA JSON before a longer render.
9. Render with Blender and encode with FFmpeg. Analyze every output frame and verify duration, frame rate, dimensions and codec with ffprobe.
10. Complete seven independent reviews from docs/REVIEW_TEAM.md: story, cinematography, character animation, environment/continuity, art direction, sound, and technical QA/rights.
11. Fix blockers, rerender affected ranges and deliver the MP4, QA report, contact sheet, manifest, script and shot plan. Disclose remaining limitations.

## Applying metrics

- Pacing: use aggregate shot-duration values as a starting range; vary rhythm to serve the story.
- Camera: global affine translation, zoom and roll are estimates. Movement must be motivated and independently designed.
- Animation: review silhouette readability, anticipation, planted contacts, follow-through and continuity. Optical flow is not a substitute for animation review.
- Line work: edge density is only an image-complexity indicator. Design original line width, colour and shader treatment.
- Colour and lighting: compare broad luminance/saturation ranges, then build an original palette and lighting setup.
- Cuts: use scene-change metrics as a pacing reference, but edit for comprehension and emotional beats.

## Approval gate

A short is not complete until frame count, frame QA, ffprobe verification, all seven review records, human contact-sheet inspection and asset rights checks pass. The purpose is to improve measurable craft while making a distinct original video.
