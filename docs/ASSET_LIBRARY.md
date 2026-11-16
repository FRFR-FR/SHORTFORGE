# SHORTFORGE asset library

SHORTFORGE imports complete, authored environments instead of relying on low-detail primitive blockouts.

## Prebuilt environments

| ID | Scene | Source | Terms |
|---|---|---|---|
| `house_of_chores` | Blender 4.3 — House of Chores | [Official Blender Demo Files](https://www.blender.org/download/demo-files/) | CC-BY as listed by Blender. Preserve creator credit and check the source file's own credit notice before redistribution. |
| `dogwalk` | Blender 4.5 — DOGWALK splash scene | [Official Blender 4.5 release page](https://www.blender.org/download/releases/4-5/) | Conservatively treated as CC-BY-SA for the splash artwork. |

The asset fetcher downloads the full `.blend` file from Blender's official mirror, validates the Blender file signature and minimum byte size, records SHA-256, and places licence/source attribution in `asset-manifest.json`. Environment files stay in the runner cache rather than adding hundreds of megabytes to Git history.

## Reusable textured avatar library

The character pipeline uses the free **Quaternius Universal Base Characters — Standard** male and female humanoids. The original pack is dedicated under CC0 1.0. The imported glTF files include PBR skin/suit, hair, eye, normal and roughness texture maps. The source rig has 65 named joints and approximately game-ready character geometry.

Each avatar is converted to a standalone Blender `.blend` project with its textures packed internally, so it remains reusable after the Actions cache is cleared.

Every saved avatar includes:
- 7 facial emotions: neutral, happy, sad, angry, surprised, scared, determined.
- 8 reusable body poses: neutral, wave, point, confident, thinking, celebrating, running, crouching.
- Original PBR materials and texture maps preserved.
- Facial expression shape keys plus a seven-shape mouth expression set.
- Named, reusable pose and emotion controls in `src/blender/avatar_system.py`.
- JSON metadata with the source, licence, skeleton, supported emotions and poses.

The pipeline builds both male and female avatar assets before it starts the episode render. It then imports the selected saved .blend from that reusable library. Each production Release includes `avatar-library.zip`, the two standalone avatar .blend files, `avatar-library.json`, `asset-manifest.json`, and the finished MP4. The same saved avatars can be brought into later projects without regenerating them.

## Use the library in a new project

Choose `character.model` as `male` or `female`. For each shot, add one `pose` and one `emotion` value from the lists above. This stores expressive character direction in the story JSON rather than hard-coding a character into the renderer.

## Asset terms

Quaternius character assets remain CC0. Blender Studio environment credits and licences remain attached to the imported scene in the manifest and render release notes. SHORTFORGE does not claim ownership of third-party source assets. Preserve each source asset's own terms and attribution when distributing derivative environments or project files.
