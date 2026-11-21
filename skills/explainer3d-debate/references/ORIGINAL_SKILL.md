---
name: explainer3d
description: Makes vertical (9:16) 3D cartoon "explained" videos in the style of the wind-turbine Short — one continuous flying camera, toon-shaded outlined 3D props, step-by-step "problem → fix → named term" narration, black-box captions and big pop-up keywords. Use for any request like "explain how X works" as a 3D video/Short/Reel. Renders locally with three.js + headless Chromium + ffmpeg; no other assets needed.
---

# 3D explainer video (Short/Reel, 60–130 s)

Output: `*.mp4` 540×960 30 fps (silent unless a TTS engine exists) + `*.srt` + `narration.txt` (script to voice). Look = flat toon colour, thin dark outlines, blue cast shadows, pale-blue hills, outlined white clouds, wind dashes, grain. Complete visual reference: see the **Visual style bible** section at the end of this file.

## Token-saving rules (follow strictly)
1. **Never read `engine/lib.js` or `render.mjs`.** The API below is complete. Only edit your own `story.js`.
2. Write the plan as a ≤25-line beat table in your head/one short message, then write **one** `story.js` in one tool call (start from `template/story.example.js`).
3. QA with **one** contact sheet (`--sheet`, 1 image, one frame per beat), fix by small edits to story.js, re-sheet at most twice. Never view individual frames/video unless the sheet shows a bug you can't locate.
4. Render the final once. Default 540×960; use `--w 720 --h 1280` only if the user asks for HD (≈1.8× slower).
5. Final answer: 2–3 lines + the files. No recap of steps.

## Workflow
```
bash scripts/setup.sh                                   # 5 s: ffmpeg/node/playwright/TTS check
cp template/story.example.js /work/story.js             # edit
node scripts/render.mjs /work/story.js /work/out.mp4 --sheet   # QA sheet → out_sheet.jpg (view once)
bash scripts/voice.sh /work/story.js                    # only if setup printed a TTS engine → narration.wav + timings.json
node scripts/render.mjs /work/story.js /work/out.mp4 [--audio /work/narration.wav]   # ~3.5× realtime on 2 cores
```
Deliver mp4 + srt + narration.txt (`beats.txt` from voice.sh, or join the `say` lines). If no TTS: say so in one line and tell the user to paste narration.txt into any voice tool (CapCut / ElevenLabs) — timing is 2.6 words/s, so it fits; `.srt` has beat timings.

## Script formula ("reinvent it" — copy this structure)
- **Hook (beat 1):** "If you [simplest crude version of the thing], you've got yourself a [thing]." Starts mid-action; no intro, no "today we'll learn".
- **Loop of 10–14 steps:** each step = *problem* (short, concrete, visible) → *fix* (a named real engineering term) → the fix creates the next problem ("Better wind, bigger problem."). Every fix is physically shown, never just said.
- **Beat = 1–2 sentences, 6–22 words**, plain spoken words, no jargon until the keyword card names it. ~2.6 words/s → 100–130 s ≈ 270–340 words ≈ 25–35 beats.
- **Keyword card on ~every second beat**: red = problem/failure ("no wind back here", "too slow", "messy air"), black = solution/term ("yaw control", "pitch control"). 1–3 words, lowercase, appears *as the word is spoken* (anchor word).
- **One everyday analogy inset** (bike gears, hand out of a car window) via `E.inset` + a quick 3D prop; 1 per video.
- **Escalate** the last third (weather turns to storm, danger: lightning, overspeed), then **close the loop**: last line "…You've officially built a [thing]." and the camera returns to the hook's opening shot so the Short loops.
- Pick a topic whose parts physically move/attach (machines, structures, vehicles, body-as-machine, systems). Facts must be correct: research first if unsure (WebSearch ≤2 queries).

