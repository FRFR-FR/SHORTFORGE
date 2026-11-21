#!/usr/bin/env python3
"""
LINEFORGE — code-authored, frame-by-frame Grease Pencil anime in a real 3D scene.

The protagonist is NOT a mesh, SVG, image plane, cut-out rig or collection of 2D
parts. Every visible character mark is an individually defined Grease Pencil
stroke, re-authored into a new 3D drawing for every rendered frame.
"""
import bpy
import math
import os
import sys
import json
import random
from mathutils import Vector

FPS = int(os.environ.get("LINEFORGE_FPS", "30"))
SECONDS = float(os.environ.get("LINEFORGE_SECONDS", "6"))
WIDTH = int(os.environ.get("LINEFORGE_WIDTH", "1280"))
HEIGHT = int(os.environ.get("LINEFORGE_HEIGHT", "720"))
FRAME_COUNT = int(round(FPS * SECONDS))
TAU = math.pi * 2.0

# ---------- Hand-authored ink catalogue ----------
# Coordinates are local drawing coordinates. Each entry is a separate stroke.
# style: 0 ink, 1 shadow/hatching, 2 cool rim, 3 hot energy.
STROKES = []

def line(part, pts, weight=1.0, style=0, depth=0.0, taper=True, wobble=0.003):
    STROKES.append({
        "part": part, "pts": pts, "weight": weight, "style": style,
        "depth": depth, "taper": taper, "wobble": wobble
    })

# HEAD — face silhouette, angular planes, ear, expressive eyes and hair.
line("head", [(-0.50,0.34),(-0.55,0.62),(-0.42,0.91),(-0.17,1.08),(0.16,1.07),(0.43,0.86),(0.53,0.55),(0.48,0.22),(0.35,-0.13),(0.12,-0.43),(-0.10,-0.52),(-0.34,-0.34),(-0.48,-0.03)], 2.3, 0, -0.04)
line("head", [(-0.45,0.28),(-0.54,0.47),(-0.49,0.67),(-0.32,0.87),(-0.10,0.99),(0.20,0.99),(0.41,0.82)], 1.2, 1, -0.03)
line("head", [(-0.47,0.10),(-0.58,0.02),(-0.59,-0.20),(-0.48,-0.34),(-0.34,-0.31)], 1.8, 0, -0.05)
line("head", [(-0.55,-0.09),(-0.70,-0.03),(-0.73,0.12),(-0.64,0.21),(-0.53,0.16)], 1.3, 0, -0.02)
line("head", [(-0.65,0.12),(-0.59,0.17),(-0.56,0.07),(-0.63,0.02)], 0.8, 1, -0.06)
line("head", [(0.42,0.31),(0.56,0.40),(0.68,0.30),(0.67,0.08),(0.52,-0.05)], 1.7, 0, -0.02)
line("head", [(0.56,0.27),(0.62,0.22),(0.58,0.09),(0.53,0.13)], 0.8, 1, -0.04)
# Hair mass is represented only by ink contours and individual locks.
line("hair", [(-0.57,0.42),(-0.78,0.73),(-0.66,0.72),(-0.89,1.06),(-0.48,0.94),(-0.55,1.31),(-0.18,1.12),(0.02,1.43),(0.19,1.15),(0.53,1.26),(0.43,0.97),(0.75,1.04),(0.58,0.78),(0.67,0.58)], 2.6, 0, -0.18)
line("hair", [(-0.60,0.63),(-0.78,0.93),(-0.43,0.81),(-0.50,1.16),(-0.17,0.96),(0.00,1.30),(0.12,0.99),(0.38,1.12),(0.31,0.88)], 1.6, 0, -0.21)
line("hair", [(-0.43,0.75),(-0.37,0.52),(-0.22,0.35),(-0.09,0.19)], 1.3, 0, -0.23)
line("hair", [(-0.30,0.91),(-0.22,0.65),(-0.09,0.45),(0.02,0.28)], 1.4, 0, -0.24)
line("hair", [(-0.08,1.02),(-0.03,0.78),(0.10,0.54),(0.16,0.31)], 1.3, 0, -0.23)
line("hair", [(0.17,1.00),(0.21,0.76),(0.34,0.56),(0.43,0.42)], 1.3, 0, -0.22)
line("hair", [(0.43,0.88),(0.36,0.67),(0.43,0.52),(0.56,0.40)], 1.2, 0, -0.20)
line("hair", [(-0.51,0.52),(-0.37,0.36),(-0.31,0.15)], 0.9, 1, -0.24)
line("hair", [(-0.20,0.44),(-0.14,0.25),(-0.07,0.10)], 0.9, 1, -0.25)
line("hair", [(0.04,0.48),(0.14,0.27),(0.24,0.10)], 0.9, 1, -0.25)
line("hair", [(0.32,0.52),(0.40,0.32),(0.48,0.15)], 0.9, 1, -0.23)
# Eyes, brows, lashes, iris rings and catchlights.
line("head", [(-0.43,0.22),(-0.31,0.31),(-0.14,0.30),(0.00,0.19),(-0.10,0.04),(-0.28,0.03),(-0.40,0.11),(-0.43,0.22)], 1.9, 0, -0.12)
line("head", [(-0.42,0.22),(-0.30,0.37),(-0.12,0.35),(0.01,0.23)], 2.6, 0, -0.13)
line("head", [(-0.32,0.06),(-0.22,0.00),(-0.07,0.03)], 0.9, 1, -0.12)
line("head", [(-0.26,0.07),(-0.24,0.21),(-0.17,0.25),(-0.10,0.18),(-0.13,0.06),(-0.21,0.02),(-0.26,0.07)], 1.25, 0, -0.16)
line("head", [(-0.20,0.09),(-0.19,0.18),(-0.16,0.20),(-0.14,0.12),(-0.16,0.06)], 0.9, 0, -0.17)
line("head", [(-0.19,0.18),(-0.16,0.22)], 0.6, 2, -0.18)
line("head", [(-0.43,0.25),(-0.47,0.35),(-0.39,0.31)], 1.0, 0, -0.16)
line("head", [(-0.32,0.37),(-0.21,0.41),(-0.08,0.38)], 1.8, 0, -0.12)
line("head", [(0.08,0.18),(0.20,0.30),(0.37,0.31),(0.49,0.20),(0.44,0.05),(0.28,-0.02),(0.14,0.06),(0.08,0.18)], 1.9, 0, -0.12)
line("head", [(0.09,0.19),(0.23,0.39),(0.40,0.37),(0.51,0.23)], 2.5, 0, -0.13)
line("head", [(0.17,0.04),(0.29,-0.02),(0.42,0.03)], 0.8, 1, -0.12)
line("head", [(0.25,0.08),(0.28,0.21),(0.36,0.25),(0.43,0.17),(0.40,0.05),(0.32,0.00),(0.25,0.08)], 1.2, 0, -0.16)
line("head", [(0.32,0.10),(0.34,0.19),(0.38,0.20),(0.39,0.10)], 0.8, 0, -0.18)
line("head", [(0.38,0.18),(0.41,0.23)], 0.7, 2, -0.19)
line("head", [(0.17,0.37),(0.29,0.42),(0.43,0.37)], 1.8, 0, -0.12)
line("head", [(-0.02,0.22),(0.02,0.14),(0.04,0.04)], 0.9, 1, -0.10)
line("head", [(0.00,-0.06),(0.08,-0.15),(0.20,-0.18)], 1.2, 0, -0.10)
line("head", [(0.18,-0.19),(0.25,-0.16),(0.32,-0.18)], 1.5, 0, -0.12)
line("head", [(0.07,-0.28),(0.20,-0.33),(0.34,-0.29)], 1.1, 0, -0.11)
line("head", [(0.12,-0.36),(0.23,-0.38)], 0.7, 1, -0.12)
# Face planes and shadow hatching.
line("head", [(-0.46,0.02),(-0.38,-0.12),(-0.31,-0.20)], 1.2, 1, -0.10)
line("head", [(-0.40,-0.16),(-0.33,-0.24)], 0.8, 1, -0.10)
line("head", [(0.43,-0.04),(0.36,-0.16),(0.26,-0.25)], 1.2, 1, -0.10)
line("head", [(0.40,-0.17),(0.31,-0.28)], 0.8, 1, -0.11)
line("head", [(-0.04,-0.42),(0.02,-0.47),(0.11,-0.48)], 0.8, 1, -0.11)
line("head", [(0.50,0.02),(0.56,-0.06),(0.53,-0.18)], 0.9, 2, -0.10)
# Neck and collar.
line("neck", [(-0.26,0.10),(-0.27,-0.22),(-0.40,-0.44)], 1.7, 0, -0.05)
line("neck", [(0.28,0.07),(0.27,-0.18),(0.43,-0.43)], 1.7, 0, -0.05)
line("neck", [(-0.22,-0.20),(-0.12,-0.31),(0.00,-0.34)], 1.1, 1, -0.06)
line("neck", [(0.20,-0.20),(0.11,-0.31),(0.02,-0.34)], 1.0, 1, -0.06)

