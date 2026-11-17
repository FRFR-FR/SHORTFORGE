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
from avatar_system import load_avatar_blend, animate_avatar


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
    # Start from the imported set's authored camera. Its composition establishes
    # the scale and direction of the location; the short's camera then tracks the hero.
    source_camera = scene.camera
    if source_camera:
        source_location = source_camera.matrix_world.translation.copy()
        base_offset = source_location - target
        if base_offset.length < 1.0 or base_offset.length > 80.0:
            base_offset = Vector((0.0, -8.0, 3.0))
        base_lens = float(source_camera.data.lens)
    else:
        base_offset = Vector((0.0, -8.0, 3.0))
        base_lens = 52.0
    bpy.ops.object.camera_add(location=target + base_offset)
    camera = bpy.context.object
    camera.name = "SHORTFORGE vertical cinema camera"
    camera.data.lens = base_lens
    camera.data.sensor_fit = "VERTICAL"
    camera.data.sensor_height = 24
    camera.data.clip_start = 0.05
    camera.data.clip_end = 1000.0
    scene.camera = camera

    direction = base_offset.normalized()
    base_distance = max(3.5, min(24.0, base_offset.length))
    profiles = {
        "wide": (direction * base_distance * 1.08, base_lens * 0.90, 0.0, 0.0),
        "push_in": (direction * base_distance * 0.90, base_lens * 1.02, 0.0, 0.0),
        "close": (direction * base_distance * 0.70, base_lens * 1.14, 0.0, 0.0),
        "side": (direction * base_distance * 0.86, base_lens, 0.18, 0.0),
        "low": (direction * base_distance * 0.96 + Vector((0.0, 0.0, -0.65)), base_lens * 0.96, 0.0, -0.15),
    }
    shots = project.get("shots") or [{
        "start_seconds": 0,
        "duration_seconds": total_frames / scene.render.fps,
        "camera": "wide",
    }]
    for shot in shots:
        start = max(1, int(float(shot.get("start_seconds", 0)) * scene.render.fps) + 1)
        end = min(total_frames, start + int(float(shot.get("duration_seconds", 1)) * scene.render.fps) - 1)
        offset, lens, side_offset, height_offset = profiles.get(shot.get("camera", "wide"), profiles["wide"])
        shot_target = target + Vector(shot.get("camera_target_offset", [0.0, 0.0, 0.0]))
        camera.location = shot_target + offset + Vector((side_offset * base_distance, 0.0, height_offset))
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
    text_obj.keyframe_insert(data_path="hide_render", frame=1)
    text_obj.hide_viewport = False
    text_obj.keyframe_insert(data_path="hide_viewport", frame=1)
    text_obj.keyframe_insert(data_path="location", frame=1)
    text_obj.location.y += 0.18
    text_obj.keyframe_insert(data_path="location", frame=42)
    text_obj.location.y -= 0.18
    text_obj.keyframe_insert(data_path="location", frame=60)
    # Title only occupies the opening beat; subsequent frames are clean for captions.
    text_obj.hide_render = True
    text_obj.keyframe_insert(data_path="hide_render", frame=121)
    text_obj.hide_viewport = True
    text_obj.keyframe_insert(data_path="hide_viewport", frame=121)
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



def clear_scene_for_procedural_theme(scene):
    """Remove imported splash-scene geometry so the custom story set is coherent."""
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    if scene.world is None:
        scene.world = bpy.data.worlds.new("SHORTFORGE Georgian dusk")
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    if background:
        background.inputs["Color"].default_value = (0.025, 0.045, 0.065, 1.0)
        background.inputs["Strength"].default_value = 0.28


def story_material(name, color, roughness=0.78, metallic=0.0, emission=0.0):
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*color, 1.0)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    if shader:
        shader.inputs["Base Color"].default_value = (*color, 1.0)
        shader.inputs["Roughness"].default_value = roughness
        shader.inputs["Metallic"].default_value = metallic
        if emission > 0:
            shader.inputs["Emission Color"].default_value = (*color, 1.0)
            shader.inputs["Emission Strength"].default_value = emission
    return material