## Visual grammar
- **One continuous shot, never cut.** Every beat sets `cam:{p,l}` (position, look-at); the engine flows between beats with a spline so the camera is always moving: sweep in to detail (gears, bolts), pull out to the full object, tilt up a tower, orbit the head. Alternate wide ↔ macro every 1–2 beats.
- Vertical safe zones: captions top-left (y≈10%), keyword at y≈66%, **bottom 16% empty** (platform UI). Keep the subject in the middle 60%.
- Objects **pop in** (`E.show`) with overshoot when mentioned; the world is built up around a single hero object that stays in place and *grows more complex each beat*.
- Annotations: lime-green arrows/arcs = forces/motion/fix, red arrows/dots/debris = problem; red tips on moving parts; red dots = noise/mess; blue-white dashed streaks = air.
- Colour: grass #86c24a, tower cream #e9e3d4, machine orange #f2a31f, generator blue #3f86c6, red #e8452c, lime #a8d12a, ink #1b1815. Use these via `E.PAL`.
- Mood: `E.mood(t0,t1,1)` = storm (grey sky, dim light, rain). `E.flash(t)` for lightning.

## story.js contract
```js
export const meta = { cam0:{p:[6,4,9], l:[0,3,0], fov:52}, wps:2.6 };   // start camera
export function setup(E){ E.ground(); /* road, trees, houses, hero parts (put in E.state.x) */ }
export const beats = [ { say:"...", key:["yaw control","term","yaw"], cam:{p:[..],l:[..],fov:50}, build(E,b){ ... } }, ... ];
```
Top level must not touch `E` or browser globals (voice.sh imports the file in Node). Units ≈ metres, y up, camera looks toward −z, hero faces +z.

`b` (beat): `b.t0 b.t1 b.dur`, `b.f(0..1)` time inside beat, `b.word('lever')` time that word is spoken.

