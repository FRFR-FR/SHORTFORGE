# FULLBODY2D — fully rendered anime characters on a 2D stage

## Correct production target

This is a **2D animation production**. People, props, effects and backgrounds are authored as 2D artwork on a 2D canvas. They must look dimensional because the drawing and painting correctly describe volume, not because a 3D environment or wireframe is doing the work.

A finished person is not a stick figure, a mannequin, a few contour strokes or a set of floating body pieces. Each character must be a complete illustrated design with:

- a fully constructed head and face: skull, jaw, ears, eyebrows, eyelids, eyes, irises, pupils, nose, lips, teeth when visible, expressions and profile/three-quarter views;
- believable anatomy and proportions: neck, shoulders, ribcage, pelvis, upper/lower arms, elbows, wrists, full hands and fingers, thighs, knees, calves, ankles and feet;
- designed hair with layered locks, clumps, strands, flyaways, overlap and follow-through;
- complete clothing and accessories: collars, lapels, seams, fasteners, belts, straps, fabric thickness, folds, boots and material-specific surface treatment;
- proper colour construction: local colour, light planes, form shadows, cast/contact shadows, reflected light, rim light, selective texture and deliberate line-weight;
- coherent poses and redraw/cleanup when the body turns, foreshortens, reaches, walks or interacts with props.

Props and environment objects need the same design care: a deliberate silhouette, perspective, edge/bevel treatment, surface material, light response, cast/contact shadow, and visible structure. Do not assemble the final artwork out of flat icons or generic primitives.

The 3D appearance is made by **2D construction**: overlap, perspective, foreshortening, form turns, plane changes, cel shading, gradient transitions, reflected colour, controlled highlights and atmospheric depth. The final stage remains 2D.

## Current free production stack

- **Krita** — high-resolution character design, painted layers, cleanup and texture.
- **Tahoma2D / OpenToonz** — traditional 2D drawing levels, X-sheets, timing, compositing and camera work.
- **Python + CairoSVG** — code-authored, deterministic 2D frame rendering for the first procedural prototype.
- **Pillow** — reference palette/contrast analysis and frame QA.
- **FFmpeg / ffprobe** — image-sequence encoding and media verification.
- **yt-dlp** — downloads the creator-cleared visual references directly from Wikimedia Commons, avoiding YouTube's sign-in gate on anonymous CI.

The code renderer is an early proof-of-pipeline, not a substitute for an animation team. Procedural artwork should be expanded through designed character sheets, expressions, key poses, breakdowns, in-betweens, cleanup and frame-by-frame visual review before long-form production.

## Licensed visual references downloaded by yt-dlp

The reference job downloads two openly licensed Morevna Project animations to temporary CI storage using **yt-dlp** direct file URLs. It verifies each original file's SHA-1 checksum before continuing, extracts the visual stream with FFmpeg, removes the muxed source file, and verifies that the resulting reference video has no audio stream. Contact sheets are used to produce a numeric palette/contrast guide. The original footage, frames, character art and sound are never copied into the finished animation or its release.

### 1. Morevna Episode 3.0.2 (English)

- A 10-minute, 1080p futuristic anime episode by Morevna Project.
- The original creator's description states CC BY-SA 4.0; the current Commons file page lists CC BY 4.0. To avoid claiming broader rights than the creator's statement, this project conservatively records and follows **CC BY-SA 4.0** for reference handling.
- Study purpose: complete character design, costume construction, dimensional 2D/limited-animation staging, action readability and cinematic framing.
- Attribution: **Animation by Morevna Project**.
- Source page: https://commons.wikimedia.org/wiki/File:Morevna_Episode_3.0.2_(English).webm
- Creator page: https://morevnaproject.org/anime/episode-3/
- Licence: https://creativecommons.org/licenses/by-sa/4.0/

### 2. Pepper & Carrot Motion Comic — Episode 6: The Potion Contest