# TORSO — tailored asymmetrical tech jacket, layered collar, zipper, seams and folds.
line("torso", [(-0.72,0.65),(-0.54,0.82),(-0.28,0.91),(0.04,0.88),(0.34,0.80),(0.62,0.60),(0.77,0.18),(0.70,-0.40),(0.52,-0.94),(0.26,-1.13),(-0.34,-1.10),(-0.61,-0.82),(-0.77,-0.22),(-0.72,0.65)], 2.5, 0, 0.00)
line("torso", [(-0.72,0.58),(-0.88,0.35),(-0.93,-0.14),(-0.80,-0.64),(-0.56,-0.95)], 1.6, 0, 0.02)
line("torso", [(0.66,0.55),(0.90,0.34),(1.00,-0.05),(0.90,-0.55),(0.60,-0.98)], 1.6, 0, 0.02)
line("torso", [(-0.29,0.78),(-0.18,0.53),(0.00,0.38),(0.20,0.58),(0.36,0.78)], 2.0, 0, -0.08)
line("torso", [(-0.28,0.79),(-0.45,0.49),(-0.30,0.20),(-0.04,0.03)], 1.6, 0, -0.09)
line("torso", [(0.34,0.76),(0.52,0.44),(0.34,0.15),(0.09,0.02)], 1.6, 0, -0.09)
line("torso", [(-0.11,0.77),(-0.02,0.56),(0.09,0.77)], 1.4, 2, -0.13)
line("torso", [(-0.39,0.36),(-0.20,0.08),(0.02,-0.05),(0.19,0.08),(0.38,0.39)], 1.6, 0, -0.12)
line("torso", [(-0.07,0.04),(-0.10,-0.45),(-0.04,-0.90)], 1.3, 0, -0.14)
line("torso", [(0.10,0.06),(0.15,-0.42),(0.10,-0.91)], 1.1, 1, -0.14)
line("torso", [(-0.16,-0.10),(-0.22,-0.52),(-0.18,-0.95)], 0.9, 1, -0.12)
line("torso", [(0.31,0.25),(0.50,0.02),(0.44,-0.35),(0.32,-0.70)], 1.3, 0, -0.08)
line("torso", [(-0.47,0.28),(-0.60,0.01),(-0.51,-0.33),(-0.39,-0.59)], 1.2, 0, -0.08)
# Chest straps, hardware, zipper and engraved seam details.
line("torso", [(-0.46,0.28),(-0.18,-0.02),(0.02,-0.16),(0.31,0.02),(0.52,0.29)], 1.0, 2, -0.16)
line("torso", [(-0.34,-0.16),(-0.23,-0.30),(-0.12,-0.32)], 1.0, 0, -0.17)
line("torso", [(0.26,-0.14),(0.39,-0.26),(0.48,-0.20)], 1.0, 0, -0.17)
line("torso", [(-0.06,-0.20),(-0.03,-0.82),(0.02,-1.02)], 1.6, 0, -0.18)
line("torso", [(0.00,-0.28),(0.05,-0.75),(0.08,-0.93)], 0.6, 2, -0.20)
line("torso", [(-0.03,-0.38),(0.02,-0.38)], 1.2, 3, -0.22)
line("torso", [(-0.02,-0.54),(0.04,-0.54)], 1.2, 3, -0.22)
line("torso", [(-0.02,-0.70),(0.04,-0.70)], 1.2, 3, -0.22)
line("torso", [(-0.53,-0.38),(-0.36,-0.46),(-0.26,-0.43)], 1.0, 0, -0.10)
line("torso", [(0.43,-0.38),(0.55,-0.44),(0.61,-0.40)], 1.0, 0, -0.10)
line("torso", [(-0.56,-0.62),(-0.40,-0.69),(-0.26,-0.67)], 1.0, 1, -0.12)
line("torso", [(0.40,-0.64),(0.53,-0.72),(0.62,-0.68)], 1.0, 1, -0.12)
line("torso", [(-0.39,-0.88),(-0.20,-0.98),(0.00,-0.96)], 1.0, 1, -0.12)
line("torso", [(0.20,-0.97),(0.40,-0.91),(0.53,-0.80)], 1.0, 1, -0.12)
# Jacket folds — directional strokes, not filled polygons.
line("torso", [(-0.60,0.46),(-0.47,0.21),(-0.42,-0.04)], 1.0, 1, -0.10)
line("torso", [(-0.65,0.16),(-0.55,-0.10),(-0.53,-0.30)], 0.8, 1, -0.10)
line("torso", [(0.60,0.42),(0.50,0.12),(0.55,-0.17)], 1.0, 1, -0.10)
line("torso", [(0.66,0.10),(0.72,-0.16),(0.65,-0.37)], 0.8, 1, -0.10)
line("torso", [(-0.26,0.40),(-0.16,0.25),(-0.10,0.14)], 0.9, 1, -0.12)
line("torso", [(0.25,0.42),(0.15,0.28),(0.12,0.12)], 0.9, 1, -0.12)
line("torso", [(-0.33,-0.47),(-0.22,-0.60),(-0.14,-0.76)], 0.8, 1, -0.12)
line("torso", [(0.32,-0.43),(0.24,-0.56),(0.22,-0.75)], 0.8, 1, -0.12)
line("torso", [(-0.67,-0.50),(-0.56,-0.43),(-0.48,-0.32)], 0.7, 1, -0.11)
line("torso", [(0.68,-0.45),(0.56,-0.34),(0.48,-0.26)], 0.7, 1, -0.11)
# Collar, neck details, straps.
line("torso", [(-0.31,0.77),(-0.52,0.95),(-0.38,1.03),(-0.12,0.91)], 1.6, 0, -0.20)
line("torso", [(0.31,0.77),(0.52,0.96),(0.38,1.05),(0.12,0.91)], 1.6, 0, -0.20)
line("torso", [(-0.45,0.94),(-0.34,0.83),(-0.20,0.80)], 0.9, 2, -0.22)
line("torso", [(0.45,0.95),(0.32,0.84),(0.21,0.81)], 0.9, 2, -0.22)
line("torso", [(-0.60,0.60),(-0.73,0.37),(-0.68,0.10)], 1.1, 2, -0.08)
line("torso", [(0.62,0.56),(0.76,0.33),(0.72,0.08)], 1.1, 2, -0.08)
# Buckles and garment labels are tiny hand-drawn marks.
line("torso", [(-0.34,-0.56),(-0.25,-0.56),(-0.25,-0.43),(-0.34,-0.43),(-0.34,-0.56)], 0.9, 0, -0.22)
line("torso", [(-0.32,-0.51),(-0.27,-0.51)], 0.5, 2, -0.23)
line("torso", [(0.39,-0.56),(0.50,-0.56),(0.50,-0.43),(0.39,-0.43),(0.39,-0.56)], 0.9, 0, -0.22)
line("torso", [(0.41,-0.50),(0.48,-0.50)], 0.5, 2, -0.23)

