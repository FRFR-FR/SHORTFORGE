# ANIMEFORGE — Claude Agent + Three.js 2.5D Anime Studio

ANIMEFORGE is a dedicated horizontal-anime production system inside SHORTFORGE. It does not replace the existing Blender-based vertical Shorts pipeline.

## Production target

- Horizontal 16:9 episodes; 1280×720 review renders and 1920×1080 masters.
- 30 fps deterministic frame output.
- 2.5D staging: layered foreground / action plane / background, perspective camera moves, depth parallax, animated lights, atmospheric particles, and optional rigged GLB or layered transparent character artwork.
- Original anime character designs, environments, dialogue and shot choreography.
- High-contrast hand-inked/cel-shaded visual direction with vivid electric cyan, hot magenta, ultraviolet and warm amber accents; this is an original cyberpunk anime language, not a recreation of another series.
- Browser-rendered Three.js frames, then FFmpeg H.264 encoding.
- Frame-by-frame technical QA plus a report and contact sheet.
- No music or narration is synthesized unless the episode supplies audio.

## Why Three.js is the final renderer here

This engine intentionally differs from SHORTFORGE's original vertical pipeline. The episode's authored JavaScript scene module is evaluated in a controlled local browser page, Three.js renders a fixed timestamp, Playwright captures the canvas, and FFmpeg encodes the numbered frames. A deterministic seek API makes every frame independent of browser refresh rate. See the official Three.js renderer docs and Playwright CI guidance.

## Create an episode with Claude

Install Node.js 22+, FFmpeg/ffprobe, then:

    cd anime-studio
    npm install
    npx playwright install chromium
    export ANTHROPIC_API_KEY="your-key"
    npm run agent -- "An original 90-second cyberpunk chase about a courier who discovers a memory chip can rewrite one minute of the past" --slug memory-run --quality preview

Claude's official Agent SDK is used as the coding agent. It receives a project-local workspace, specialist subagents, and only file authoring / inspection tools. Shell execution is not granted to the model: trusted scripts validate and render the resulting project. The Agent SDK package is documented on npm as @anthropic-ai/claude-agent-sdk.

The agent edits:
- projects/<slug>/episode.json — episode spec, cast, timeline, shot intent and output profile.
- projects/<slug>/episode.js — executable Three.js choreography using the shared ANIMEFORGE kit.
- projects/<slug>/TASK.md — the supplied creative brief and quality bar.

After generation, validate and render:

    npm run validate -- --project projects/memory-run/episode.json
    npm run render -- --project projects/memory-run/episode.json --output out/memory-run.mp4

## Render profiles

| Profile | Resolution | Use |
|---|---:|---|
| smoke | 640×360 | Engine/scene validation only |
| preview | 1280×720 | Review and iteration |
| master | 1920×1080 | Final horizontal master |

Override the JSON dimensions with --quality when rendering. The project remains 30 fps. A long episode can take substantial time because every frame is rendered and captured; use a short smoke render before a full episode.

## Asset pipeline: actual anime artwork, not primitive-only scenes

ANIMEFORGE supports:
1. Original transparent PNG character layers attached to articulated 2D pivots.
2. Rigged GLB characters with animation clips through Three.js GLTFLoader.
3. Painted environment plates and layered depth cards.
4. Three-dimensional sets, props, vehicles, lighting and camera choreography.
5. Procedural vector/toon puppets for smoke tests only.

The included procedural city and puppet are a runnable engine demonstration, not a claim of finished studio-grade anime art. For final production, the art pack should contain high-resolution original character turnarounds, separated hair / face / torso / upper-arm / forearm / hand / thigh / shin / footwear layers or a properly rigged GLB, expression variants, and detailed environment plates. The validator distinguishes a technical render from an art-complete master; a master must declare its real character and environment assets rather than rely on the fallback puppet.

### Recommended folder layout

    projects/<slug>/
      TASK.md
      episode.json
      episode.js
      assets/
        characters/<character-id>/
          model.glb
          expressions/
          layers/
        environments/<environment-id>/
          foreground/
          midground/
          background/
        audio/

Use only original, owned, public-domain or correctly licensed assets. Do not trace existing anime characters, recreate signature costumes, copy frames, or reproduce a show's exact shot sequence.

## Quality gates

A render is not marked complete merely because Chromium opened. ANIMEFORGE checks:

- Valid 16:9 dimensions and complete, gap-free shot coverage.
- Scene module syntax and required exported function.
- Character IDs, shot descriptions, visual actions, camera intent and art direction.
- Full frame count, PNG dimensions, blank-frame / near-frozen-frame checks.
- FFmpeg exit status and ffprobe codec, size, duration and frame-rate verification.
- A contact sheet and JSON QA report.

Automated checks cannot prove good anatomy, acting, composition, emotional storytelling or final illustration quality. A human art review remains mandatory before calling an episode release-ready.

## GitHub Actions

Run Actions → ANIMEFORGE episode. Add ANTHROPIC_API_KEY as a repository Actions secret to enable Claude generation. Supply a concept, duration, quality and optional release publishing. The workflow publishes MP4 and QA files as a GitHub Release; it does not use Actions artifacts.

## Safety and budget

The Claude agent has a configurable CLAUDE_MAX_BUDGET_USD limit and CLAUDE_MODEL override. Default model: claude-opus-5-5. It is not permitted to run shell commands. Local validation, browser rendering and encoding are performed by the repository's own scripts.
