---
name: explainer3d-debate
version: 1.0.0
description: Production skill for long-form, horizontal, multi-character 3D explainer debates. Extends the uploaded explainer3d visual language into a 5-minute, multi-location, three-voice debate using SHORTFORGE's Blender final renderer and rigged humanoid library.
---

# Explainer3D Debate — SHORTFORGE production skill

This is the repository implementation of the supplied explainer3d skill. The source skill and its source style bible are preserved in references/. It retains the original preference for a designed 3D world, a moving camera, clear physical demonstrations, bold keyword graphics, restrained narration and no transcript captions by default. It deliberately extends the source's 60–130 second, vertical, single-camera, single-location explainer format for the user's explicitly requested long-form debate.

## Project contract

- **Format:** horizontal 16:9, 1280×720, 30 fps, H.264 MP4.
- **Duration:** exactly 300 seconds for the Glasswing episode; project schema permits 60–600 seconds.
- **Final renderer:** Blender EEVEE Next. FFmpeg is used for audio assembly, final encoding and media verification. Three.js remains optional previs; it is not the final-render path.
- **Characters:** imported, fully rigged and textured humanoids from SHORTFORGE's existing avatar library. No stick figures, flat 2D substitutes, or primitive-only people. Distinct wardrobe treatments, facial expressions, gestures, blocking and silhouettes are required.
- **Voice casting:** Liam = Kokoro am_liam; George = Kyutai Pocket TTS George; Eponine = Kyutai Pocket TTS Eponine. Speaker identity must remain consistent from first line to last. Fail on unavailable requested voice; never silently substitute another voice.
- **Sound:** dialogue and purposeful diegetic effects only. No background music unless the user explicitly requests it. Keep voice intelligible and mix peaks safely.
- **Captions:** no burned-in dialogue captions by default, matching the source skill. Deliver a separate SRT. Use restrained speaker IDs, role labels, and short keyword cards as visual graphics, not as a full transcript.
- **Visual policy:** original characters, original sets, original blocking, original dialogue and rights-cleared source assets. Do not reproduce a reference creator's characters, script, shot sequence or distinctive visual signature.

## Debate design rules

A debate is not three narrators taking turns to agree. Each speaker must hold a coherent position and challenge the others with reasons:

1. **Host / evidence examiner (Liam):** introduces the question, checks the headline against evidence, explains the programme, and delivers a measured verdict.
2. **Open-source maintainer (George):** challenges overclaiming, explains the human maintenance bottleneck, questions patch quality and funding, and highlights dual-use risk.
3. **Critical-infrastructure defender (Eponine):** explains why discovery speed matters, describes coordinated defence and the value to high-impact sectors, and argues that early warning can materially reduce exposure.

Each position must be steel-manned. Let a speaker acknowledge the strongest point from another side before challenging its conclusion. Do not use fake disagreement, repeated summaries, strawmen or manufactured quotations.

## Fact-first writing

- Research the named model, initiative, dates, partner list, reported results and example vulnerabilities before writing dialogue.
- Maintain FACT_CHECK.md with direct source URLs, what each source actually supports, dates, and caveats.
- Attribute programme totals to the organisation reporting them; do not present partner counts or discovered-vulnerability counts as independently audited facts unless that is independently established.
- Distinguish model capability, reported demonstration, confirmed vulnerability, published patch, deployment and real-world risk reduction. These are different claims.
- Do not claim that one model “saved the internet” as a literal fact. It may be the provocative question, but the script must examine and qualify it.
- Do not invent dialogue as a quote from real people. All debate speakers are fictional presenters/experts unless explicitly identified otherwise.

## Visual story grammar

Use the source skill's physical-explanation approach, adapted to a landscape, editorial, multi-location format:

- The opening begins mid-action with a strong visual hook, not a logo or title animation that delays the premise.
- Build a visual argument: threat surface → discovered flaw → exploit chain → defensive workflow → deployment gap → balanced verdict.
- Use multiple deliberately art-directed locations. Each location communicates its speaker's lived perspective, not merely a generic background.
- Make the camera glide, push, orbit, rack perspective, or reframe inside each scene. Use a motivated cut only when the debate changes location, viewpoint or evidence.
- Use wide, medium, close, over-shoulder and macro framings. Maintain eyelines and screen direction across adjacent shots.
- Give each speaking character a readable performance: planted feet, anticipation, clear gesture, facial emotion, head movement and follow-through. Background characters must not appear frozen or accidentally intersecting.
- Show technical concepts physically: doors and access routes for exploit chains, code workbenches for maintenance, racks and control consoles for infrastructure, and a visible release-and-update pipeline for remediation.
- Place short keyword cards on a subset of beats: red/orange for risk or failure, dark ink/ivory for concepts and mitigations. The keyword must be spoken or immediately explained.
- Every 2–4 seconds, something meaningful should change: actor gesture, expression, monitor state, prop, diagram, camera distance, lighting cue or focus. Avoid arbitrary motion for its own sake.
- Use layered foreground, midground and background; textured PBR surfaces; soft key/fill/rim lighting; clear contact shadows; controlled bloom; restrained depth of field; and an intentional color grade.
- Never use a cube-and-sphere stand-in as a final human. Primitive meshes are acceptable for environmental props, machines, diagrams and architectural dressing.