# NEAR ARM — foreshortened striking arm and a properly drawn fist.
line("armNear", [(0.00,0.10),(0.20,0.32),(0.49,0.38),(0.73,0.21),(0.82,-0.06),(0.70,-0.35),(0.43,-0.57),(0.18,-0.44),(-0.03,-0.17)], 2.2, 0, -0.03)
line("armNear", [(0.04,0.02),(0.23,0.13),(0.50,0.16),(0.71,0.03)], 1.2, 1, -0.06)
line("armNear", [(0.08,-0.18),(0.26,-0.37),(0.52,-0.46),(0.71,-0.31)], 1.5, 0, -0.08)
line("armNear", [(0.15,0.25),(0.30,0.48),(0.57,0.52),(0.76,0.36)], 1.3, 0, -0.05)
line("armNear", [(0.22,0.20),(0.40,0.33),(0.62,0.31)], 0.8, 1, -0.09)
line("armNear", [(0.26,-0.36),(0.34,-0.18),(0.52,-0.08)], 0.9, 1, -0.10)
line("armNear", [(0.47,-0.49),(0.57,-0.37),(0.68,-0.27)], 0.8, 1, -0.12)
# fist contour and knuckles
line("armNear", [(0.68,-0.16),(0.76,0.02),(0.98,0.16),(1.18,0.14),(1.34,0.03),(1.40,-0.16),(1.30,-0.35),(1.12,-0.43),(0.90,-0.40),(0.77,-0.29),(0.68,-0.16)], 2.4, 0, -0.70)
line("armNear", [(0.80,0.05),(0.91,0.25),(1.08,0.30),(1.20,0.24),(1.29,0.11)], 1.4, 0, -0.75)
line("armNear", [(0.88,-0.03),(1.00,0.10),(1.11,0.12),(1.21,0.04),(1.27,-0.08)], 1.2, 0, -0.78)
line("armNear", [(1.01,-0.42),(1.03,-0.26),(1.12,-0.18),(1.21,-0.20)], 1.1, 0, -0.78)
line("armNear", [(1.17,-0.40),(1.20,-0.28),(1.28,-0.20)], 0.9, 1, -0.78)
line("armNear", [(0.81,-0.23),(0.94,-0.19),(1.02,-0.23)], 0.8, 1, -0.76)
line("armNear", [(0.90,0.18),(0.95,0.26)], 0.8, 2, -0.79)
line("armNear", [(1.10,0.26),(1.15,0.31)], 0.8, 2, -0.79)
line("armNear", [(1.34,-0.08),(1.45,-0.02),(1.49,-0.12)], 0.9, 0, -0.75)
# cuff, panel stitching and sleeve folds
line("armNear", [(0.16,-0.32),(0.25,-0.52),(0.44,-0.64),(0.59,-0.54)], 1.6, 0, -0.15)
line("armNear", [(0.23,-0.38),(0.37,-0.46),(0.52,-0.42)], 0.8, 2, -0.18)
line("armNear", [(0.25,0.30),(0.19,0.07),(0.22,-0.12)], 0.9, 1, -0.10)
line("armNear", [(0.46,0.40),(0.42,0.19),(0.46,0.02)], 0.8, 1, -0.11)
line("armNear", [(0.64,0.35),(0.62,0.16),(0.70,-0.01)], 0.8, 1, -0.11)
line("armNear", [(0.40,-0.55),(0.46,-0.65),(0.60,-0.62)], 0.9, 0, -0.19)

