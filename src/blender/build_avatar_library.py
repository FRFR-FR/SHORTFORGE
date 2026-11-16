#!/usr/bin/env python3
"""Build reusable male and female avatar .blend files with emotions and pose presets."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from avatar_system import add_rigged_avatar, avatar_library_manifest

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--male", required=True)
    parser.add_argument("--female", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    manifest = avatar_library_manifest()
    entries = []
    for avatar_id, model in (("hero_male", args.male), ("hero_female", args.female)):
        bpy = __import__("bpy")
        bpy.ops.wm.read_factory_settings(use_empty=True)
        avatar = add_rigged_avatar(model, avatar_id, location=(0, 0, 0), rotation_z=0, scale=1.0)
        bpy.context.scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in {x.identifier for x in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items} else "BLENDER_EEVEE"
        blend_path = output / f"{avatar_id.replace('_', '-')}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), compress=True)
        entries.append({
            "id": avatar_id,
            "blend_file": blend_path.name,
            "bytes": blend_path.stat().st_size,
            "rig_bones": len(avatar["armature"].data.bones),
            "emotions": manifest["emotions"],
            "poses": manifest["poses"],
            "asset_license": "CC0-1.0",
            "asset_attribution": "Quaternius — Universal Base Characters Standard",
            "controls": "Import the .blend as a library or use SHORTFORGE avatar_system.apply_pose() and apply_emotion()",
        })
        print(f"SHORTFORGE_AVATAR_OK {blend_path} bones={len(avatar['armature'].data.bones)}")
    manifest["avatars"] = entries
    (output / "avatar-library.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("SHORTFORGE_AVATAR_LIBRARY_OK")

if __name__ == "__main__":
    main()
