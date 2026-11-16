"""Render a cinematic vertical short in a prebuilt Blender environment."""
from __future__ import annotations
import argparse
import json
import math
import os
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from avatar_system import add_rigged_avatar, animate_avatar


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--frames-dir", required=True)
    parser.add_argument("--save-blend", default="")
    return parser.parse_args(argv)


def set_engine_and_quality(scene, config):
    engines = {item.identifier for item in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}
    if "BLENDER_EEVEE_NEXT" in engines:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    elif "BLENDER_EEVEE" in engines:
        scene.render.engine = "BLENDER_EEVEE"
    else:
        raise RuntimeError("SHORTFORGE requires Blender Eevee Next or Eevee for its final renderer")
    scene.render.resolution_x = int(config["width"])
    scene.render.resolution_y = int(config["height"])
    scene.render.resolution_percentage = 100
    scene.render.fps = int(config["fps"])
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.render.use_file_extension = True
    scene.render.threads_mode = "FIXED"
    scene.render.threads = max(1, min(4, os.cpu_count() or 2))
    if hasattr(scene, "eevee_next") and hasattr(scene.eevee_next, "taa_render_samples"):
        scene.eevee_next.taa_render_samples = int(config.get("render", {}).get("samples", 64))
    if hasattr(scene, "eevee") and hasattr(scene.eevee, "taa_render_samples"):
        scene.eevee.taa_render_samples = int(config.get("render", {}).get("samples", 64))
    # AgX preserves highlight detail in HDR environments and emissive practicals.
    transforms = {item.name for item in scene.view_settings.bl_rna.properties["view_transform"].enum_items}
    if "AgX" in transforms:
        scene.view_settings.view_transform = "AgX"
    scene.view_settings.exposure = float(config.get("render", {}).get("exposure", 0.0))
    scene.view_settings.gamma = 1.0
    scene.render.filepath = "//"


def add_area_light(name, location, target, energy, color, size):
    bpy.ops.object.light_add(type="AREA", location=location)
    light = bpy.context.object
    light.name = name
    light.data.energy = energy
    light.data.shape = "DISK"
    light.data.size = size
    light.data.color = color
    light.rotation_euler = (Vector(target) - light.location).to_track_quat("-Z", "Y").to_euler()
    return light


