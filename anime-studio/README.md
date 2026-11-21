# LINEFORGE — Code-authored, hand-drawn 2.5D anime

LINEFORGE is the new horizontal anime path inside SHORTFORGE. It replaces the earlier Three.js/SVG cut-out experiment. The character is drawn as individual frame-by-frame Grease Pencil strokes in Blender's actual 3D world.

## Non-negotiable production rule

The character is not built from stick figures, body meshes, SVG/PNG/raster body parts, 2D image planes, cut-out puppets, sprite assemblies, downloaded character models or animation footage.

The character is built from individually coded line paths. Every contour, eyelid, iris, pupil, brow, nose, mouth line, hair lock, seam, clothing fold, finger, knuckle, shadow hatch, rim highlight and action mark is a separate stroke. Each output frame gets a new Grease Pencil drawing. The coordinates are transformed and deformed frame-by-frame into 3D world space; stroke depth, line weight, tapered ends, camera perspective, lighting and parallax make the drawing live inside a 3D scene.

The environment is actual 3D geometry: layered towers, windows, structural ribs, cables, elevated walkways, shopfronts, signage, wet street, utility structures, practical neon lighting and a moving perspective camera.

## Free/open-source toolchain

| Tool | Role | Why selected |
|---|---|---|
| Blender 4.5.16 LTS + Grease Pencil v3 | Main line-art renderer, animation and 3D stage | Frame-by-frame 2D strokes can exist in 3D space, with camera, depth, layers, modifiers and lighting. |
| Krita | Free raster animation and cleanup companion | Useful for traditional hand-drawn frame studies, onion-skin checks, paint passes and brush work. |
| Tahoma2D 1.6.3 | Free traditional 2D animation / FX companion | Provides a 2D production, X-sheet, brush, palette, perspective-grid and compositing workflow. Not used for character cut-out animation here. |
| FFmpeg / ffprobe | Video encoding and delivery verification | Converts rendered frames to MP4 and confirms actual resolution, codec, frame rate and duration. |

Pencil2D is another lightweight open-source frame-by-frame option. OpenToonz is a broader traditional 2D production system. Synfig is a free vector animation option, but emphasizes tweened/vector and rig workflows, so it is not the character renderer here.

### Runtime installation

On an Ubuntu-based Linux machine or CI runner:

    sudo bash anime-studio/lineforge/install_free_tools.sh

The installer pins Blender 4.5.16 LTS, installs Krita and FFmpeg from the system package manager, and verifies the Tahoma2D 1.6.3 Linux package by SHA-256 before installing it. All selected software is free/open-source; no AI image credits, paid animation service or copyrighted production asset is required.

### Local rendering

    LINEFORGE_FPS=30 \
    LINEFORGE_SECONDS=6 \
    LINEFORGE_WIDTH=1280 \
    LINEFORGE_HEIGHT=720 \
    blender --background --factory-startup --threads 4 \
      --python-exit-code 1 \
      --python anime-studio/lineforge/build_handdrawn.py -- \
      --output-dir out/lineforge

The script writes an editable Blender scene with Grease Pencil drawings, numbered PNG frames and a JSON manifest containing per-frame stroke counts.

Encode:

    ffmpeg -framerate 30 -start_number 1 \
      -i out/lineforge/frames/frame_%04d.png \
      -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p \
      -r 30 -movflags +faststart -an \
      out/lineforge/lineforge-handdrawn-720p.mp4

Run the strict stroke QA:

    python3 anime-studio/lineforge/qa.py \
      --video out/lineforge/lineforge-handdrawn-720p.mp4 \
      --manifest out/lineforge/lineforge-manifest.json \
      --report out/lineforge/lineforge-qa.json

## Reference research: craft, not copying

The visual target is informed by multiple animation traditions and production approaches:

- Cyberpunk: Edgerunners / Studio Trigger: expressive silhouette design, sharp graphic posing, energetic hair and clothing shapes, selective neon contrast, intense face acting and impactful drawn effects.
- Jujutsu Kaisen / MAPPA: action readability, strong perspective, foreshortening, clear contact poses, spacing, impact drawings, controlled abstraction and expressive character acting.
- Mob Psycho 100 / Bones: individual animator personality, elastic expression, emotional clarity and freedom in drawn effects.
- Akira: dense perspective backgrounds, architectural drawing, mechanical detail and convincing physical weight.
- Fog Hill of Five Elements: ink-like brush energy, fluid action and graphic shape rhythm.
- Arcane: a useful non-anime hybrid reference for painterly lighting, 3D depth, layered composition and material treatment.