# FAR ARM — bent guard arm, sleeve and open hand.
line("armFar", [(0.02,0.00),(-0.15,-0.16),(-0.34,-0.38),(-0.48,-0.66),(-0.39,-0.91),(-0.15,-1.02),(0.05,-0.85),(0.17,-0.57),(0.16,-0.23)], 2.0, 0, 0.08)
line("armFar", [(-0.08,-0.13),(-0.27,-0.37),(-0.34,-0.62)], 1.0, 1, 0.05)
line("armFar", [(-0.39,-0.67),(-0.22,-0.75),(-0.04,-0.72),(0.08,-0.61)], 1.4, 0, 0.03)
line("armFar", [(-0.34,-0.78),(-0.22,-0.93),(-0.05,-0.97)], 0.9, 1, 0.02)
line("armFar", [(-0.38,-0.72),(-0.54,-0.83),(-0.60,-0.98),(-0.47,-1.10),(-0.27,-1.06)], 1.5, 0, 0.02)
line("armFar", [(-0.54,-0.88),(-0.66,-0.90),(-0.72,-0.82)], 1.0, 0, 0.00)
line("armFar", [(-0.45,-1.04),(-0.48,-1.18),(-0.36,-1.23),(-0.25,-1.13)], 1.0, 0, 0.00)
line("armFar", [(-0.25,-1.06),(-0.18,-1.18),(-0.05,-1.17),(0.00,-1.06)], 1.0, 0, 0.00)
line("armFar", [(-0.54,-0.82),(-0.40,-0.90),(-0.28,-0.91)], 0.8, 1, 0.00)
line("armFar", [(-0.35,-0.54),(-0.19,-0.59),(-0.06,-0.52)], 0.8, 1, 0.00)
line("armFar", [(-0.39,-0.71),(-0.29,-0.77),(-0.18,-0.74)], 0.8, 2, -0.03)

# LEGS — layered trousers, knee articulation, boot profiles and tension folds.
line("legNear", [(-0.05,0.20),(-0.27,-0.06),(-0.36,-0.40),(-0.28,-0.78),(-0.08,-1.02),(0.20,-1.07),(0.38,-0.84),(0.35,-0.53),(0.22,-0.20),(0.15,0.13)], 2.1, 0, 0.05)
line("legNear", [(-0.28,-0.12),(-0.12,-0.40),(0.05,-0.51),(0.31,-0.44)], 1.2, 1, 0.03)
line("legNear", [(-0.29,-0.46),(-0.10,-0.67),(0.11,-0.75),(0.33,-0.69)], 1.4, 0, 0.02)
line("legNear", [(-0.18,-0.24),(-0.22,-0.52),(-0.14,-0.78)], 0.8, 1, 0.00)
line("legNear", [(0.16,-0.20),(0.23,-0.47),(0.19,-0.63)], 0.8, 1, 0.00)
line("legNear", [(-0.20,-0.80),(-0.12,-0.94),(0.10,-0.99),(0.28,-0.88)], 1.1, 0, 0.00)
line("legNear", [(-0.10,-1.01),(-0.16,-1.22),(-0.38,-1.37),(-0.34,-1.50),(0.20,-1.50),(0.40,-1.36),(0.31,-1.18),(0.20,-1.04)], 2.0, 0, -0.10)
line("legNear", [(-0.34,-1.37),(-0.12,-1.30),(0.22,-1.34)], 1.1, 0, -0.14)
line("legNear", [(-0.23,-1.46),(0.12,-1.44),(0.29,-1.37)], 0.9, 2, -0.16)
line("legNear", [(-0.23,-1.20),(-0.18,-1.06),(-0.08,-1.00)], 0.9, 1, -0.14)
line("legFar", [(0.05,0.20),(0.26,-0.04),(0.53,-0.31),(0.65,-0.60),(0.55,-0.83),(0.32,-0.95),(0.09,-0.83),(-0.03,-0.57),(-0.12,-0.30)], 2.0, 0, 0.18)
line("legFar", [(0.24,-0.13),(0.42,-0.38),(0.47,-0.58),(0.36,-0.76)], 1.0, 1, 0.14)
line("legFar", [(0.55,-0.60),(0.39,-0.53),(0.22,-0.58)], 1.1, 0, 0.12)
line("legFar", [(0.32,-0.95),(0.28,-1.16),(0.12,-1.29),(0.18,-1.40),(0.62,-1.40),(0.78,-1.28),(0.67,-1.12),(0.55,-0.93)], 1.9, 0, 0.05)
line("legFar", [(0.18,-1.28),(0.46,-1.22),(0.70,-1.27)], 0.9, 1, 0.02)
line("legFar", [(0.29,-1.38),(0.56,-1.35),(0.68,-1.29)], 0.8, 2, 0.00)
# Belt, straps, seam and cross-hatch marks.
line("torso", [(-0.51,-0.98),(-0.39,-1.14),(-0.16,-1.20),(0.12,-1.17),(0.44,-1.10),(0.55,-0.94)], 1.5, 0, -0.03)
line("torso", [(-0.16,-1.16),(-0.13,-1.28),(0.10,-1.30),(0.12,-1.17)], 1.1, 0, -0.10)
line("torso", [(-0.08,-1.22),(0.03,-1.22)], 0.6, 2, -0.12)
line("legNear", [(-0.23,-0.54),(-0.13,-0.61),(-0.05,-0.60)], 0.9, 1, 0.00)
line("legNear", [(-0.18,-0.59),(-0.08,-0.67),(0.02,-0.66)], 0.7, 1, -0.02)
line("legFar", [(0.42,-0.40),(0.54,-0.46),(0.59,-0.55)], 0.8, 1, 0.10)
line("legFar", [(0.38,-0.45),(0.48,-0.55),(0.52,-0.62)], 0.7, 1, 0.08)

# Small, individually drawn hatching strokes give form rather than flat colour.
for i in range(9):
    x = -0.48 + i * 0.045
    z = -0.12 - (i % 3) * 0.055
    line("head", [(x,z),(x+0.055,z-0.07)], 0.50, 1, -0.12, True, 0.001)
for i in range(12):
    x = -0.57 + i * 0.035
    z = -0.61 + (i % 4) * 0.035
    line("torso", [(x,z),(x+0.06,z-0.10)], 0.52, 1, -0.16, True, 0.001)
for i in range(10):
    x = 0.25 + i * 0.025
    z = -0.57 - (i % 3) * 0.045
    line("armNear", [(x,z),(x+0.04,z-0.09)], 0.48, 1, -0.18, True, 0.001)