**Engine API `E`** (all return three.js objects; add with `E.add(obj[,parent])`, place with `E.at(obj,x,y,z)` or opts `{x,y,z,rx,ry,rz,s,outline,cast}`):
- Shapes (toon+outline): `box(w,h,d,c,o) cyl(rt,rb,h,c,o) sph(r,c) cone(r,h,c) tor(r,tube,c) ext([[x,y]..],depth,c) rbox(w,h,d,radius,c) mesh(geometry,c)`; `grp(...kids)`; colours are hex numbers (`E.PAL.*`).
- Props: `tree(scale,seed) house() car(c) pole(h) road(len,w) tower(h,rBase,rTop) slab(r,h) nacelle(w,h,l) generator(len,r,c) gear(r,teeth,w,c) vane() bolt(from,to) rotor({n,len,hubR,boards,blade:{len,c0,c1,tw0,tw1,tip}}) blade({...}) board(len,w,th) ground()`. `rotor().userData.blades[i].rotation.y = pitch` pitches a blade. Rotor lies in XY facing +z; spin on `'z'`.
- Annotation: `arrow(from,to,color,{w})` and `arc(center,r,a0,a1,color,axis)` both expose `.userData.set(p∈0..1)` to draw them on; `particles(n,(i,t)=>[x,y,z,scale]|null,color,{size,kind:'sph'|'box',box})` for dots/debris/streaks.
- Timeline (absolute-time, deterministic): `show(obj,t0,t1?,pop?)` pop-in/out · `anim(t0,t1,(p,t)=>{...},'io'|'out'|'lin'|'back')` (fn runs every frame with p clamped 0..1 → must be an idempotent setter, e.g. `obj.rotation.y = p*2`) · `spin(obj,'z',rpsOrFn)` · `mood(t0,t1,0..1)` · `flash(t,dur)` · `inset(t0,t1,(ctx,r,p,t)=>{…draw in circle…},{x,y,r})` · `keyword(text,'problem'|'term',t0,t1)` (usually via the beat's `key`) · `E.shake` handheld amount.
- Beat keys: `key:[text, kind, anchorWord]`.

## Quality checklist (check on the sheet, one pass)
Hero object recognisable in every frame · each beat has a visible *change* · keyword colours match meaning · text never covers the subject centre · no frame is a blank sky/ground · camera positions not inside geometry · every term in `key` is spoken in `say` · loop ends where it began.
Common fixes: object invisible → camera inside/behind it, move `p`; text clipped → shorten keyword; flat look → add `E.tree`/`house`/`car` context in `setup`, vary camera height.

---

# Style bible — extracted frame-by-frame from the reference Short (128 s, 720×1600, 30 fps, mono AAC)

**Format.** Vertical 9:16, ONE continuous shot (scene-cut detector fires only at the loop seam). Constant voice-over, flat loudness (no music bed), ≈155 wpm (2.6 words/s), ~330 words. ~14 problem→fix steps, ~30 beats, avg 4.3 s per beat. Video loops: last line ("You've officially built a wind turbine") visually returns to the opening crude 3-blade pole.

**Rendering look.** 3D scene, flat toon colour with 2–4 tonal bands, thin near-black outline (≈2–3 px at 960 high), soft blue cast shadow on the ground, slight paper grain. Sky = blue gradient to pale horizon; pale-blue layered hills at horizon (follow camera pitch); 4–6 white outlined cartoon clouds fixed in screen space drifting slowly; short white wind dashes streaming across the screen; green ground with faint blotchy mottling; grey road with dashed centre line crossing the ground; low-poly rounded trees (clustered spheres), small houses/cars/power poles for scale. Storm = grey gradient sky, dim light, diagonal rain streaks, grey clouds.

**Palette.** grass #86c24a · concrete/tower cream #e9e3d4 · machine orange #f2a31f · blue generator #3f86c6 · red accents #e8452c · lime annotation #a8d12a · ink #1b1815 · wood #c9772f · sage green gearbox #b7d3b0.

**Camera.** Never stops moving and never cuts: macro push-ins on mechanisms (generator coils, gears, bolts at tower base), pull-backs to the full hero, tilt up a tower, top-down on yaw rotation, low-angle looking up a blade, orbit around the hub. Wide→macro→wide rhythm; fov ≈50; slight handheld drift. Hero object stays the same object all video and accumulates parts (blades → generator → tower → slab → vane → yaw motors → airfoil + twist → gearbox → tilt → lightning receptor → serrations → pitch motors).

**Text.** (1) Captions: top-left, y≈10%, 2–3 stacked lines, each in its own tight black box (88% opacity), white semi-bold sans ≈2.8% of frame height, word-by-word reveal, ≤22 chars/line. (2) Keyword card: lowercase extra-bold sans, centred at y≈66%, ~85% frame width max, white halo; red = problem/failure, near-black = solution/term; pop-in with overshoot (~0.2 s), holds ~2 s, fades; appears exactly when the word is spoken. (3) Bottom ~16% kept free (platform UI).

**Annotations.** Lime arrows/arcs for forces & motion (growing on, with arrowhead), red arrows for pushes/problems, red dots = noise/air mess, red slivers = splintering fence boards, ring/arc swept by blade tip vs root to compare speeds, dashed airflow streaks over an airfoil, blue/red thermometer-style "noise" meter, white circular inset with bike gear/chain analogy (black outline), an orange hand tilting out a red car window as the pitch analogy.

**Beat map of the reference (copy the rhythm):**
1 hook: 3 wooden blades on a pole + generator → *a wind turbine* · 2 tree blocks wind → *no wind back here* (red) · 3 taller tower → *cleaner wind up here* · 4 pole bends → *long lever* (red) · 5 concrete slab + bolts + arrows pushing down → *concrete slab* · 6 wind swings sideways, blades slow → 7 wind vane → *wind vane* · 8 yaw motors, green arc rotating head → *yaw motors*, *yaw control* · 9 blades are fence boards (splinters) → *fence boards* (red) · 10 airplane-wing shape, airflow dashes, lift arrow → *airplane wings* · 11 tip vs root circles → *bigger circle*, *time*, *different angle*, *twist* · 12 gearbox: blue generator "too slow" (red) → gears + bike inset → *gearbox*; "15→1" counter "fast turns" · 13 gust bends blade near tower → *freeze*, *tilt the shaft*, *more room* · 14 lightning: metal target at tip, conductor down tower → *lightning*, *conductor to ground* · 15 whoosh: saw teeth, red noise dots → *messy air* (red) → *quieter* · 16 storm: rain, grey sky → *storm*, *too fast* (red) → *pitch motors* → hand-in-car analogy → *pitch control*, *feathering*, *shut down* · 17 finale: "You've officially built a wind turbine." → cut back to beat 1 (loop).

**Narration voice.** Calm, matter-of-fact, second person ("you stick", "you put"), short declaratives, sentence ends on the key noun, causal connectors ("Then", "So", "Now"), one-line aphorism per transition ("Better wind, bigger problem.").