def create_camera(scene, project, avatar_root, total_frames):
    character = project.get("character", {})
    spawn = Vector(character.get("position", [0.0, 0.0, 0.0]))
    aim_height = float(character.get("camera_aim_height", 1.18))
    target = spawn + Vector((0.0, 0.0, aim_height))
    bpy.ops.object.camera_add(location=target + Vector((0.0, -8.0, 3.0)))
    camera = bpy.context.object
    camera.name = "SHORTFORGE vertical cinema camera"
    camera.data.lens = 52
    camera.data.sensor_fit = "VERTICAL"
    camera.data.sensor_height = 24
    camera.data.clip_start = 0.05
    camera.data.clip_end = 1000.0
    scene.camera = camera

    profiles = {
        "wide": (Vector((0.0, -10.2, 4.0)), 45.0),
        "push_in": (Vector((0.0, -8.2, 3.4)), 52.0),
        "close": (Vector((0.0, -6.5, 2.7)), 62.0),
        "side": (Vector((4.1, -7.6, 3.25)), 52.0),
        "low": (Vector((0.0, -8.8, 2.15)), 48.0),
    }
    shots = project.get("shots") or [{
        "start_seconds": 0,
        "duration_seconds": total_frames / scene.render.fps,
        "camera": "wide",
    }]
    for shot in shots:
        start = max(1, int(float(shot.get("start_seconds", 0)) * scene.render.fps) + 1)
        end = min(total_frames, start + int(float(shot.get("duration_seconds", 1)) * scene.render.fps) - 1)
        offset, lens = profiles.get(shot.get("camera", "wide"), profiles["wide"])
        shot_target = target + Vector(shot.get("camera_target_offset", [0.0, 0.0, 0.0]))
        camera.location = shot_target + offset
        camera.rotation_euler = (shot_target - camera.location).to_track_quat("-Z", "Y").to_euler()
        camera.data.lens = lens
        camera.keyframe_insert(data_path="location", frame=start)
        camera.keyframe_insert(data_path="rotation_euler", frame=start)
        camera.data.keyframe_insert(data_path="lens", frame=start)
        # Small motivated tracking drift gives each shot life without handheld wobble.
        drift = float(shot.get("camera_drift", 0.14))
        camera.location.x += drift
        camera.location.z += drift * 0.18
        camera.rotation_euler = (shot_target - camera.location).to_track_quat("-Z", "Y").to_euler()
        camera.keyframe_insert(data_path="location", frame=end)
        camera.keyframe_insert(data_path="rotation_euler", frame=end)
        camera.data.keyframe_insert(data_path="lens", frame=end)

    if camera.animation_data and camera.animation_data.action:
        for curve in camera.animation_data.action.fcurves:
            for key in curve.keyframe_points:
                key.interpolation = "BEZIER"
                key.handle_left_type = "AUTO_CLAMPED"
                key.handle_right_type = "AUTO_CLAMPED"

    # Camera-parented title cards stay perfectly framed through every camera move.
    font = bpy.data.curves.new("SHORTFORGE title typography", type="FONT")
    font.body = str(project.get("title", "SHORTFORGE")).upper()[:36]
    font.align_x = "CENTER"
    font.size = 0.34 if len(font.body) > 18 else 0.43
    font.extrude = 0.001
    text_obj = bpy.data.objects.new("SHORTFORGE title overlay", font)
    scene.collection.objects.link(text_obj)
    text_obj.parent = camera
    text_obj.location = (0.0, 2.35, -8.0)
    text_obj.rotation_euler = (0.0, 0.0, 0.0)
    title_mat = bpy.data.materials.new("Title warm ivory")
    title_mat.diffuse_color = (1.0, 0.91, 0.70, 1.0)
    title_mat.use_nodes = True
    bsdf = title_mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (1.0, 0.91, 0.70, 1.0)
        bsdf.inputs["Emission Color"].default_value = (1.0, 0.67, 0.28, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 0.7
    font.materials.append(title_mat)
    text_obj.hide_render = False
    text_obj.keyframe_insert(data_path="location", frame=1)
    text_obj.location.y += 0.18
    text_obj.keyframe_insert(data_path="location", frame=42)
    text_obj.location.y -= 0.18
    text_obj.keyframe_insert(data_path="location", frame=60)
    return camera


def create_story_prop(scene, character_root, total_frames, fps):
    # A small original emissive practical is the story's visual focal point.
    emission = bpy.data.materials.new("Last light | warm emissive core")
    emission.diffuse_color = (1.0, 0.55, 0.12, 1.0)
    emission.use_nodes = True
    nodes = emission.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeEmission")
    shader.inputs["Color"].default_value = (1.0, 0.39, 0.055, 1.0)
    shader.inputs["Strength"].default_value = 4.0
    emission.node_tree.links.new(shader.outputs["Emission"], output.inputs["Surface"])

    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, radius=0.14,
                                         location=character_root.location + Vector((0.62, -0.06, 1.35)))
    orb = bpy.context.object
    orb.name = "The last light | emissive story prop"
    orb.data.materials.append(emission)
    bpy.ops.object.shade_smooth()
    orb.parent = character_root
    orb.location = (0.58, -0.10, 1.45)
    for frame, position, scale in [
        (1, (0.58, -0.10, 1.45), 1.0),
        (fps * 10, (0.84, -0.08, 1.70), 1.12),
        (fps * 20, (0.40, -0.12, 1.52), 0.98),
        (fps * 30, (0.18, -0.12, 1.65), 1.05),
        (fps * 40, (-0.12, -0.12, 1.92), 1.18),
        (fps * 50, (0.10, -0.12, 2.22), 1.3),
        (total_frames, (0.10, 0.12, 2.75), 1.45),
    ]:
        orb.location = position
        orb.scale = (scale, scale, scale)
        orb.keyframe_insert(data_path="location", frame=frame)
        orb.keyframe_insert(data_path="scale", frame=frame)
    for curve in orb.animation_data.action.fcurves:
        for key in curve.keyframe_points:
            key.interpolation = "BEZIER"
            key.handle_left_type = "AUTO_CLAMPED"
            key.handle_right_type = "AUTO_CLAMPED"

    bpy.ops.object.light_add(type="POINT", location=(0, 0, 0))
    glow = bpy.context.object
    glow.name = "Last light | moving glow"
    glow.data.energy = 58
    glow.data.color = (1.0, 0.38, 0.08)
    glow.data.shadow_soft_size = 0.55
    glow.parent = character_root
    for frame, position in [
        (1, (0.58, -0.1, 1.45)),
        (fps * 20, (0.4, -0.1, 1.52)),
        (fps * 40, (-0.12, -0.1, 1.92)),
        (total_frames, (0.1, 0.12, 2.75)),
    ]:
        glow.location = position
        glow.keyframe_insert(data_path="location", frame=frame)
    return orb