- A 7-minute, 1080p animated short/motion comic by Morevna Project, based on David Revoy's open webcomic.
- The official Morevna page and Wikimedia Commons file page state **CC BY-SA 4.0**; Commons records a Wikimedia Volunteer Response Team permission ticket for the file.
- Study purpose: full-colour illustrated character shapes, visual hierarchy, props, expressive posing, graphic composition and colour grouping.
- Attribution: **Animation: Morevna Project; Illustrations: David Revoy**. The soundtrack by Gregoire Lourme is excluded from the reference work.
- Source page: https://commons.wikimedia.org/wiki/File:Morevna_Project_-_Pepper%26Carrot_(animated_comic)_-_Episode_6_-_The_Potion_Contest.webm
- Creator page: https://morevnaproject.org/pepper-and-carrot/episode-6/
- Licence: https://creativecommons.org/licenses/by-sa/4.0/

These are visual study references, not replacement assets. Do not trace a reference frame, reproduce its characters/costumes/props, or reconstruct its distinctive shot sequence. Use only broad craft principles. The final project's characters, object designs, scenes, poses and story must be independently created.

## How reference footage is used

1. `yt-dlp` downloads the direct Commons WebM files into the runner's temporary directory.
2. FFmpeg copies only each video stream into a video-only WebM; the muxed original file is deleted immediately.
3. ffprobe confirms that no audio stream remains.
4. FFmpeg samples frames into temporary contact sheets.
5. `analyze_reference.py` measures high-level colour palette, luminance and contrast. It outputs numeric data only.
6. `render.py` uses the measured accent colours in original background/signage lighting. No downloaded frame or pixel artwork is embedded in the release.

## Current prototype scene

The first review scene is an original rainy neon street, drawn entirely in SVG and rasterized to PNG. It contains two full-body people:

- Foreground swordswoman: complete face, layered hair, neck, torso, both arms, gloves, fingers, trousers, knees, boots, detailed layered jacket, belt/pouch and a metallic sword with a wrapped grip and bevel highlights.
- Midground scout: a second original full-body person with a distinct face, auburn layered hair, armoured costume, hands/fingers, trousers, knee panels, boots, harness and a designed sidearm.

The 2D environment includes layered architecture, windows, signage, rain, perspective road markings, a small vehicle/prop, lighting glows and camera drift. Character movement includes breathing/weight shift, limbs, blade movement, hair and coat follow-through. The project renderer contains no 3D scene or character meshes.

## Delivery and QA

The GitHub Actions workflow renders a 6-second, 1280×720, 30 fps H.264 no-audio sample. It publishes:
- MP4 review render;
- source SVG scene;
- contact sheet;
- render manifest;
- QA report;
- numeric reference palette and attribution/licence metadata.

QA checks exact frame count, codec, dimensions, frame rate, duration, absence of audio, 2D-stage declaration, full-body anatomy metadata, two character designs, image contrast and measurable frame-to-frame motion. QA cannot certify professional-quality drawing, appealing acting or clean animation. Those still require human visual review.

## Attribution, references and tools

- Morevna Project, *Morevna Episode 3.0.2 (English)*: https://commons.wikimedia.org/wiki/File:Morevna_Episode_3.0.2_(English).webm
- Morevna Project / David Revoy, *Pepper & Carrot Motion Comic — Episode 6*: https://commons.wikimedia.org/wiki/File:Morevna_Project_-_Pepper%26Carrot_(animated_comic)_-_Episode_6_-_The_Potion_Contest.webm
- Creative Commons BY-SA 4.0: https://creativecommons.org/licenses/by-sa/4.0/
- yt-dlp: https://github.com/yt-dlp/yt-dlp
- Krita animation manual: https://docs.krita.org/en/user_manual/animation.html
- Tahoma2D: https://tahoma2d.org/
- OpenToonz: https://opentoonz.github.io/e/
- FFmpeg: https://ffmpeg.org/