## Character continuity and casting

The same speaker must look like the same person in every location. The renderer reuses each speaker's same rig, materials, face and accessories. Liam, George and Eponine must be visually and behaviorally distinguishable. Use role-specific styling and props without turning anyone into a caricature. Any additional people are fully rigged supporting engineers, maintainers or operators, with distinct positions and background actions.

Animate the imported rig with the SHORTFORGE avatar API:
- Poses: neutral, wave, point, confident, thinking, celebrating, running, crouching.
- Emotions: neutral, happy, sad, angry, surprised, scared, determined.
- Key pose and emotion transitions at dialogue cue boundaries. Use subtle motion and grounded weight shifts between emphatic gestures.
- Do not let every speaker use the same pose or expression for every line.

## Audio procedure

1. Keep each dialogue turn separate in dialogue.json and preserve exact speaker IDs.
2. Generate Liam with Kokoro am_liam; George and Eponine with the designated Kyutai Pocket TTS voice prompts.
3. Generate per-line clips, preserve line order, insert authored pauses, and build the mixed track plus speaker stems.
4. Fit the assembled speech to the available five-minute timeline with pitch-preserving tempo correction only when necessary. Refuse if the required tempo is outside 0.85–1.15×; edit the script rather than making speech unnaturally fast or slow.
5. Write timings.json and a separate SRT from the final clip durations. Voice timing drives camera and acting; do not guess timings from word count.
6. Verify the final audio sample rate, duration, peak and non-silent content. No background music is added.

## Production workflow

1. Read this skill, the source skill and source style bible, project brief and FACT_CHECK.md.
2. Validate the debate: speakers, argument arc, evidence, source citations, exact target duration and voice assignments.
3. Prepare the licensed, textured male/female avatar assets and build the reusable avatar library.
4. Generate the three requested voices and lock voice timing.
5. Build dedicated Blender locations and stage all people, props, monitors, diagrams and lighting.
6. Render a 10-second smoke test at the final aspect ratio and frame rate. Confirm that every actor loads, facial expressions render, the camera framing is correct and the output can be encoded.
7. Only after smoke passes, render the full 300 seconds at 30 fps (9,000 frames).
8. Run per-frame QA, generate one contact sheet, run ffprobe, listen to the mixed audio and review the contact sheet.
9. Perform the seven specialist reviews: story/debate, camera/editing, character/acting, environments/continuity, art direction/materials, dialogue/sound, and technical delivery. Record Pass / Needs revision / Blocked with timestamp and fix.
10. Re-render after any critical or major issue. Publish MP4, dialogue audio, speaker stems, SRT, script, fact-check notes, manifest, QA report and contact sheet as a GitHub Release. Never use Actions artifacts for large MP4 delivery.

## Seven specialist quality gates

- **Story / debate:** hook in first seconds; distinct and fair positions; accurate claims; meaningful rebuttal; no filler; satisfying nuanced verdict.
- **Camera / edit:** motivated cuts; varied shot scale; clear eyelines; stable screen direction; no camera clipping or dead holds.
- **Character / performance:** full rigged models; correct anatomy; consistent identity; grounded feet; purposeful gestures; readable expressions; no floating, clipping or duplicate parts.
- **Environment / continuity:** each location is specific and detailed; props persist; monitor content matches the current point; actor placement and scale remain coherent.
- **Art / materials:** PBR textures retained; lighting has shape; skin and fabric readable; highlights controlled; cohesive but location-specific palettes; no low-poly placeholder look.
- **Dialogue / sound:** correct three voices; intelligible pacing; correct pronunciation; balanced levels; silence/pause placement intentional; no unrequested music.
- **Technical / delivery:** exactly 16:9, 1280×720, 30 fps and 300 seconds; expected 9,000 frames; valid H.264/AAC; frame QA and contact sheet pass; no missing assets.

## Completion rule

A branch, a workflow, a successful smoke render and a finished five-minute video are four different milestones. Do not report the full video as completed until the MP4 exists, ffprobe confirms its exact properties, frame QA passes, the audio has been checked, the contact sheet has been reviewed and the release upload succeeds. State any unavailable local/GitHub runner, model access or credential dependency plainly.
