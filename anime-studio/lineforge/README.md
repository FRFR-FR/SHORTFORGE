# LINEFORGE — Hand-drawn 2.5D anime, authored as code

LINEFORGE replaces the earlier SVG cut-out character experiment. It is a separate production path inside SHORTFORGE and does not alter the existing vertical Shorts renderer.

## Non-negotiable art method

The protagonist is drawn as individual Grease Pencil strokes in Blender's 3D world. The renderer creates a new Grease Pencil drawing for every output frame. Face contours, eyelids, irises, pupils, brows, nose, mouth, hair locks, garment seams, fabric folds, knuckles, fingers, hatching, rim lights, impact lines and speed strokes are authored as code-defined paths.

The character has:
- zero character meshes;
- zero SVG character planes;
- zero raster character drawings;
- zero cut-out body parts or sprite assemblies.

The only character art is the line work. Every stroke contains multiple 3D points, line-weight pressure, depth, colour/material and frame-dependent deformation. The face and body have deliberately varying depth; a perspective camera, parallax, camera movement and real 3D lights create the 2.5D volume. Environmental architecture is actual 3D geometry.

This is not a claim that a short procedural sample equals studio animation. The render is a technical and visual proof of the new line-art pipeline; it must pass human review before it is called production-ready.

## Free/open-source software comparison

| Software | What it is best at | Why it is / is not in this pipeline |
|---|---|---|
| Blender 4.5.16 LTS — Grease Pencil v3 | Traditional frame-by-frame drawing directly in 3D space; stroke depth, layers, materials, modifiers, lighting, camera and compositor | **Primary renderer.** Matches the required drawn characters in an actual 3D environment. Pinned to a tested LTS build. |
| Krita | Raster frame-by-frame animation, brush rendering, onion skinning and drawing/cleanup | Companion for hand-drawn frame studies and paint/line cleanup. Not the 3D scene renderer. |
| Tahoma2D 1.6.3 | Traditional 2D production, brushwork, palettes, X-sheet, FX nodes, perspective grid and compositing | Companion for 2D animation studies and review. Its cut-out capability is explicitly not used for characters here. |
| OpenToonz | Full traditional 2D production/X-sheet and compositing workflow | Relevant alternative, but not needed alongside Tahoma2D for the initial code-only renderer. |
| Pencil2D | Lightweight, straightforward hand-drawn bitmap/vector animation | Useful learning tool; less suited to the desired 3D camera/world integration. |
| Synfig | Vector interpolation, layers, bones and rig/cut-out animation | Not used: the central brief explicitly rejects vector-tween and cut-out characters. |

### Installed runtime

The GitHub Actions production job installs:
- Blender 4.5.16 LTS from the official Blender release mirror;
- FFmpeg/ffprobe for encoding and verification;
- Krita and Tahoma2D as free companion tools for frame-by-frame review and 2D clean-up studies.

The output itself is generated entirely by the Blender Python script. No AI image generation, purchased assets, stock footage, imported anime frames, SVG character pieces or downloaded character models are involved.

## Visual research and direction checklist

The references are studied for high-level craft, not copied. Characters, scene designs, scripts, compositions and effects in LINEFORGE are original.

### Cyberpunk: Edgerunners — Studio Trigger

Observed targets:
- sharp, readable silhouettes and graphic posing;
- energetic shape rhythm in hair, clothes and action arcs;
- intense colour contrast and purposeful neon accents;
- direct, legible staging with bold changes of scale;
- expressive facial close-ups and strong held poses;
- use of drawn effects and graphic imagery to make impacts feel immediate.

### Jujutsu Kaisen — MAPPA

Observed targets:
- action that communicates weight, distance and momentum;
- strong camera placement, perspective distortion and foreshortening;
- clear contact poses, anticipation, follow-through and recovery;
- variable line energy, rough impact emphasis and controlled visual abstraction;
- detailed facial acting between action beats;
- effects that support the movement instead of obscuring it.

The MAPPA / Crunchyroll interview notes that the production's action relied on animators from Japan and around the world. That is a useful production lesson: strong action depends on individual animation decisions, not on a single automatic effect.