The references are for high-level craft analysis only. No copyrighted anime frame, model sheet, character, costume, script, shot sequence, logo, music or episode is included in the project.

## Art and animation checklist

1. Anatomy: convincing head construction, neck, torso, shoulder girdle, elbows, wrists, pelvis, knees, ankles, hands and believable proportions.
2. Face: eyes are drawn from lids, iris, pupil, lashes and brows; nose and mouth have structure; expressions change with acting.
3. Hair: individual locks, layered clumps, flyaways and follow-through; never one helmet-like silhouette.
4. Line craft: tapered ends, varied line weight, selective broken contours, clean overlaps, secondary detail, deliberate roughness and no mechanically uniform outline.
5. Construction: internal contours, cross-contours and hatching clarify volume; line placement changes with body turn and perspective.
6. Frame animation: each frame has a new Grease Pencil drawing; readable keys and breakdowns, anticipation, arcs, spacing, overshoot, holds, follow-through and recovery.
7. Action: clear contact poses, foreshortened limbs, directional smears, speed lines and impact accents that support rather than obscure the action.
8. 3D staging: perspective camera, camera movement, depth-separated line geometry, parallax, spatially placed strokes and real 3D environment lighting.
9. Colour and finish: controlled palette, coloured rim strokes, selective shadow hatching, atmospheric depth and restrained bloom that never washes away the ink.
10. Environment: detailed, occupied 3D locations with foreground / midground / background layers, practical light sources, mechanical detail and believable scale.
11. Cinematography: shots have deliberate screen direction, readable staging, motivated camera moves, close-ups, wide shots and controlled shot rhythm.
12. Delivery: 16:9, 720p review, 30 fps, H.264 MP4, exact frame count, contact sheet, source Blender scene, manifest and QA report.
13. Human review: playback and frame review for line popping, anatomy, perspective, expression, timing, visual clarity and continuity.

Automated QA proves the character is rendered from Grease Pencil strokes and the video is complete. It cannot prove that the artwork equals a professional studio series. That requires repeated redraw, animation supervision and visual review.

## Current proof-of-pipeline scope

The first LINEFORGE CI target is a six-second, 720p, 30 fps original action sample. It is a technical and art-direction prototype for the line-only pipeline, not a claim that six seconds of code can automatically equal a full studio production. Higher fidelity requires more authored drawings, more poses, cleanup and shot-specific animation.

## Workflow

GitHub Actions workflow: .github/workflows/lineforge-anime.yml.

It installs the open tools, checks the Blender Grease Pencil API, generates the city scene, redraws the character strokes on every frame, encodes the MP4, generates a contact sheet, runs strict line-art QA and publishes the MP4 plus editable Blender scene, manifest and QA report as a separate GitHub prerelease.

## Official software and research links

- Blender Grease Pencil manual: https://docs.blender.org/manual/en/4.5/grease_pencil/introduction.html
- Blender Grease Pencil animation: https://docs.blender.org/manual/en/4.5/grease_pencil/animation/introduction.html
- Blender Grease Pencil API: https://docs.blender.org/api/4.5/bpy.types.GreasePencilDrawing.html
- Krita animation manual: https://docs.krita.org/en/user_manual/animation.html
- Tahoma2D: https://tahoma2d.org/
- Tahoma2D source and releases: https://github.com/tahoma2d/tahoma2d
- Pencil2D: https://www.pencil2d.org/about
- Synfig: https://www.synfig.org/
- Studio Trigger / Netflix on Cyberpunk: Edgerunners: https://about.netflix.com/en/news/netflix-cd-projekt-red-and-studio-trigger-come-together-for-global-anime-cyberpunk-edgerunners
- Animation World Network on Edgerunners: https://www.awn.com/animationworld/cyberpunk-edgerunners-vibrant-ode-retro-anime
- Crunchyroll interview with MAPPA leadership on Jujutsu Kaisen: https://www.crunchyroll.com/hi/news/interviews/2022/8/8/interview-manabu-otsuka-hiroshi-seko-and-hiroaki-matsutani-on-the-future-of-jujutsu-kaisen
- Crunchyroll interview with Mob Psycho 100 director: https://www.crunchyroll.com/news/interviews/2019/3/30/interview-mob-psychos-director-is-changing-hearts-and-getting-in-trouble-with-the-president-of-bones
