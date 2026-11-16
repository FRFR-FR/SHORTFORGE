"""Reusable rigged humanoid avatars, facial-emotion controls and pose presets.

The underlying Quaternius meshes are CC0 humanoid models with a 65-bone rig.
This module adds a SHORTFORGE facial expression layer and a reusable pose bank.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

EMOTIONS = ("neutral", "happy", "sad", "angry", "surprised", "scared", "determined")

# Angles are degrees in local bone XYZ order. Names match Quaternius Universal Base.
POSES = {
    "neutral": {},
    "wave": {"upperarm_l": (0, 0, -72), "lowerarm_l": (0, 0, -92), "hand_l": (0, 0, -18)},
    "point": {"upperarm_r": (0, 0, 54), "lowerarm_r": (0, 0, -18), "hand_r": (0, 0, -8)},
    "confident": {"upperarm_l": (0, 0, -18), "upperarm_r": (0, 0, 18), "spine_02": (0, 0, -4)},
    "thinking": {"upperarm_l": (0, 0, -42), "lowerarm_l": (0, 0, -68), "hand_l": (0, 0, -22), "Head": (0, 0, 8)},
    "celebrating": {"upperarm_l": (0, 0, -112), "upperarm_r": (0, 0, 112), "lowerarm_l": (0, 0, -22), "lowerarm_r": (0, 0, 22)},
    "running": {"upperarm_l": (38, 0, -18), "upperarm_r": (-38, 0, 18), "thigh_l": (-32, 0, 0), "thigh_r": (32, 0, 0), "calf_l": (42, 0, 0), "calf_r": (12, 0, 0)},
    "crouching": {"pelvis": (0, 0, 0), "thigh_l": (62, 0, 0), "thigh_r": (62, 0, 0), "calf_l": (-108, 0, 0), "calf_r": (-108, 0, 0), "spine_02": (-18, 0, 0)},
}

# Local XY mouth curves: positive Y is an upturned mouth corner (smile).
MOUTHS = {
    "neutral": [(-0.045, 0.000), (-0.022, -0.001), (0.000, -0.002), (0.022, -0.001), (0.045, 0.000)],
    "happy": [(-0.048, -0.004), (-0.025, -0.018), (0.000, -0.022), (0.025, -0.018), (0.048, -0.004)],
    "sad": [(-0.048, 0.000), (-0.025, 0.012), (0.000, 0.018), (0.025, 0.012), (0.048, 0.000)],
    "angry": [(-0.045, 0.008), (-0.022, 0.000), (0.000, -0.006), (0.022, 0.000), (0.045, 0.008)],
    "surprised": [(0.000, 0.018), (0.018, 0.000), (0.014, -0.022), (0.000, -0.030), (-0.014, -0.022), (-0.018, 0.000), (0.000, 0.018)],
    "scared": [(-0.020, 0.020), (0.015, 0.025), (0.024, -0.010), (0.000, -0.035), (-0.026, -0.012), (-0.020, 0.020)],
    "determined": [(-0.046, 0.002), (-0.022, 0.000), (0.000, 0.000), (0.022, 0.000), (0.046, 0.002)],
}

PALETTES = {
    "hero_male": {"suit": (0.055, 0.22, 0.38, 1.0), "label": "Hero Male"},
    "hero_female": {"suit": (0.34, 0.075, 0.24, 1.0), "label": "Hero Female"},
}


def _material(name: str, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = 0.42
        bsdf.inputs["Metallic"].default_value = 0.06
    return mat


def _import_gltf(model_path: Path, label: str):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(model_path))
    imported = [obj for obj in bpy.data.objects if obj not in before]
    armatures = [obj for obj in imported if obj.type == "ARMATURE"]
    if not armatures:
        raise RuntimeError(f"No armature was imported from {model_path}")
    armature = armatures[0]
    armature.name = f"{label}_Rig"
    root = bpy.data.objects.new(f"{label}_Root", None)
    bpy.context.scene.collection.objects.link(root)
    imported_set = set(imported)
    top_level = [obj for obj in imported if obj.parent not in imported_set]
    for obj in top_level:
        world = obj.matrix_world.copy()
        obj.parent = root
        obj.matrix_world = world
    root["shortforge_avatar"] = label
    root["asset_source"] = "Quaternius Universal Base Characters — Standard"
    root["asset_license"] = "CC0-1.0"
    return root, armature, imported


def _make_brow_keys(brow_obj):
    if not brow_obj or brow_obj.type != "MESH":
        return {}
    if not brow_obj.data.shape_keys:
        brow_obj.shape_key_add(name="Basis")
    keys = {}
    coords = [v.co.copy() for v in brow_obj.data.vertices]
    if not coords:
        return keys
    min_x = min(v.x for v in coords)
    max_x = max(v.x for v in coords)
    center_x = (min_x + max_x) * 0.5
    half_width = max(0.001, (max_x - min_x) * 0.5)
    for emotion in EMOTIONS:
        key = brow_obj.shape_key_add(name=f"emotion_{emotion}")
        for index, base in enumerate(coords):
            nx = max(-1.0, min(1.0, (base.x - center_x) / half_width))
            arch = 1.0 - abs(nx)
            delta = 0.0
            if emotion == "happy":
                delta = 0.006 * arch
            elif emotion == "sad":
                delta = 0.014 * arch - 0.003 * abs(nx)
            elif emotion == "angry":
                delta = -0.016 * arch + 0.004 * abs(nx)
            elif emotion == "surprised":
                delta = 0.020
            elif emotion == "scared":
                delta = 0.023 * arch + 0.004
            elif emotion == "determined":
                delta = -0.008 * arch
            key.data[index].co = (base.x, base.y + delta, base.z)
        keys[emotion] = key
    return keys


def _make_eye_keys(eyes_obj):
    if not eyes_obj or eyes_obj.type != "MESH":
        return {}
    if not eyes_obj.data.shape_keys:
        eyes_obj.shape_key_add(name="Basis")
    coords = [v.co.copy() for v in eyes_obj.data.vertices]
    if not coords:
        return {}
    center_y = sum(v.y for v in coords) / len(coords)
    keys = {}
    for emotion in EMOTIONS:
        key = eyes_obj.shape_key_add(name=f"emotion_{emotion}")
        scale_y = 1.0
        if emotion == "happy":
            scale_y = 0.88
        elif emotion == "angry":
            scale_y = 0.90
        elif emotion in ("surprised", "scared"):
            scale_y = 1.16
        elif emotion == "sad":
            scale_y = 0.94
        for index, base in enumerate(coords):
            key.data[index].co = (base.x, center_y + (base.y - center_y) * scale_y, base.z)
        keys[emotion] = key
    return keys


def _curve_object(name: str, local_points, world_matrix, material):
    curve = bpy.data.curves.new(name, type="CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 12
    curve.bevel_depth = 0.006
    curve.bevel_resolution = 3
    spline = curve.splines.new("POLY")
    spline.points.add(len(local_points) - 1)
    for point, (x, y) in zip(spline.points, local_points):
        point.co = (x, y, 0.0, 1.0)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(material)
    obj.matrix_world = world_matrix
    return obj


def _attach_to_head(obj, armature):
    pose_bone = armature.pose.bones.get("Head")
    if pose_bone is None:
        return
    desired_world = obj.matrix_world.copy()
    bone_world = armature.matrix_world @ pose_bone.matrix
    obj.parent = armature
    obj.parent_type = "BONE"
    obj.parent_bone = "Head"
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.matrix_basis = bone_world.inverted() @ desired_world


def _add_face_expressions(armature, imported):
    eyes = next((o for o in imported if o.type == "MESH" and ("eyes" in o.name.lower() or "face.001" in o.name.lower())), None)
    brows = next((o for o in imported if o.type == "MESH" and ("eyebrow" in o.name.lower() or o.name.lower() == "face")), None)
    brow_keys = _make_brow_keys(brows)
    eye_keys = _make_eye_keys(eyes)
    if eyes:
        depsgraph = bpy.context.evaluated_depsgraph_get()
        bpy.context.view_layer.update()
        corners = [eyes.matrix_world @ Vector(corner) for corner in eyes.bound_box]
        center = sum(corners, Vector()) / len(corners)
        basis = eyes.matrix_world.to_3x3()
        right = (basis @ Vector((1, 0, 0))).normalized()
        up = (basis @ Vector((0, 1, 0))).normalized()
        forward = (basis @ Vector((0, 0, 1))).normalized()
    else:
        pose_bone = armature.pose.bones.get("Head")
        center = armature.matrix_world @ (pose_bone.head + (pose_bone.tail - pose_bone.head) * 0.55) if pose_bone else Vector((0, 0, 1.65))
        right, up, forward = Vector((1, 0, 0)), Vector((0, 0, 1)), Vector((0, -1, 0))
    center -= up * 0.075
    center += forward * 0.025
    basis_matrix = Matrix(((right.x, up.x, forward.x, center.x),
                           (right.y, up.y, forward.y, center.y),
                           (right.z, up.z, forward.z, center.z),
                           (0, 0, 0, 1)))
    mouth_mat = _material("SHORTFORGE facial expression ink", (0.035, 0.025, 0.035, 1))
    mouths = {}
    for emotion, path in MOUTHS.items():
        obj = _curve_object(f"FaceExpression_{emotion}", path, basis_matrix, mouth_mat)
        _attach_to_head(obj, armature)
        obj.hide_render = emotion != "neutral"
        obj.hide_viewport = emotion != "neutral"
        obj["emotion"] = emotion
        mouths[emotion] = obj
    return brow_keys, eye_keys, mouths


def add_rigged_avatar(model_path, avatar_id, location=(0.0, 0.0, 0.0), rotation_z=180.0, scale=1.0):
    model_path = Path(model_path).resolve()
    if not model_path.is_file():
        raise FileNotFoundError(f"Avatar asset not found: {model_path}")
    root, armature, imported = _import_gltf(model_path, avatar_id)
    root.location = Vector(location)
    root.rotation_euler.z = math.radians(rotation_z)
    root.scale = (scale, scale, scale)

    palette = PALETTES.get(avatar_id, PALETTES["hero_male"])
    body = next((o for o in imported if o.type == "MESH" and any(k in o.name.lower() for k in ("superhero", "superhero_male", "superhero_female"))), None)
    if body:
        body.data.materials.clear()
        body.data.materials.append(_material(f"{avatar_id} tailored hero suit", palette["suit"]))

    brow_keys, eye_keys, mouths = _add_face_expressions(armature, imported)
    pose_json = json.dumps(POSES, sort_keys=True)
    emotion_json = json.dumps(list(EMOTIONS))
    root["available_emotions"] = emotion_json
    root["available_poses"] = json.dumps(list(POSES.keys()))
    armature["shortforge_pose_presets"] = pose_json
    armature["shortforge_emotion_presets"] = emotion_json
    armature["shortforge_avatar_id"] = avatar_id
    armature["shortforge_rig_bones"] = len(armature.data.bones)
    armature["shortforge_face_controls"] = len(mouths) + len(brow_keys) + len(eye_keys)
    return {"root": root, "armature": armature, "imported": imported, "brow_keys": brow_keys, "eye_keys": eye_keys, "mouths": mouths}


def apply_pose(armature, pose_name: str, frame: int | None = None):
    if pose_name not in POSES:
        raise ValueError(f"Unknown avatar pose {pose_name!r}; choose from {list(POSES)}")
    for bone in armature.pose.bones:
        bone.rotation_mode = "XYZ"
        bone.rotation_euler = (0.0, 0.0, 0.0)
    for bone_name, degrees in POSES[pose_name].items():
        bone = armature.pose.bones.get(bone_name)
        if bone:
            bone.rotation_euler = tuple(math.radians(v) for v in degrees)
    if frame is not None:
        for bone in armature.pose.bones:
            bone.keyframe_insert(data_path="rotation_euler", frame=frame, group=bone.name)
    armature["active_pose"] = pose_name


def apply_emotion(avatar, emotion_name: str, frame: int | None = None):
    if emotion_name not in EMOTIONS:
        raise ValueError(f"Unknown avatar emotion {emotion_name!r}; choose from {list(EMOTIONS)}")
    for key in avatar["brow_keys"].values():
        key.value = 0.0
        if frame is not None:
            key.keyframe_insert(data_path="value", frame=frame)
    for key in avatar["eye_keys"].values():
        key.value = 0.0
        if frame is not None:
            key.keyframe_insert(data_path="value", frame=frame)
    for key_map in (avatar["brow_keys"], avatar["eye_keys"]):
        key = key_map.get(emotion_name)
        if key:
            key.value = 1.0
            if frame is not None:
                key.keyframe_insert(data_path="value", frame=frame)
    for name, mouth in avatar["mouths"].items():
        mouth.hide_render = name != emotion_name
        mouth.hide_viewport = name != emotion_name
        if frame is not None:
            mouth.keyframe_insert(data_path="hide_render", frame=frame)
    avatar["root"]["active_emotion"] = emotion_name


def animate_avatar(avatar, config, fps: int, total_frames: int):
    shots = config.get("shots", [])
    armature = avatar["armature"]
    root = avatar["root"]
    spawn = Vector(config.get("character", {}).get("position", [0.0, -0.4, 0.0]))
    for index, shot in enumerate(shots):
        frame = max(1, int(float(shot.get("start_seconds", 0)) * fps) + 1)
        end_frame = min(total_frames, frame + int(float(shot.get("duration_seconds", 1)) * fps) - 1)
        apply_pose(armature, shot.get("pose", "neutral"), frame)
        apply_emotion(avatar, shot.get("emotion", "neutral"), frame)
        drift = float(shot.get("character_x", 0.0))
        root.location = (spawn.x + drift, spawn.y, spawn.z)
        root.keyframe_insert(data_path="location", frame=frame)
        root.location = (spawn.x + drift + float(shot.get("character_drift", 0.0)), spawn.y, spawn.z)
        root.keyframe_insert(data_path="location", frame=end_frame)
    return avatar


def avatar_library_manifest():
    return {
        "source": "Quaternius Universal Base Characters — Standard",
        "source_license": "CC0-1.0",
        "source_url": "https://quaternius.com/packs/universalbasecharacters.html",
        "emotions": list(EMOTIONS),
        "poses": list(POSES.keys()),
        "rig": "65-bone humanoid skeleton",
        "notes": "Each .blend includes a skinned humanoid, facial expression controls and stored JSON pose/emotion presets. Poses are applied with SHORTFORGE avatar_system.apply_pose().",
    }