### Additional reference disciplines

- *Mob Psycho 100*: expressive acting, unusual line shapes and freedom for individual animation styles.
- *Akira*: dense architectural perspective, rich mechanical detail, strong environmental drawing and believable weight.
- *Fog Hill of Five Elements* and other Chinese action animation: ink-like motion, highly designed silhouettes and forceful action staging.
- *Arcane* (international 3D/2D hybrid, not anime): painterly surface treatment, 3D light design and layered atmospheric depth.

### Shot-by-shot quality gate

1. **Draftsmanship:** recognisable adult anatomy, coherent head construction, joints, fingers, facial planes and clothing construction; no stick figures.
2. **Line control:** varied outer/inner weights, tapered line endings, clean overlaps, intentional broken lines, selective roughness and no mechanical uniform outline.
3. **Frame drawing:** each frame has its own Grease Pencil drawing; key poses and breakdowns must visibly change rather than slide a static drawing around.
4. **Volume:** 3D point placement, depth ordering, foreshortening, cross-contours, head/body turn, perspective camera and parallax.
5. **Face:** eyelids, iris/pupil, brows, nose bridge/tip, mouth corners, ears and expression all change with the acting.
6. **Hair and fabric:** separate locks, clumps, flyaways, seams, folds, tension and follow-through; no single helmet-shaped hair mass.
7. **Motion:** anticipation, readable key poses, arcs, spacing, smear/impact drawings, hold/recovery, secondary motion and camera shake used with restraint.
8. **Lighting and colour:** controlled palette, coloured rim strokes, shadow hatching, atmospheric depth, bloom that never erases the ink.
9. **Environment:** real 3D architecture with layered detail, perspective, ground reflections, practical lights and foreground/midground/background separation.
10. **Compositing:** readable contrast, coherent exposure, deliberate effects, no muddy glow or excessive particles.
11. **Delivery:** horizontal 16:9, 720p review, 30 fps output, H.264 MP4, frame count and codec verified.
12. **Human review:** contact sheet and actual playback must be inspected for anatomical errors, line popping, temporal wobble, unclear staging and bad contact.

Automated QA can verify that the character is actually made from Grease Pencil strokes and that the render is complete. It cannot certify that the animation is as good as *Edgerunners* or *Jujutsu Kaisen*; that requires visual review and further redraw passes.

## Licensing and asset policy

Only open-source software is installed. Production drawings are newly authored in code. No anime scene, model sheet, key animation, logo, soundtrack, character, or copyrighted background is copied into the project. Reference images/footage are for analysis only and are not redistributed.

Software references:
- Blender Grease Pencil manual: https://docs.blender.org/manual/en/4.5/grease_pencil/introduction.html
- Blender Grease Pencil animation: https://docs.blender.org/manual/en/4.5/grease_pencil/animation/introduction.html
- Krita animation manual: https://docs.krita.org/en/user_manual/animation.html
- Tahoma2D: https://tahoma2d.org/
- Tahoma2D source/licensing: https://github.com/tahoma2d/tahoma2d
- Pencil2D: https://www.pencil2d.org/about
- Synfig: https://www.synfig.org/

Visual research:
- Studio Trigger / Netflix announcement: https://about.netflix.com/en/news/netflix-cd-projekt-red-and-studio-trigger-come-together-for-global-anime-cyberpunk-edgerunners
- *Cyberpunk: Edgerunners* production feature: https://www.awn.com/animationworld/cyberpunk-edgerunners-vibrant-ode-retro-anime
- Crunchyroll interview with MAPPA leadership on *Jujutsu Kaisen*: https://www.crunchyroll.com/hi/news/interviews/2022/8/8/interview-manabu-otsuka-hiroshi-seko-and-hiroaki-matsutani-on-the-future-of-jujutsu-kaisen
- Crunchyroll interview with *Mob Psycho 100* director Yuzuru Tachikawa: https://www.crunchyroll.com/news/interviews/2019/3/30/interview-mob-psychos-director-is-changing-hearts-and-getting-in-trouble-with-the-president-of-bones