def main():
    args = parse_args()
    project_path = Path(args.project).resolve()
    frames_dir = Path(args.frames_dir).resolve()
    frames_dir.mkdir(parents=True, exist_ok=True)
    project = json.loads(project_path.read_text(encoding="utf-8"))
    fps = int(project["fps"])
    total_frames = int(project["duration_seconds"]) * fps

    environment_file = project.get("environment_file", "")
    loaded_environment = bool(environment_file and bpy.data.filepath)
    if not loaded_environment:
        # Minimal empty-scene fallback for local authoring; production projects should
        # select an imported, licensed environment in config/<story>.json.
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)
        world = bpy.data.worlds.new("SHORTFORGE fallback world")
        world.use_nodes = True
        world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.12, 0.18, 0.26, 1)
        world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.65
        bpy.context.scene.world = world
        bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, -0.05))
        plane = bpy.context.object
        plane.name = "Fallback studio floor"
        floor = bpy.data.materials.new("Fallback floor")
        floor.diffuse_color = (0.16, 0.22, 0.24, 1)
        plane.data.materials.append(floor)

    scene = bpy.context.scene
    set_engine_and_quality(scene, project)
    scene.frame_start = 1
    scene.frame_end = total_frames

    character_cfg = project.get("character", {})
    model_path = character_cfg.get("model_file")
    if model_path:
        avatar = add_rigged_avatar(
            model_path,
            character_cfg.get("avatar_id", "hero_female"),
            location=character_cfg.get("position", [0.0, 0.0, 0.0]),
            rotation_z=float(character_cfg.get("rotation_z", 0.0)),
            scale=float(character_cfg.get("scale", 1.0)),
        )
        animate_avatar(avatar, project, fps, total_frames)
        avatar_root = avatar["root"]
    else:
        raise RuntimeError("No reusable rigged character model_file was supplied by the asset stage")

    # Add soft cinematic key/fill/rim lights without replacing the authored environment lighting.
    spawn = Vector(character_cfg.get("position", [0.0, 0.0, 0.0]))
    add_area_light("SHORTFORGE soft key", spawn + Vector((-4.5, -5.0, 7.0)), spawn + Vector((0, 0, 1.4)), 850, (1.0, 0.79, 0.61), 5.0)
    add_area_light("SHORTFORGE cool fill", spawn + Vector((4.0, -3.0, 4.0)), spawn + Vector((0, 0, 1.2)), 420, (0.50, 0.69, 1.0), 4.0)
    add_area_light("SHORTFORGE rim", spawn + Vector((0.0, 2.8, 5.5)), spawn + Vector((0, 0, 1.4)), 700, (1.0, 0.60, 0.30), 3.5)

    create_story_prop(scene, avatar_root, total_frames, fps)
    camera = create_camera(scene, project, avatar_root, total_frames)
    scene.camera = camera
    scene.frame_set(1)

    if args.save_blend:
        blend_path = Path(args.save_blend).resolve()
        blend_path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    for frame in range(1, total_frames + 1):
        scene.frame_set(frame)
        scene.render.filepath = str(frames_dir / f"frame_{frame:06d}.png")
        bpy.ops.render.render(write_still=True)
        if frame % max(1, fps * 5) == 0 or frame == total_frames:
            print(f"SHORTFORGE_PROGRESS {frame}/{total_frames}", flush=True)

    print(f"SHORTFORGE_RENDER_COMPLETE frames={total_frames} size={project['width']}x{project['height']} environment={environment_file}", flush=True)


if __name__ == "__main__":
    main()
