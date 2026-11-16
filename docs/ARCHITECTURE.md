# Architecture

## Rendering boundaries

SHORTFORGE has two separate visual systems by design:

- **Three.js previs:** a fast interactive browser view for blocking a shot, testing camera composition and checking timing. It is a creative preview, not the final renderer.
- **Blender final render:** procedural assets and the final 3D scene are generated in a `.blend` session by `src/blender/render_scene.py`. Blender writes a numbered PNG sequence directly to a temporary directory. No browser process is involved.

FFmpeg consumes that numbered sequence at exactly 30 fps and produces H.264 MP4 (`yuv420p`, fast-start metadata). If narration exists, FFmpeg muxes it as AAC. Music is not generated or inserted by default.

## Render lifecycle

```text
Project JSON
    │
    ▼
Schema validation ── fail fast on wrong fps/aspect ratio/duration
    │
    ▼
Blender headless scene build + animation
    │
    ▼
PNG frame sequence in temporary storage
    │
    ▼
Frame QA ── every frame: dimensions, luminance, variance, duplicate-run checks
    │
    ├── contact sheet
    └── QA JSON
    │
    ▼
FFmpeg H.264 + optional AAC narration
    │
    ▼
ffprobe verification: codec, 30 fps, dimensions, duration
    │
    ▼
Optional GitHub Release assets (no Actions artifact)
```

## Failure containment

- Blender uses only `bpy` and Python's standard library; it does not import NumPy or export a GLB for the renderer.
- The main render does not depend on Node, Vite, Chromium, Chrome Headless Shell, Remotion, Puppeteer or browser DevTools Protocol.
- Every render is bounded by a GitHub Actions job timeout. Blender frame progress is written into the Actions log.
- Temporary frames are removed after QA and encoding unless `--keep-frames` is used locally.
- The final render is verified independently with `ffprobe`.
- `actions/upload-artifact` is deliberately absent. If the user requests publishing, the workflow uploads MP4 and QA files to a GitHub Release with `gh`.

## Reproducibility

A render is driven by one JSON project file, one style bible and source-controlled procedural geometry. Random generation is not used in the starter scene. Output settings are explicit, and the output manifest records settings and media metadata.
