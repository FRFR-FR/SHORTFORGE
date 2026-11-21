# ANIMEFORGE production standard

## Visual language

The target is original premium cyberpunk action anime: confident line hierarchy, clearly separated silhouettes, saturated coloured practicals, painted value groupings, strong facial acting and camera movement with physical motivation. Use cyan, magenta, ultraviolet and warm amber as an accent family, but make each episode's character and location palettes coherent.

Do not use one generic neon city for every shot. Build the set around the action. Include foreground architecture, middle-distance landmarks, deep skyline layers, readable street/room geography, signage, cables, pipes, vehicles, crowds, haze, wet-surface reflections and practical light sources where appropriate. Reuse the scene kit as a foundation, not as a substitute for authored environment art.

## 2.5D scene construction

1. Background plate / skyline: painted environment art or designed Three.js geometry, positioned at a distant depth.
2. Midground: buildings, vehicles, crowds, props and environmental action.
3. Character/action plane: layered 2D character artwork with articulated pivots or a rigged GLB. Keep it readable from the chosen camera.
4. Foreground: signs, rails, cables, rain streaks, debris and silhouettes used for controlled parallax and depth.
5. Camera: motivated trucking, push-ins, orbits, crane moves and perspective changes. Avoid motion that obscures the action.
6. Post: cel-shaded material response, line hierarchy, bloom, restrained grain and colour grade. Effects support the drawing; they must not hide weak staging.

## Character art contract

For each main character, provide a turnaround, face/expression sheet, colour key, outfit detail sheet and either:
- a rigged GLB with a usable skeleton and named animation clips; or
- separated transparent artwork for head/hair, torso, upper/lower arms, hands, upper/lower legs, feet and important accessories, with local pivot coordinates.

Keep source layers at 2K–4K or better for 1080p masters. The art must be original and remain consistent between scenes. The fallback procedural puppet is only for engine validation. Claude-authored original vector layers are the default episode art path; they must be detailed, transparent, consistently proportioned and rigged through named joints.

## Episode and shot design

Every shot records start time, duration, physical action, camera move and emotional beat. Each action should have anticipation, a clearly readable key pose, contact or reaction, and follow-through. Screen direction, eyelines, props and geography must remain continuous unless a motivated cut establishes a new axis.

A 30 fps episode has exactly duration_seconds × 30 frames. Prefer motivated shot changes at 2–7 second intervals; no shot may exceed 12 seconds in the first release of the engine.

## Audio

The renderer can mux a supplied episode-local audio file. Music, narration and dialogue generation are off by default. Dialogue should be authored per character, recorded or generated through a separately configured licensed voice system, then supplied as episode-local audio before final mux.

## Release readiness

Technical QA is necessary but insufficient. A reviewer must inspect the contact sheet and full video for anatomy, mouth/eye placement, hand contact, foot planting, perspective, depth order, line consistency, frame pacing, emotion, lighting and visual continuity. A master may only declare assets_complete=true when the actual original character and environment assets are present.
