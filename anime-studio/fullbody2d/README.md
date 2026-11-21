# FULLBODY2D — fully rendered characters on a 2D stage

This is the replacement art direction for the retired LINEFORGE stroke-only experiment.

## The actual target

Build the entire production as a **2D animation**. The background, people, props, effects and compositing are drawn and staged on a 2D canvas. The people must be complete, fully rendered characters — not stick figures, skeleton diagrams, floating body segments or a few outline strokes.

Every main character must be designed as a finished character asset before animation begins:

- a complete head with skull/jaw construction, ears, eyes, eyelids, brows, irises, pupils, nose, mouth and expression shapes;
- complete adult anatomy and readable proportions: neck, shoulders, ribcage, pelvis, elbows, wrists, hands, fingers, thighs, knees, calves and feet;
- designed hair built from layered locks, clumps and flyaways;
- complete costume construction, seams, collars, cuffs, fastenings, folds, layered fabrics, accessories and footwear;
- material-specific colour, form shadows, cast shadows, reflected light, rim highlights, texture and varied ink weight;
- props designed with silhouette, perspective, material response, bevel/highlight logic and contact shadows.

The 3D appearance comes from the **2D artwork itself**: volume-aware drawing, overlapping forms, foreshortening, perspective, cel-shaded light and shadow, controlled gradients, reflected colour, surface detail and consistent highlights. It is not a 3D environment with a few lines pasted over it.

## Hard rules

1. The final stage is 2D. Do not build a 3D city or a Blender mesh scene as a substitute for a designed 2D background.
2. No stick figures, wireframes, unshaded outlines, placeholder mannequin people, flat icon characters or primitive-only props.
3. No crude SVG cut-out puppet as the final character. A rig may assist animation, but the character must read as one coherent, fully illustrated person with carefully drawn overlaps and no visible hinge gaps.
4. Do not imitate or trace the downloaded reference frames. Study broad craft only: anatomy, silhouette, posing, facial acting, colour grouping, perspective, lighting and timing.
5. Keep the original reference videos and extracted frames out of the final release. Do not include source audio.
6. Every shot needs human review. Automated QA can verify frame count, image variation and output format; it cannot certify professional character design or animation quality.

## 2D production stack

- **Krita** — character concept art, painted texture passes, cleanup and high-resolution layered artwork.
- **Tahoma2D / OpenToonz** — 2D X-sheet, exposure timing, drawing levels, camera moves, compositing and traditional animation review.
- **SVG + CairoSVG** — deterministic code-authored vector passes for the procedural prototype, with full colour and shading rather than line-only strokes.
- **FFmpeg / ffprobe** — image-sequence encoding and delivery verification.
- **yt-dlp** — downloads explicitly licensed, creator-published animation references to temporary storage. The downloader selects video-only formats; it does not request the source music.

The code renderer is a procedural proof of the intended 2D art construction. It is not a claim that procedural curves alone can replace a character artist, animator or cleanup artist for a complete series.

## Licensed visual references

The first visual study uses the **Morevna Project**, an actual independent open-source cyberpunk anime project:

- *The Beautiful Queen Marya Morevna: Demo* — the creator states that the visual footage is CC BY 3.0; its soundtrack has a separate CC BY-NC-SA 3.0 licence. The reference downloader therefore retrieves video-only and never downloads or uses the soundtrack.
- *Morevna Episode 3.0.2* — its official upload declares CC BY-SA 4.0. It is also downloaded video-only for study. Any later redistribution of reference material would require the appropriate attribution and share-alike treatment; reference footage is not included in this project's releases.

The downloader checks that the expected licence declaration is present in the creator's video description before it downloads. If it cannot verify the declaration, it fails closed. It stores the video and temporary frame contact sheets under the GitHub runner's temporary directory, not in the repository or final MP4.

Attribution for the visual references:
- “Animation by Morevna Project” — *The Beautiful Queen Marya Morevna: Demo*, visual footage CC BY 3.0.
- Morevna Project — *Morevna Episode 3.0.2*, CC BY-SA 4.0.

Sources and licence pages:
- https://morevnaproject.org/anime/demo/
- https://www.youtube.com/watch?v=PThy9_RZQ8c
- https://www.youtube.com/watch?v=ecVv2IB7f5k
- https://creativecommons.org/licenses/by/3.0/
- https://creativecommons.org/licenses/by-sa/4.0/
- yt-dlp format selection: https://github.com/yt-dlp/yt-dlp#format-selection

## Review target

The CI smoke test is 6 seconds, 1280×720, 30 fps, H.264. It must contain a fully coloured, fully shaded, full-body character in an intentionally designed 2D location, with at least one designed prop and visible motion across frames. The MP4 is a review sample, not the final claim of studio-level quality.
