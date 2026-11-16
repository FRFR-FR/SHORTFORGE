"""Build and render an original procedural short with Blender's native renderer.

This script intentionally uses only bpy + Python's standard library. It does not
require NumPy, GLB export, Node, Chromium, Remotion or network access.
"""
from __future__ import annotations
import argparse
import json
import math
import os
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--frames-dir", required=True)
    parser.add_argument("--save-blend", default="")
    return parser.parse_args(argv)


def rgba(value, fallback):
    if isinstance(value, list) and len(value) == 4:
        return tuple(float(max(0.0, min(1.0, x))) for x in value)
    return fallback


def material(name, color, roughness=0.78, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat


def assign(obj, mat):
    if mat:
        obj.data.materials.append(mat)
    return obj


def bevel(obj, amount=0.12, segments=3):
    mod = obj.modifiers.new("Soft crafted edges", "BEVEL")
    mod.width = amount
    mod.segments = segments
    obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return obj


def cube(name, location, scale, mat, bevel_amount=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(obj, mat)
    if bevel_amount:
        bevel(obj, bevel_amount)
    return obj


def sphere(name, location, scale, mat, segments=20, rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    assign(obj, mat)
    bpy.ops.object.shade_smooth()
    return obj


def cone(name, location, radius, depth, mat):
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=radius, radius2=0.0, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    assign(obj, mat)
    bevel(obj, 0.04, 2)
    return obj


def parent_local(obj, parent, location):
    obj.parent = parent
    obj.location = location
    return obj


def set_linear(obj):
    if not obj.animation_data or not obj.animation_data.action:
        return
    for fcurve in obj.animation_data.action.fcurves:
        for key in fcurve.keyframe_points:
            key.interpolation = "BEZIER" if "rotation_euler" in fcurve.data_path else "LINEAR"


def create_tree(x, y, ground_mat, trunk_mat, leaf_mat, size=1.0):
    cube("Tree trunk", (x, y, 0.68 * size), (0.22 * size, 0.22 * size, 1.35 * size), trunk_mat, 0.04)
    sphere("Tree crown lower", (x, y, 1.5 * size), (0.72 * size, 0.65 * size, 0.72 * size), leaf_mat)
    sphere("Tree crown upper", (x + 0.12 * size, y, 1.95 * size), (0.48 * size, 0.45 * size, 0.52 * size), leaf_mat)


def build_environment(mats):
    ground = mats["ground"]
    road = mats["road"]
    sidewalk = mats["sidewalk"]
    building_mats = mats["buildings"]
    window = mats["window"]
    trunk = mats["trunk"]
    leaf = mats["leaf"]
    lane = mats["lane"]

    cube("Ground", (0, 2, -0.22), (28, 36, 0.4), ground)
    cube("Road", (0, -0.2, 0.005), (28, 7.2, 0.08), road)
    cube("Far sidewalk", (0, 3.65, 0.07), (28, 1.2, 0.16), sidewalk, 0.08)
    cube("Near sidewalk", (0, -4.05, 0.07), (28, 1.2, 0.16), sidewalk, 0.08)
    for x in range(-12, 13, 3):
        cube("Road dash", (x, -0.2, 0.06), (1.35, 0.13, 0.035), lane, 0.02)

    for index, x in enumerate([-10, -5.2, 0, 5.2, 10]):
        width = 3.8 if index % 2 else 4.2
        height = [5.4, 6.5, 5.8, 7.0, 5.2][index]
        depth = 2.1
        y = 6.5
        bmat = building_mats[index % len(building_mats)]
        cube(f"Town building {index + 1}", (x, y, height / 2), (width, depth, height), bmat, 0.12)
        # Repeating window grids are generated deterministically, not imported assets.
        cols = max(2, int(width / 0.9))
        rows = max(2, int(height / 1.05) - 1)
        for row in range(rows):
            for col in range(cols):
                wx = x - width / 2 + (col + 0.5) * width / cols
                wz = 0.85 + row * 1.05
                cube("Window", (wx, y - depth / 2 - 0.018, wz), (0.42, 0.045, 0.55), window, 0.025)

    for x in [-8.2, -3.0, 3.0, 8.2]:
        create_tree(x, 3.8, ground, trunk, leaf, 0.9 if abs(x) > 7 else 0.75)

    # A compact moving car adds a second layer of motion behind the protagonist.
    car_root = bpy.data.objects.new("Moving car root", None)
    bpy.context.collection.objects.link(car_root)
    car_body = cube("Car body", (0, 0, 0), (1.55, 0.78, 0.46), mats["car"], 0.13)
    parent_local(car_body, car_root, (0, 0, 0.45))
    cabin = cube("Car cabin", (0, 0, 0), (0.83, 0.68, 0.42), mats["glass"], 0.12)
    parent_local(cabin, car_root, (-0.08, 0, 0.82))
    for wheel_x in [-0.48, 0.48]:
        for wheel_y in [-0.34, 0.34]:
            wheel = sphere("Car wheel", (0, 0, 0), (0.19, 0.12, 0.19), mats["tire"], 16, 8)
            parent_local(wheel, car_root, (wheel_x, wheel_y, 0.2))
    car_root.location = (-10.5, 1.7, 0)
    car_root.keyframe_insert(data_path="location", frame=1)
    car_root.location = (10.5, 1.7, 0)
    car_root.keyframe_insert(data_path="location", frame=301)
    set_linear(car_root)


def create_character(config, mats, total_frames):
    character = config.get("character", {})
    primary = material("Character primary", rgba(character.get("primary_color"), (0.12, 0.48, 0.78, 1)))
    accent = material("Character accent", rgba(character.get("accent_color"), (1.0, 0.58, 0.12, 1)))
    skin = mats["skin"]
    dark = mats["dark"]
    white = mats["white"]

    root = bpy.data.objects.new("Character root", None)
    bpy.context.collection.objects.link(root)

    torso = cube("Character torso", (0, 0, 0), (0.74, 0.48, 0.86), primary, 0.16)
    parent_local(torso, root, (0, 0, 1.48))
    head = sphere("Character head", (0, 0, 0), (0.47, 0.43, 0.48), skin)
    parent_local(head, root, (0, -0.015, 2.32))
    hair = sphere("Hair cap", (0, 0, 0), (0.49, 0.44, 0.24), dark)
    parent_local(hair, root, (0, 0.005, 2.63))
    # Eyes are placed on the camera-facing side of the head.
    for eye_x in [-0.16, 0.16]:
        eye = sphere("Eye white", (0, 0, 0), (0.075, 0.045, 0.105), white, 16, 8)
        parent_local(eye, root, (eye_x, -0.405, 2.34))
        pupil = sphere("Eye pupil", (0, 0, 0), (0.035, 0.024, 0.055), dark, 16, 8)
        parent_local(pupil, root, (eye_x, -0.448, 2.33))
    mouth = sphere("Mouth", (0, 0, 0), (0.09, 0.025, 0.025), dark, 16, 8)
    parent_local(mouth, root, (0, -0.433, 2.12))

    # Joint empties make limbs animatable without a fragile external rig dependency.
    limbs = []
    for side, x in [("L", -0.43), ("R", 0.43)]:
        arm_pivot = bpy.data.objects.new(f"Arm {side} pivot", None)
        bpy.context.collection.objects.link(arm_pivot)
        parent_local(arm_pivot, root, (x, 0, 1.82))
        arm = sphere(f"Arm {side}", (0, 0, 0), (0.145, 0.16, 0.46), primary)
        parent_local(arm, arm_pivot, (0, 0, -0.38))
        hand = sphere(f"Hand {side}", (0, 0, 0), (0.15, 0.15, 0.15), skin)
        parent_local(hand, arm_pivot, (0, -0.015, -0.76))
        limbs.append((arm_pivot, 1 if side == "L" else -1))

    for side, x in [("L", -0.20), ("R", 0.20)]:
        leg_pivot = bpy.data.objects.new(f"Leg {side} pivot", None)
        bpy.context.collection.objects.link(leg_pivot)
        parent_local(leg_pivot, root, (x, 0, 1.08))
        leg = sphere(f"Leg {side}", (0, 0, 0), (0.18, 0.19, 0.46), accent)
        parent_local(leg, leg_pivot, (0, 0, -0.36))
        shoe = sphere(f"Shoe {side}", (0, 0, 0), (0.18, 0.28, 0.15), dark)
        parent_local(shoe, leg_pivot, (0, -0.12, -0.72))
        limbs.append((leg_pivot, -1 if side == "L" else 1))

    # One-second run cycle, repeated over the whole 30 fps timeline.
    cycle_frames = [0, 7, 15, 22, 30]
    cycle_angles = [0.72, 0.0, -0.72, 0.0, 0.72]
    for pivot, direction in limbs:
        for frame, angle in zip(cycle_frames, cycle_angles):
            pivot.rotation_euler[0] = angle * direction
            pivot.keyframe_insert(data_path="rotation_euler", index=0, frame=frame)
        if pivot.animation_data and pivot.animation_data.action:
            for curve in pivot.animation_data.action.fcurves:
                modifier = curve.modifiers.new(type="CYCLES")
                modifier.mode_before = "REPEAT"
                modifier.mode_after = "REPEAT"

    for frame, z in [(1, 0.0), (8, 0.10), (16, 0.0), (23, 0.10), (30, 0.0)]:
        root.location.z = z
        root.keyframe_insert(data_path="location", index=2, frame=frame)
    root.location.x = -0.45
    root.keyframe_insert(data_path="location", index=0, frame=1)
    root.location.x = 0.45
    root.keyframe_insert(data_path="location", index=0, frame=total_frames)
    set_linear(root)
    if root.animation_data and root.animation_data.action:
        for curve in root.animation_data.action.fcurves:
            if curve.data_path == "location" and curve.array_index == 2:
                modifier = curve.modifiers.new(type="CYCLES")
                modifier.mode_before = "REPEAT"
                modifier.mode_after = "REPEAT"
    return root


def setup_camera(scene, total_frames, config):
    bpy.ops.object.camera_add(location=(0, -13.2, 4.2))
    camera = bpy.context.object
    camera.name = "Vertical cinematic camera"
    target = Vector((0, 1.1, 2.0))
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = 47
    camera.data.sensor_width = 36
    scene.camera = camera
    profiles = {
        "wide": ((0.0, -15.5, 5.0), 41.0),
        "push_in": ((0.1, -11.5, 4.35), 51.0),
        "close": ((0.0, -9.7, 3.45), 61.0),
        "side": ((3.2, -12.0, 4.25), 49.0),
        "low": ((0.0, -13.0, 3.05), 48.0),
    }
    shots = config.get("shots") or [{"start_seconds": 0, "duration_seconds": total_frames / scene.render.fps, "camera": "wide"}]
    for shot in shots:
        start_frame = max(1, int(float(shot.get("start_seconds", 0)) * scene.render.fps) + 1)
        end_frame = min(total_frames, start_frame + int(float(shot.get("duration_seconds", 1)) * scene.render.fps) - 1)
        location, lens = profiles.get(shot.get("camera", "wide"), profiles["wide"])
        camera.location = location
        target = Vector((0, 1.1, 2.0))
        camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
        camera.data.lens = lens
        camera.keyframe_insert(data_path="location", frame=start_frame)
        camera.keyframe_insert(data_path="rotation_euler", frame=start_frame)
        camera.data.keyframe_insert(data_path="lens", frame=start_frame)
        # A restrained drift within each shot prevents static slideshow framing.
        camera.location.x += 0.12 if shot.get("camera") != "side" else -0.12
        camera.keyframe_insert(data_path="location", frame=end_frame)
        camera.keyframe_insert(data_path="rotation_euler", frame=end_frame)
        camera.data.keyframe_insert(data_path="lens", frame=end_frame)
    set_linear(camera)
    if camera.animation_data and camera.animation_data.action:
        for curve in camera.animation_data.action.fcurves:
            for key in curve.keyframe_points:
                key.interpolation = "BEZIER"

    # Custom title card, kept in the 3D scene for a fully local render.
    title = bpy.data.curves.new("Short title", type="FONT")
    title.body = str(config.get("title", "SHORTFORGE")).upper()[:28]
    title.align_x = "CENTER"
    title.size = 0.28 if len(title.body) > 18 else 0.36
    title.extrude = 0.004
    text_obj = bpy.data.objects.new("Short title", title)
    bpy.context.collection.objects.link(text_obj)
    text_obj.location = (0, -0.55, 4.55)
    text_obj.rotation_euler = (math.radians(90), 0, 0)
    title_mat = material("Title cream", (1.0, 0.94, 0.78, 1.0))
    assign(text_obj, title_mat)


def create_lighting(scene):
    world = bpy.data.worlds.new("Soft blue studio") if not bpy.data.worlds else bpy.data.worlds[0]
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.25, 0.39, 0.56, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.55

    bpy.ops.object.light_add(type="AREA", location=(-5, -7, 10))
    key = bpy.context.object
    key.name = "Large soft key"
    key.data.energy = 1700
    key.data.shape = "DISK"
    key.data.size = 8
    key.rotation_euler = (math.radians(24), 0, math.radians(-26))

    bpy.ops.object.light_add(type="AREA", location=(5, 1, 7))
    rim = bpy.context.object
    rim.name = "Warm rim light"
    rim.data.energy = 900
    rim.data.size = 6
    rim.data.color = (1.0, 0.72, 0.45)
    rim.rotation_euler = (math.radians(18), 0, math.radians(145))


def make_materials():
    return {
        "ground": material("Warm stone ground", (0.54, 0.52, 0.46, 1)),
        "road": material("Deep asphalt", (0.10, 0.15, 0.21, 1)),
        "sidewalk": material("Pale sidewalk", (0.72, 0.69, 0.61, 1)),
        "buildings": [
            material("Building coral", (0.74, 0.36, 0.28, 1)),
            material("Building teal", (0.24, 0.50, 0.54, 1)),
            material("Building sand", (0.78, 0.62, 0.40, 1)),
            material("Building lavender", (0.48, 0.43, 0.61, 1)),
        ],
        "window": material("Window blue glass", (0.22, 0.45, 0.58, 1), 0.25, 0.1),
        "trunk": material("Tree bark", (0.28, 0.18, 0.12, 1)),
        "leaf": material("Tree green", (0.20, 0.43, 0.25, 1)),
        "lane": material("Lane paint", (0.95, 0.83, 0.55, 1)),
        "car": material("Car amber", (0.92, 0.31, 0.12, 1), 0.32),
        "glass": material("Car glass", (0.15, 0.34, 0.43, 1), 0.22),
        "tire": material("Tire", (0.035, 0.045, 0.055, 1)),
        "skin": material("Character warm skin", (0.83, 0.58, 0.39, 1)),
        "dark": material("Character dark details", (0.10, 0.12, 0.16, 1)),
        "white": material("Eye white", (0.96, 0.96, 0.91, 1)),
    }


def main():
    args = parse_args()
    project_path = Path(args.project).resolve()
    frames_dir = Path(args.frames_dir).resolve()
    frames_dir.mkdir(parents=True, exist_ok=True)
    config = json.loads(project_path.read_text(encoding="utf-8"))
    fps = int(config["fps"])
    total_frames = int(config["duration_seconds"]) * fps

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)

    scene = bpy.context.scene
    engine_options = {item.identifier for item in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}
    if "BLENDER_EEVEE_NEXT" in engine_options:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    elif "BLENDER_EEVEE" in engine_options:
        scene.render.engine = "BLENDER_EEVEE"
    else:
        scene.render.engine = "BLENDER_WORKBENCH"
        scene.display.shading.light = "STUDIO"
        scene.display.shading.show_shadows = True
        scene.display.shading.show_cavity = True

    scene.render.resolution_x = int(config["width"])
    scene.render.resolution_y = int(config["height"])
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.filepath = str(frames_dir / "frame_")
    scene.frame_start = 1
    scene.frame_end = total_frames
    scene.render.use_file_extension = True
    scene.render.image_settings.color_depth = "8"
    scene.render.resolution_percentage = 100
    scene.render.threads_mode = "FIXED"
    scene.render.threads = max(1, min(4, os.cpu_count() or 2))
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast" if "Medium High Contrast" in [x.name for x in scene.view_settings.bl_rna.properties["look"].enum_items] else "None"
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    if hasattr(scene, "eevee") and hasattr(scene.eevee, "taa_render_samples"):
        scene.eevee.taa_render_samples = int(config.get("render", {}).get("samples", 32))
    if hasattr(scene, "eevee_next") and hasattr(scene.eevee_next, "taa_render_samples"):
        scene.eevee_next.taa_render_samples = int(config.get("render", {}).get("samples", 32))

    mats = make_materials()
    build_environment(mats)
    create_character(config, mats, total_frames)
    setup_camera(scene, total_frames, config)
    create_lighting(scene)
    scene.frame_set(1)

    if args.save_blend:
        blend_path = Path(args.save_blend).resolve()
        blend_path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    for frame in range(1, total_frames + 1):
        scene.frame_set(frame)
        scene.render.filepath = str(frames_dir / f"frame_{frame:06d}.png")
        bpy.ops.render.render(write_still=True)
        if frame % max(1, fps) == 0 or frame == total_frames:
            print(f"SHORTFORGE_PROGRESS {frame}/{total_frames}", flush=True)

    print(f"SHORTFORGE_RENDER_COMPLETE frames={total_frames} size={config['width']}x{config['height']}", flush=True)


if __name__ == "__main__":
    main()