for i in range(8):
    x = -0.18 + i * 0.035
    z = -0.64 - (i % 2) * 0.055
    line("legNear", [(x,z),(x+0.055,z-0.085)], 0.48, 1, 0.01, True, 0.001)

# ---------- 3D environment ----------
def principled(name, color, roughness=0.5, metallic=0.0, emission=None, strength=0.0):
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*color, 1.0)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    return material

MAT_BUILDING = principled("Midnight ceramic composite", (0.018,0.032,0.065), 0.32, 0.55)
MAT_PANEL = principled("Graphite steel panels", (0.045,0.064,0.105), 0.29, 0.72)
MAT_GROUND = principled("Wet asphalt", (0.012,0.019,0.038), 0.18, 0.62)
MAT_WINDOW_CYAN = principled("Window cyan", (0.02,0.24,0.34), 0.26, 0.2, (0.02,0.85,1.0), 3.0)
MAT_WINDOW_PINK = principled("Window magenta", (0.25,0.02,0.16), 0.28, 0.1, (1.0,0.015,0.28), 3.6)
MAT_WINDOW_WARM = principled("Window amber", (0.32,0.12,0.025), 0.28, 0.05, (1.0,0.28,0.04), 2.2)
MAT_NEON_WHITE = principled("Neon white", (0.55,0.8,0.9), 0.2, 0.1, (0.55,0.95,1.0), 4.0)
MAT_RAIL = principled("Brushed alloy", (0.09,0.13,0.19), 0.24, 0.86)
MAT_RED = principled("Signal red", (0.4,0.015,0.07), 0.2, 0.4, (1.0,0.015,0.07), 2.8)

def cube(name, loc, scale, material, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    if bevel:
        mod = obj.modifiers.new("Machined softened edges", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        mod.profile = 0.5
        obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return obj

def cylinder_between(name, a, b, radius, material, vertices=12):
    start, end = Vector(a), Vector(b)
    direction = end - start
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=direction.length, location=(start+end)*0.5)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = direction.to_track_quat("Z", "Y")
    obj.data.materials.append(material)
    return obj

def curve_wire(name, points, material, bevel=0.018):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 2
    curve.bevel_depth = bevel
    curve.bevel_resolution = 2
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points)-1)
    for point, coord in zip(spline.bezier_points, points):
        point.co = coord
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj

def build_tower(name, x, y, width, depth, height, seed):
    rng = random.Random(seed)
    cube(name + " core", (x,y,height*0.5), (width,depth,height), MAT_BUILDING, 0.12)
    # Structural ribs and inset facade bands create a dense, layered skyline.
    for side in (-1,1):
        xx = x + side*(width*0.49)
        cube(name+" corner rib", (xx,y-depth*0.505,height*0.5), (0.11,0.10,height*0.98), MAT_PANEL, 0.025)
    cube(name+" crown", (x,y,height+0.08), (width+0.18,depth+0.16,0.16), MAT_RAIL, 0.035)
    cols = max(3, int(width/0.38))
    rows = max(5, int(height/0.58))
    for row in range(rows):
        for col in range(cols):
            wx = x - width*0.42 + col*(width*0.84/max(1,cols-1))
            wz = 0.42 + row*(height-0.82)/max(1,rows-1)
            lit = rng.random()
            if lit < 0.19:
                wm = MAT_WINDOW_CYAN
            elif lit < 0.29:
                wm = MAT_WINDOW_PINK
            elif lit < 0.35:
                wm = MAT_WINDOW_WARM
            else:
                continue
            cube(name+" window", (wx,y-depth*0.515,wz), (0.16,0.025,0.24), wm, 0.012)
    # Antenna trusses and rooftop machinery.
    for i in range(3):
        xx = x + (i-1)*width*0.23
        cylinder_between(name+" rooftop mast", (xx,y,height+0.12), (xx+0.04,y,height+0.62+rng.random()*0.35), 0.025, MAT_RAIL, 8)
    for band in range(2, int(height), 3):
        cube(name+" facade band", (x,y-depth*0.53,band), (width*0.96,0.04,0.055), MAT_RAIL, 0.01)
    return

