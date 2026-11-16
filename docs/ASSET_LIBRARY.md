# SHORTFORGE asset library

SHORTFORGE now prefers full authored environments over primitive placeholder sets.

## Prebuilt environments

| ID | Scene | Source | Terms |
|---|---|---|---|
| `house_of_chores` | Blender 4.3 — House of Chores | [Official Blender Demo Files](https://www.blender.org/download/demo-files/) | Listed as CC-BY. Preserve creator credit and check the source file's own credit notice before redistribution. |
| `dogwalk` | Blender 4.5 LTS — DOGWALK splash scene | [Official Blender 4.5 release page](https://www.blender.org/download/releases/4-5/) | Splash artwork credited CC-BY-SA. Treat derived art under the applicable share-alike terms. |

The fetcher downloads complete `.blend` files to `.cache/shortforge-assets/environments`, checks the Blender file signature and minimum file size, records SHA-256, and places a source/licence attribution record in `asset-manifest.json`. This avoids committing hundreds of megabytes of scene files into Git.

## Reusable avatars

The avatar library uses the free **Quaternius Universal Base Characters — Standard** male and female humanoids. The source models are dedicated under CC0 1.0. Each imported rig contains 65 named joints and is stored as a standalone Blender `.blend` asset.

Every saved avatar has:
- 7 facial emotions: neutral, happy, sad, angry, surprised, scared, determined.
- 8 reusable body poses: neutral, wave, point, confident, thinking, celebrating, running, crouching.
- Facial expression controls and body pose presets available through `src/blender/avatar_system.py`.
- A JSON manifest with asset source, licence, rig, emotions and poses.

The pipeline creates the two avatar `.blend` files before rendering the short, then loads the selected saved avatar library file into the scene. Each render Release includes `avatar-library.zip` and both Blender avatar files so future projects can reuse the same character rigs without rebuilding them.

## Use the library in a new project

Choose `character.model` as `male` or `female` in your project JSON. Shots can specify `pose` and `emotion` values from the lists above. Do not invent new bone names; the pose bank uses the Quaternius 65-joint names.

## Asset terms

The external models and environments are not made proprietary by SHORTFORGE. Preserve each source asset's own terms and attribution when redistributing project files, derivative assets or media. The final MP4 is an original SHORTFORGE edit, but its visual environment remains subject to its source licence.