def story_cube(name, location, dimensions, material, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        obj.data.materials.append(material)
    if bevel > 0:
        modifier = obj.modifiers.new("Soft crafted edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
        obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return obj


def story_cylinder(name, location, radius, depth, material, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=depth, location=location
    )
    obj = bpy.context.object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    bevel = obj.modifiers.new("Coin edge bevel", "BEVEL")
    bevel.width = min(depth * 0.18, 0.012)
    bevel.segments = 2
    obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return obj


def make_window_unit(x, z, front_y, wood, glass, stone, label, sealed=False):
    """Create a readable Georgian sash window on the front of a building."""
    width, height = 0.96, 1.45
    story_cube(f"{label} | dark recess", (x, front_y, z), (width, 0.10, height), stone, 0.01)
    story_cube(f"{label} | glass", (x, front_y - 0.075, z), (width - 0.18, 0.035, height - 0.20), glass, 0.01)
    frame_y = front_y - 0.12
    for dx in (-width / 2, width / 2):
        story_cube(f"{label} | vertical sash", (x + dx, frame_y, z), (0.10, 0.13, height + 0.12), wood, 0.012)
    for dz in (-height / 2, height / 2):
        story_cube(f"{label} | horizontal sash", (x, frame_y, z + dz), (width + 0.10, 0.13, 0.10), wood, 0.012)
    story_cube(f"{label} | centre mullion", (x, frame_y - 0.01, z), (0.055, 0.15, height - 0.10), wood, 0.008)
    story_cube(f"{label} | cross rail", (x, frame_y - 0.02, z), (width - 0.10, 0.15, 0.055), wood, 0.008)
    story_cube(f"{label} | stone sill", (x, front_y - 0.20, z - height / 2 - 0.08), (width + 0.26, 0.32, 0.16), stone, 0.035)
    story_cube(f"{label} | lintel", (x, front_y - 0.16, z + height / 2 + 0.09), (width + 0.18, 0.20, 0.17), stone, 0.025)
    if sealed:
        story_cube(f"{label} | permanent blind inset", (x, front_y - 0.22, z), (width - 0.10, 0.09, height - 0.10), stone, 0.015)


def build_window_tax_set(scene, avatar_root, total_frames, fps):
    """Create an original period-inspired street, animated brick-up and tax ledger."""
    stone = story_material("Warm Georgian limestone", (0.49, 0.39, 0.29))
    pale_stone = story_material("Weathered pale sandstone", (0.68, 0.57, 0.42))
    brick = story_material("Hand-fired red brick", (0.34, 0.105, 0.065))
    brick_alt = story_material("Brick variation", (0.46, 0.17, 0.095))
    timber = story_material("Dark painted sash timber", (0.105, 0.075, 0.055))
    glass = story_material("Muted blue glass", (0.10, 0.22, 0.29), roughness=0.20, metallic=0.12)
    roof = story_material("Slate roof", (0.12, 0.17, 0.21))
    road = story_material("Wet cobbled street", (0.10, 0.13, 0.15), roughness=0.48)
    brass = story_material("Aged brass coins", (0.57, 0.34, 0.09), roughness=0.30, metallic=0.78)
    parchment = story_material("Ledger parchment", (0.72, 0.61, 0.43))
    leather = story_material("Ledger leather", (0.16, 0.09, 0.06))
    ink = story_material("Ledger ink", (0.07, 0.055, 0.04))
    floor = story_material("Street stone", (0.24, 0.25, 0.24), roughness=0.92)

    story_cube("Street paving", (0.0, 1.0, -0.18), (42.0, 38.0, 0.32), floor, 0.08)
    story_cube("Cobbled roadway", (0.0, -5.0, -0.015), (40.0, 10.0, 0.10), road, 0.02)

    # Three original facades establish a narrow late-Georgian street.
    buildings = [
        (-10.2, 7.0, 7.6, 6.0, pale_stone, brick),
        (0.0, 13.0, 9.4, 6.0, stone, brick),
        (10.0, 7.0, 7.2, 6.0, pale_stone, brick_alt),
    ]
    for building_index, (x, width, height, front_y, wall_mat, roof_mat) in enumerate(buildings):
        story_cube(f"Georgian house {building_index + 1}", (x, front_y + 0.85, height / 2),
                   (width, 1.7, height), wall_mat, 0.07)
        story_cube(f"Georgian plinth {building_index + 1}",
                   (x, front_y - 0.02, 0.55), (width + 0.18, 0.28, 0.65), roof_mat, 0.035)
        story_cube(f"Georgian cornice {building_index + 1}",
                   (x, front_y - 0.05, height - 0.10), (width + 0.30, 0.30, 0.22), pale_stone, 0.025)
        story_cube(f"Georgian roof fascia {building_index + 1}",
                   (x, front_y + 0.85, height + 0.20), (width + 0.50, 2.05, 0.45), roof, 0.04)
        columns = 4 if building_index == 1 else 2
        for row, z in enumerate((2.25, 4.55, 6.85)):
            for col in range(columns):
                if building_index == 1:
                    wx = x - 4.7 + col * 3.1
                else:
                    wx = x - 1.8 + col * 3.6
                # One blank opening is intentionally symmetrical, to make the
                # historical distinction between blind design and tax response visible.
                is_blind_by_design = building_index == 1 and row == 1 and col == 3
                is_animated_tax_window = building_index == 1 and row == 1 and col == 1
                make_window_unit(
                    wx, z, front_y - 0.06, timber, glass, pale_stone,
                    f"Facade {building_index + 1} window {row}-{col}",
                    sealed=is_blind_by_design,
                )
                if is_animated_tax_window:
                    target_x, target_z = wx, z

    # Animated bricks fill one opening. This represents a documented response,
    # not a claim that every blind window was created for tax avoidance.
    for row in range(3):
        for col in range(2):
            width = 0.40
            height = 0.38
            final_x = target_x - 0.21 + col * 0.42
            final_z = target_z - 0.47 + row * 0.44
            start_x = final_x + 2.2
            block = story_cube(
                f"Tax response | animated brick {row * 2 + col + 1}",
                (start_x, 5.54, final_z - 1.6),
                (width, 0.16, height),
                brick if (row + col) % 2 == 0 else brick_alt,
                0.018,
            )
            block.keyframe_insert(data_path="location", frame=1)
            block.location = (start_x, 5.54, final_z - 1.6)
            block.keyframe_insert(data_path="location", frame=18 * fps)
            block.location = (final_x, 5.39, final_z)
            block.keyframe_insert(data_path="location", frame=26 * fps)
            if block.animation_data and block.animation_data.action:
                for curve in block.animation_data.action.fcurves:
                    for key in curve.keyframe_points:
                        key.interpolation = "BEZIER"
                        key.handle_left_type = "AUTO_CLAMPED"
                        key.handle_right_type = "AUTO_CLAMPED"

    # The assessor's table, ledger and coins are a separate foreground insert.
    story_cube("Assessor's oak table", (2.7, -1.0, 0.78), (4.0, 2.1, 0.22), timber, 0.08)
    for x in (1.0, 4.4):
        for y in (-1.8, -0.2):
            story_cube("Table leg", (x, y, 0.34), (0.16, 0.16, 0.75), timber, 0.025)
    story_cube("Bound tax ledger", (2.45, -0.95, 0.94), (1.45, 1.15, 0.12), leather, 0.025)
    story_cube("Ledger page", (2.45, -0.92, 1.015), (1.27, 1.02, 0.025), parchment, 0.01)
    story_cube("Ledger centre fold", (2.45, -0.92, 1.035), (0.025, 1.02, 0.02), leather, 0.005)
    for row in range(5):
        story_cube("Ledger ruled line", (2.45, -1.30 + row * 0.18, 1.052),
                   (0.86, 0.012, 0.008), ink, 0.002)
    for index in range(9):
        coin = story_cylinder(
            f"Assessment coins {index + 1}",
            (3.75 + (index % 3) * 0.24, -1.20 + (index // 3) * 0.25, 0.91 + (index // 3) * 0.035),
            0.105, 0.035, brass,
        )
        coin.rotation_euler[0] = math.radians(90)
        coin.keyframe_insert(data_path="rotation_euler", frame=1)
        coin.rotation_euler[1] = math.radians(25 + index * 5)
        coin.keyframe_insert(data_path="rotation_euler", frame=45 * fps)

    # Warm street lamps and period door surrounds add scale and depth.
    for x in (-8.8, 8.6):
        story_cube("Street lamp post", (x, -1.2, 2.25), (0.10, 0.10, 4.4), timber, 0.018)
        story_cube("Street lamp arm", (x + 0.34, -1.2, 4.23), (0.72, 0.10, 0.10), timber, 0.018)
        lamp = story_material("Gas lamp warm glass", (1.0, 0.47, 0.14), roughness=0.25, emission=1.2)
        story_cube("Street lamp lantern", (x + 0.67, -1.2, 4.0), (0.37, 0.37, 0.55), lamp, 0.04)

    # The householder is visible in the opening only; object details carry the
    # explanation afterwards so that the narration is never hidden by staging.
    for obj in [avatar_root] + list(avatar_root.children_recursive):
        obj.hide_render = False
        obj.keyframe_insert(data_path="hide_render", frame=1)
        obj.hide_render = True
        obj.keyframe_insert(data_path="hide_render", frame=16 * fps)

    add_area_light("Window tax | warm key", (-7.0, -10.0, 13.5), (0.0, 4.0, 4.0),
                   1700, (1.0, 0.72, 0.48), 9.0)
    add_area_light("Window tax | cool sky fill", (8.0, -6.0, 10.0), (0.0, 4.0, 4.0),
                   900, (0.48, 0.65, 0.88), 8.0)
    add_area_light("Window tax | street rim", (0.0, 12.0, 11.0), (0.0, 4.0, 3.5),
                   1300, (1.0, 0.52, 0.28), 7.0)


def create_window_tax_camera(scene, project, total_frames, fps):
    """A fresh, story-specific vertical camera path with motivated gliding moves."""
    camera_path = [
        (0, (0.0, -18.0, 7.0), (0.0, 5.0, 4.3), 38.0),
        (5, (-4.0, -11.0, 5.2), (-4.0, 5.0, 4.2), 52.0),
        (10, (-2.6, -8.0, 2.6), (-2.6, -0.8, 1.55), 54.0),
        (15, (0.0, -10.0, 5.8), (0.0, 5.0, 5.0), 51.0),
        (20, (-1.6, -7.0, 5.0), (-1.6, 5.0, 4.55), 69.0),
        (25, (-1.6, -5.7, 4.7), (-1.6, 5.0, 4.55), 82.0),
        (30, (0.0, -13.0, 6.6), (0.0, 5.0, 4.4), 43.0),
        (35, (2.7, -5.8, 8.4), (2.7, -1.0, 0.9), 57.0),
        (40, (0.0, -15.0, 7.1), (0.0, 5.0, 5.0), 41.0),
        (45, (3.8, -8.0, 4.6), (3.8, 5.0, 4.1), 57.0),
        (50, (0.0, -17.0, 6.3), (0.0, 5.0, 4.4), 39.0),
        (55, (0.0, -19.0, 8.2), (0.0, 5.0, 4.4), 36.0),
    ]
    bpy.ops.object.camera_add(location=camera_path[0][1])
    camera = bpy.context.object
    camera.name = "SHORTFORGE | window tax vertical camera"
    camera.data.lens = camera_path[0][3]
    camera.data.sensor_fit = "VERTICAL"
    camera.data.sensor_height = 24
    camera.data.clip_start = 0.05
    camera.data.clip_end = 500.0
    scene.camera = camera

    for seconds, position, target, lens in camera_path:
        frame = min(total_frames, int(seconds * fps) + 1)
        camera.location = position
        camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
        camera.data.lens = lens
        camera.keyframe_insert(data_path="location", frame=frame)
        camera.keyframe_insert(data_path="rotation_euler", frame=frame)
        camera.data.keyframe_insert(data_path="lens", frame=frame)
    if camera.animation_data and camera.animation_data.action:
        for curve in camera.animation_data.action.fcurves:
            for key in curve.keyframe_points:
                key.interpolation = "BEZIER"
                key.handle_left_type = "AUTO_CLAMPED"
                key.handle_right_type = "AUTO_CLAMPED"

    title = bpy.data.curves.new("Window tax title typography", type="FONT")
    title.body = "TAXED SUNLIGHT"
    title.align_x = "CENTER"
    title.size = 0.40
    title.extrude = 0.001
    title_obj = bpy.data.objects.new("Opening title | THE WINDOW TAX", title)
    scene.collection.objects.link(title_obj)
    title_obj.parent = camera
    title_obj.location = (0.0, 1.55, -8.0)
    title_obj.rotation_euler = (0.0, 0.0, 0.0)
    title_mat = story_material("Opening title | warm ivory", (1.0, 0.83, 0.57), roughness=0.48, emission=0.8)
    title.materials.append(title_mat)
    title_obj.keyframe_insert(data_path="location", frame=1)
    title_obj.location.y = 1.78
    title_obj.keyframe_insert(data_path="location", frame=70)
    title_obj.hide_render = False
    title_obj.keyframe_insert(data_path="hide_render", frame=1)
    title_obj.hide_render = True
    title_obj.keyframe_insert(data_path="hide_render", frame=4 * fps)
    return camera

def main():
    args = parse_args()
    project_path = Path(args.project).resolve()
    frames_dir = Path(args.frames_dir).resolve()
    frames_dir.mkdir(parents=True, exist_ok=True)
    project = json.loads(project_path.read_text(encoding="utf-8"))
    fps = int(project["fps"])
    total_frames = int(project["duration_seconds"]) * fps

    environment_file = project.get("environment_file", "")
    if not environment_file:
        raise RuntimeError("Production rendering requires a downloaded, licensed prebuilt Blender environment")
    if not bpy.data.filepath or Path(bpy.data.filepath).resolve() != Path(environment_file).resolve():
        raise RuntimeError(
            f"Blender did not open the selected prebuilt environment: expected {environment_file}, "
            f"loaded {bpy.data.filepath or '(empty scene)'}"
        )

    scene = bpy.context.scene
    visual_theme = project.get("visual_theme", "")
    if visual_theme == "window-tax":
        clear_scene_for_procedural_theme(scene)
    set_engine_and_quality(scene, project)
    scene.frame_start = 1
    scene.frame_end = total_frames

    character_cfg = project.get("character", {})
    avatar_blend = character_cfg.get("avatar_blend_file")
    if avatar_blend:
        avatar = load_avatar_blend(
            avatar_blend,
            character_cfg.get("avatar_id", "hero_female"),
            location=character_cfg.get("position", [0.0, 0.0, 0.0]),
            rotation_z=float(character_cfg.get("rotation_z", 0.0)),
            scale=float(character_cfg.get("scale", 1.0)),
        )
        animate_avatar(avatar, project, fps, total_frames)
        avatar_root = avatar["root"]
    else:
        raise RuntimeError("No reusable avatar .blend file was supplied by the avatar-library stage")

    if visual_theme == "window-tax":
        build_window_tax_set(scene, avatar_root, total_frames, fps)
        camera = create_window_tax_camera(scene, project, total_frames, fps)
    else:
        # Existing SHORTFORGE cinematic defaults for other projects.
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