def create_environment():
    cube("Wet city avenue", (0,3,-0.20), (34,44,0.38), MAT_GROUND, 0.02)
    # Deep perspective alleys: towers on both sides with distinct silhouettes.
    buildings = [
        ("West 01",-8.2,3.0,4.7,4.0,12.0,41),
        ("West 02",-5.8,8.5,3.3,3.6,8.6,42),
        ("West 03",-10.8,12.0,3.8,4.3,15.0,43),
        ("East 01",8.0,4.2,4.5,4.0,13.5,51),
        ("East 02",5.7,9.0,3.2,3.6,9.5,52),
        ("East 03",10.4,13.0,4.0,4.5,16.0,53),
        ("Far tower",-1.5,22.0,6.5,5.0,18.0,61)
    ]
    for args in buildings:
        build_tower(*args)
    # Street-level shops, ducts, bridge structure and a layered overhead crossing.
    for side in (-1,1):
        sx = side*4.2
        cube("Street-level shop fascia", (sx,0.8,3.5), (3.2,1.2,2.1), MAT_PANEL, 0.12)
        cube("Shop canopy", (sx,-0.05,4.65), (3.4,1.6,0.18), MAT_RAIL, 0.04)
        for j in range(4):
            cube("Shop glass", (sx-1.1+j*0.72,0.17,3.43), (0.52,0.035,1.42), MAT_WINDOW_CYAN if (j+side)%2 else MAT_WINDOW_PINK, 0.018)
        cylinder_between("Vertical utility pipe", (side*6.0,-0.15,0.2), (side*6.0,-0.15,7.4), 0.075, MAT_RAIL, 12)
        for z in (1.0,2.4,4.0,5.7):
            cylinder_between("Pipe brackets", (side*5.8,-0.18,z), (side*6.2,-0.18,z), 0.035, MAT_NEON_WHITE, 8)
    cube("Elevated walkway deck", (0,2.0,7.1), (12.0,1.0,0.28), MAT_RAIL, 0.08)
    for x in (-5.7,-4.1,4.1,5.7):
        cylinder_between("Walkway support", (x,2.0,0.2), (x,2.0,7.0), 0.12, MAT_RAIL, 12)
    for x in (-5.5,5.5):
        curve_wire("Overhead cable", [(x,4.5,11.5),(x*0.65,1.8,10.6),(x*0.25,-1.0,10.4)], MAT_RAIL, 0.025)
    # Neon sign frames, extruded letters and emissive strips.
    for x, sign_y, z, mat in [(-4.2,-0.10,5.2,MAT_WINDOW_PINK),(4.1,-0.14,5.0,MAT_WINDOW_CYAN)]:
        cube("Neon sign backing", (x,sign_y,z), (2.15,0.16,0.70), MAT_BUILDING, 0.06)
        cube("Neon sign top stroke", (x,sign_y-0.10,z+0.25), (1.90,0.035,0.035), mat, 0.01)
        cube("Neon sign lower stroke", (x,sign_y-0.10,z-0.25), (1.90,0.035,0.035), mat, 0.01)
        cube("Neon sign left stroke", (x-0.93,sign_y-0.10,z), (0.035,0.035,0.48), mat, 0.01)
        cube("Neon sign right stroke", (x+0.93,sign_y-0.10,z), (0.035,0.035,0.48), mat, 0.01)
    # Text is environmental signage, not character artwork.
    font = bpy.data.curves.new("AFTERHOUR typography", "FONT")
    font.body = "AFTERHOUR  /  09"
    font.size = 0.32
    font.extrude = 0.006
    text_obj = bpy.data.objects.new("AFTERHOUR 09 sign", font)
    bpy.context.collection.objects.link(text_obj)
    text_obj.location = (-5.1,-0.20,5.15)
    text_obj.rotation_euler[0] = math.radians(90)
    text_obj.data.materials.append(MAT_NEON_WHITE)
    # Wet street lane markings converge toward the vanishing point.
    for side in (-1,1):
        curve_wire("Perspective lane light", [(side*3.7,-8,0.015),(side*2.5,1,0.018),(side*1.2,14,0.02),(side*0.45,24,0.02)], MAT_WINDOW_CYAN, 0.012)
    for i in range(8):
        x = -3.5 + i
        cube("Road inset reflector", (x, -1.0-(i%3)*2.8, 0.015), (0.10,0.55,0.025), MAT_WINDOW_PINK if i%3==0 else MAT_WINDOW_CYAN, 0.01)
    # Airborne traffic drone: a real 3D prop in the environment.
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.45, location=(4.6,5.8,7.0))
    drone = bpy.context.object
    drone.name = "Distant patrol drone"
    drone.scale = (1.6,0.7,0.42)
    drone.data.materials.append(MAT_PANEL)
    for dx in (-0.55,0.55):
        cylinder_between("Drone rotor", (4.6+dx,5.8,7.05),(4.6+dx,5.8,7.36),0.055,MAT_RAIL,10)
        cube("Drone status light", (4.6+dx,5.42,7.0), (0.12,0.04,0.09), MAT_WINDOW_PINK, 0.02)
    # Street service boxes and cable runs.
    for side in (-1,1):
        cube("Street power cabinet", (side*3.4,-0.1,0.85), (0.62,0.48,1.55), MAT_PANEL, 0.07)
        for j in range(4):
            cube("Cabinet vent", (side*3.4,-0.35,0.40+j*0.16), (0.36,0.025,0.035), MAT_RAIL, 0.006)
    # Lighting in real 3D space.
    def area(name, loc, target, color, power, size):
        data = bpy.data.lights.new(name, "AREA")
        data.energy = power
        data.shape = "DISK"
        data.size = size
        data.color = color
        obj = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(obj)
        obj.location = loc
        obj.rotation_euler = (Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
    area("Cyan storefront key", (-4.8,-2.8,6.5), (0,0,2.5), (0.08,0.68,1.0), 1100, 7.0)
    area("Magenta rim", (5.4,1.2,7.6), (0,0,3.1), (1.0,0.035,0.28), 1500, 6.0)
    area("Moon softbox", (0,4.0,13.0), (0,0,2.0), (0.28,0.44,1.0), 1900, 10.0)
    area("Warm low bounce", (-1.5,-6.0,2.0), (0,0,2.6), (1.0,0.24,0.08), 280, 4.0)

# ---------- 3D camera and lighting pipeline ----------
def make_camera():
    bpy.ops.object.camera_add(location=(5.7,-15.0,6.0))
    camera = bpy.context.object
    camera.name = "LINEFORGE anamorphic tracking camera"
    camera.data.lens = 42.0
    camera.data.sensor_width = 36.0
    camera.data.clip_start = 0.08
    camera.data.clip_end = 180.0
    bpy.context.scene.camera = camera
    keys = [
        (1,   (5.7,-15.0,6.0), (0.0,0.0,2.75)),
        (55,  (2.0,-12.3,5.1), (0.0,0.0,2.80)),
        (100, (0.3,-9.2,4.5), (0.0,0.0,3.15)),
        (137, (0.0,-6.7,4.35), (0.0,-0.05,4.05)),
        (160, (1.3,-8.8,5.4), (0.0,0.0,3.2)),
        (FRAME_COUNT, (2.8,-12.0,5.6), (0.0,0.0,2.9))
    ]
    for frame, loc, target in keys:
        camera.location = loc
        camera.rotation_euler = (Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
        camera.keyframe_insert(data_path="location", frame=frame)
        camera.keyframe_insert(data_path="rotation_euler", frame=frame)
    if camera.animation_data and camera.animation_data.action:
        for fc in camera.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
    return camera

# ---------- Original character: strokes only, no mesh or image cut-outs ----------
PIVOTS = {
    "head": (0.00,4.12), "hair": (0.00,4.12), "neck": (0.00,3.52),
    "torso": (0.00,2.72), "armNear": (0.57,3.15), "armFar": (-0.56,3.15),
    "legNear": (-0.22,1.55), "legFar": (0.22,1.55)
}

def smooth(a,b,x):
    u=max(0.0,min(1.0,(x-a)/(b-a)))
    return u*u*(3.0-2.0*u)

def pose_at(t):
    run_phase = t*TAU*1.65
    dash = smooth(1.85,2.7,t)
    impact = smooth(2.85,3.45,t) * (1.0-smooth(4.1,4.65,t))
    recover = smooth(4.15,5.0,t)
    bob = 0.07*math.sin(run_phase*2.0) if t < 2.7 else 0.035*math.sin(t*8.0)
    return {
        "root": (0.12+0.15*math.sin(t*2.0), -0.18-0.44*dash, bob+0.04+0.34*dash),
        "angles": {
            "head": -0.08 + 0.08*math.sin(t*2.6) + 0.05*impact,
            "hair": -0.10 + 0.10*math.sin(t*3.1+0.7),
            "neck": 0.0,
            "torso": -0.12 - 0.30*dash + 0.08*math.sin(run_phase),
            "armNear": -0.10 - 0.80*impact + 0.16*math.sin(run_phase+math.pi),
            "armFar": 0.18 + 0.28*math.sin(run_phase+math.pi),
            "legNear": 0.48*math.sin(run_phase+math.pi),
            "legFar": 0.48*math.sin(run_phase)
        },
        "depth": {"head":-0.03,"hair":-0.02,"neck":-0.04,"torso":0.0,
                  "armNear":-0.18-1.0*impact,"armFar":0.06,
                  "legNear":-0.02,"legFar":0.16},
        "scale": {"head":1.0,"hair":1.0,"neck":1.0,"torso":1.0,
                  "armNear":1.0+0.34*impact,"armFar":1.0,
                  "legNear":1.0,"legFar":1.0},
        "hair_sway": math.sin(t*4.5)*0.07 + 0.20*dash,
        "impact": impact,
        "dash": dash,
        "blink": 1.0 if 5.08 < t < 5.18 else 0.0,
        "recover": recover
    }

def catmull(points, subdivisions=3):
    if len(points) < 3:
        return points
    out=[]
    p=[points[0]]+list(points)+[points[-1]]
    for i in range(1,len(p)-2):
        p0,p1,p2,p3 = [Vector(v) for v in p[i-1:i+3]]
        for j in range(subdivisions):
            u=j/float(subdivisions)
            u2=u*u; u3=u2*u
            v=0.5*((2*p1)+(-p0+p2)*u+(2*p0-5*p1+4*p2-p3)*u2+(-p0+3*p1-3*p2+p3)*u3)
            out.append(tuple(v))
    out.append(tuple(points[-1]))
    return out

def transform_point(part, point, spec, pose, frame):
    x,z = point[0],point[1]
    depth = spec["depth"]
    px,pz = PIVOTS[part]
    scale = pose["scale"][part]
    angle = pose["angles"][part]
    if part == "hair":
        x += pose["hair_sway"] * (0.20 + max(0.0,z)*0.34)
    # Individual line points are redrawn at sub-pixel offsets each drawing frame.
    phase = frame*0.37 + spec.get("seed",0)*1.91
    wobble = spec["wobble"]*math.sin(phase + x*7.1 + z*9.7)
    x += wobble
    z += spec["wobble"]*0.55*math.cos(phase*0.87 + x*5.3)
    x *= scale
    z *= scale
    c,s = math.cos(angle), math.sin(angle)
    rx = x*c-z*s
    rz = x*s+z*c
    rootx,rooty,rootz = pose["root"]
    # Curved front surfaces establish actual depth around the face and torso.
    surface = 0.0
    if part in ("head","hair"):
        surface = -0.21*math.sqrt(max(0.0,1.0-min(1.0,(x/0.66)**2)))
    elif part == "torso":
        surface = -0.12*max(0.0,1.0-min(1.0,(x/0.95)**2))
    world = (rootx+px+rx, rooty+depth+pose["depth"][part]+surface, rootz+pz+rz)
    return world

def dynamic_fx(t):
    fx=[]
    impact = smooth(2.82,3.34,t)*(1.0-smooth(3.80,4.3,t))
    slash = smooth(4.65,5.05,t)*(1.0-smooth(5.8,6.0,t))
    dash = smooth(1.7,2.15,t)*(1.0-smooth(2.8,3.2,t))
    # Hand-inked action rays, perspective streaks, and impact debris.
    if dash > 0.02:
        for i in range(26):
            x=-4.8+(i%13)*0.78
            z=0.8+(i//13)*3.2 + 0.15*math.sin(i*2.3+t*8)
            fx.append({"pts":[(x,z),(x+0.28,z+0.12),(x+0.62,z+0.18)],
                       "weight":0.5+0.35*dash,"style":2 if i%4==0 else 1,"depth":-0.8,"wobble":0.002})
    if impact > 0.01:
        for i in range(30):
            a=TAU*i/30.0
            r=0.85+0.15*math.sin(i*3.1)
            x0=1.10+math.cos(a)*r
            z0=3.06+math.sin(a)*r
            x1=1.10+math.cos(a)*(r+0.45+0.4*impact)
            z1=3.06+math.sin(a)*(r+0.45+0.4*impact)
            fx.append({"pts":[(x0,z0),(x0+(x1-x0)*0.45+0.08,z0+(z1-z0)*0.45),(x1,z1)],
                       "weight":0.8+0.9*impact,"style":3 if i%5==0 else 0,"depth":-1.3,"wobble":0.004})
    if slash > 0.01:
        for i in range(8):
            start=-0.95+i*0.12
            fx.append({"pts":[(-2.6,2.0+start),(0.0,3.0+start*0.25),(2.8,4.15+start*0.55)],
                       "weight":1.5 if i<2 else 0.8,"style":3 if i<3 else 2,"depth":-1.8,"wobble":0.004})
        for i in range(18):
            x=-2.1+i*0.24
            fx.append({"pts":[(x,1.25+0.16*math.sin(i)),(x+0.16,1.52+0.16*math.sin(i+0.4))],
                       "weight":0.55,"style":3 if i%4==0 else 2,"depth":-1.5,"wobble":0.003})
    return fx

def rain_strokes(t):
    rain=[]
    for i in range(44):
        seed=i*17.17
        x=((i*1.37)%12.0)-6.0
        z=0.5+((i*2.29+t*(4.5+(i%7)*0.38))%9.0)
        y=-1.0+(i%5)*0.85
        drift=0.15+0.10*math.sin(t*2.0+i)
        rain.append({"pts":[(x,z),(x-drift,z-0.38),(x-drift*1.7,z-0.76)],
                     "weight":0.36,"style":2 if i%6==0 else 1,"depth":y,"wobble":0.001,"part":"world"})
    return rain

def create_grease_pencil():
    if bpy.app.version >= (5,0,0):
        gp_data = bpy.data.grease_pencils.new("LINEFORGE • frame-by-frame ink data")
    else:
        gp_data = bpy.data.grease_pencils_v3.new("LINEFORGE • frame-by-frame ink data")
    obj = bpy.data.objects.new("CHARACTER — 100% individual Grease Pencil strokes", gp_data)
    bpy.context.collection.objects.link(obj)
    palette = [
        ("Obsidian plum ink",(0.018,0.008,0.035,1.0)),
        ("Violet cross-hatch",(0.20,0.055,0.25,1.0)),
        ("Electric cyan rim",(0.18,0.82,1.0,1.0)),
        ("Impact vermilion",(1.0,0.055,0.22,1.0))
    ]
    for name,color in palette:
        material=bpy.data.materials.new(name)
        bpy.data.materials.create_gpencil_data(material)
        material.grease_pencil.show_stroke=True
        material.grease_pencil.show_fill=False
        material.grease_pencil.color=color
        material.diffuse_color=color
        gp_data.materials.append(material)
    layer=gp_data.layers.new("Frame-by-frame drawn lines", set_active=True)
    layer.use_lights=False
    layer.opacity=1.0
    layer.use_onion_skinning=True
    obj.show_in_front=False

    counts=[]
    for frame_number in range(1,FRAME_COUNT+1):
        t=(frame_number-1)/float(FPS)
        pose=pose_at(t)
        frame_lines=[]
        for i,spec in enumerate(STROKES):
            part=spec["part"]
            samples=catmull(spec["pts"],3)
            coords=[transform_point(part,p,spec | {"seed":i},pose,frame_number) for p in samples]
            frame_lines.append((coords,spec))
        # Additional moving FX and rain are also authored as individual lines.
        for i,spec in enumerate(dynamic_fx(t)+rain_strokes(t)):
            if spec.get("part")=="world":
                coords=[]
                for p in catmull(spec["pts"],2):
                    coords.append((p[0],spec["depth"],p[1]))
                frame_lines.append((coords,spec))
            else:
                coords=[]
                for p in catmull(spec["pts"],3):
                    coords.append((p[0],-1.25+spec["depth"],p[1]))
                frame_lines.append((coords,spec))
        sizes=[len(coords) for coords,spec in frame_lines if len(coords)>=2]
        gp_frame=layer.frames.new(frame_number)
        drawing=gp_frame.drawing
        drawing.add_strokes(sizes)
        stroke_index=0
        for coords,spec in frame_lines:
            if len(coords)<2:
                continue
            stroke=drawing.strokes[stroke_index]
            stroke_index+=1
            style=int(spec.get("style",0))
            stroke.material_index=max(0,min(3,style))
            stroke.cyclic=False
            base=float(spec.get("weight",1.0))*0.011
            count=len(coords)
            for j,(point,coord) in enumerate(zip(stroke.points,coords)):
                u=j/max(1,count-1)
                taper=(0.38+0.62*math.sin(math.pi*u)**0.42) if spec.get("taper",True) else 1.0
                point.position=coord
                point.radius=base*taper
                point.opacity=0.96 if style==0 else (0.64 if style==1 else (0.95 if style==2 else 0.90))
        counts.append({"frame":frame_number,"strokes":len(sizes)})
    return obj,counts

# ---------- Render setup ----------
def setup_scene(output_dir):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes,bpy.data.curves,bpy.data.materials,bpy.data.cameras,bpy.data.lights):
        for datablock in list(datablocks):
            if datablock.users==0:
                datablocks.remove(datablock)
    scene=bpy.context.scene
    scene.render.engine="BLENDER_EEVEE_NEXT"
    scene.eevee.taa_render_samples=48
    scene.render.resolution_x=WIDTH
    scene.render.resolution_y=HEIGHT
    scene.render.resolution_percentage=100
    scene.render.fps=FPS
    scene.render.image_settings.file_format="PNG"
    scene.render.image_settings.color_mode="RGBA"
    scene.render.image_settings.color_depth="8"
    scene.render.image_settings.compression=12
    scene.render.film_transparent=False
    scene.render.use_file_extension=True
    scene.render.filepath=os.path.join(output_dir,"frames","frame_")
    scene.frame_start=1
    scene.frame_end=FRAME_COUNT
    scene.world=bpy.data.worlds.new("Afterhour midnight atmosphere")
    scene.world.use_nodes=True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value=(0.003,0.006,0.022,1)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value=0.22
    scene.view_settings.view_transform="AgX"
    scene.view_settings.look="AgX - Medium High Contrast"
    scene.view_settings.exposure=0.0
    scene.view_settings.gamma=1.0
    scene.render.image_settings.color_mode="RGBA"
    scene.use_nodes=True
    tree=scene.node_tree
    tree.nodes.clear()
    render_layers=tree.nodes.new("CompositorNodeRLayers")
    glare=tree.nodes.new("CompositorNodeGlare")
    glare.glare_type="FOG_GLOW"
    glare.quality="HIGH"
    glare.threshold=1.25
    glare.size=7
    glare.mix=-0.88
    comp=tree.nodes.new("CompositorNodeComposite")
    tree.links.new(render_layers.outputs["Image"],glare.inputs["Image"])
    tree.links.new(glare.outputs["Image"],comp.inputs["Image"])
    create_environment()
    make_camera()
    gp_obj,stroke_counts=create_grease_pencil()
    os.makedirs(os.path.join(output_dir,"frames"),exist_ok=True)
    manifest={
        "engine":"Blender Grease Pencil v3, 3D world-space, frame-by-frame",
        "blender_version":bpy.app.version_string,
        "fps":FPS,"seconds":SECONDS,"frames":FRAME_COUNT,
        "resolution":[WIDTH,HEIGHT],
        "hand_authored_stroke_templates":len(STROKES),
        "character_mesh_objects":0,
        "character_image_planes":0,
        "character_svg_layers":0,
        "character_cutout_parts":0,
        "grease_pencil_object":gp_obj.name,
        "per_frame_drawings":len(stroke_counts),
        "per_frame_stroke_counts":stroke_counts,
        "palette":["obsidian plum ink","violet cross-hatch","electric cyan rim","impact vermilion"],
        "audio":"none"
    }
    with open(os.path.join(output_dir,"lineforge-manifest.json"),"w",encoding="utf-8") as f:
        json.dump(manifest,f,indent=2)
    blend_path=os.path.join(output_dir,"lineforge-handdrawn.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    scene.frame_set(1)
    print("LINEFORGE: rendering",FRAME_COUNT,"frames at",WIDTH,"x",HEIGHT,"/",FPS,"fps")
    bpy.ops.render.render(animation=True)
    print("LINEFORGE: render complete",output_dir)

def main():
    args=sys.argv
    if "--" in args:
        args=args[args.index("--")+1:]
    output_dir="out/lineforge"
    for i,arg in enumerate(args):
        if arg=="--output-dir" and i+1<len(args):
            output_dir=args[i+1]
    output_dir=os.path.abspath(output_dir)
    os.makedirs(output_dir,exist_ok=True)
    setup_scene(output_dir)

if __name__=="__main__":
    main()
