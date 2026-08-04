import bpy
import math
import os
import sys
from mathutils import Vector

VERSION = "4.0.0-clean-surface"
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT_DIR = os.path.abspath(ARGS[0] if ARGS else "preview-output")
os.makedirs(OUT_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# Scene
# -----------------------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.resolution_x = 768
scene.render.resolution_y = 768
scene.render.image_settings.color_mode = "RGBA"
scene.view_settings.look = "AgX - Medium High Contrast"

model = bpy.data.collections.new("CAPIBARA_V4_CLEAN_SURFACE")
studio = bpy.data.collections.new("STUDIO")
scene.collection.children.link(model)
scene.collection.children.link(studio)


def link_only(obj, collection=model):
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def material(name, color, roughness=0.72, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


MAT_FUR = material("Fur warm brown", (0.36, 0.145, 0.050, 1), 0.88)
MAT_FUR_LIGHT = material("Muzzle warm tan", (0.50, 0.245, 0.095, 1), 0.90)
MAT_FUR_DARK = material("Paws dark brown", (0.19, 0.070, 0.025, 1), 0.92)
MAT_EYE = material("Eyes", (0.010, 0.007, 0.005, 1), 0.13)
MAT_WHITE = material("Eye highlights", (1.0, 0.96, 0.86, 1), 0.14)
MAT_NOSE = material("Nose", (0.075, 0.028, 0.018, 1), 0.55)
MAT_MOUTH = material("Mouth", (0.055, 0.012, 0.010, 1), 0.82)
MAT_TONGUE = material("Tongue", (0.58, 0.14, 0.16, 1), 0.66)
MAT_TOOTH = material("Teeth", (0.93, 0.82, 0.59, 1), 0.72)
MAT_HAT = material("Explorer olive", (0.25, 0.26, 0.10, 1), 0.86)
MAT_HAT_LIGHT = material("Explorer olive light", (0.39, 0.39, 0.16, 1), 0.84)
MAT_LEATHER = material("Leather", (0.20, 0.075, 0.024, 1), 0.82)
MAT_LEATHER_LIGHT = material("Camera leather", (0.36, 0.14, 0.045, 1), 0.78)
MAT_METAL = material("Camera metal", (0.32, 0.32, 0.29, 1), 0.32, 0.45)
MAT_GLASS = material("Camera glass", (0.08, 0.29, 0.42, 1), 0.12, 0.12)
MAT_BACK = material("Backdrop", (0.095, 0.115, 0.095, 1), 0.96)
MAT_FLOOR = material("Floor", (0.12, 0.15, 0.11, 1), 0.98)


def finish_mesh(obj, mat, subdiv=2):
    link_only(obj)
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    if subdiv:
        mod = obj.modifiers.new("Subdivision", "SUBSURF")
        mod.levels = subdiv
        mod.render_levels = subdiv
        mod.subdivision_type = "CATMULL_CLARK"
    return obj


def loft_z(name, sections, segments, mat, subdiv=2):
    """Continuous closed surface built from horizontal elliptical rings.
    section = (z, center_y, radius_x, radius_y)
    """
    verts = []
    faces = []
    for z, cy, rx, ry in sections:
        for i in range(segments):
            a = 2.0 * math.pi * i / segments
            verts.append((rx * math.cos(a), cy + ry * math.sin(a), z))
    rings = len(sections)
    for r in range(rings - 1):
        for i in range(segments):
            n = (i + 1) % segments
            a = r * segments + i
            b = r * segments + n
            c = (r + 1) * segments + n
            d = (r + 1) * segments + i
            faces.append((a, b, c, d))
    bottom = len(verts)
    verts.append((0, sections[0][1], sections[0][0]))
    top = len(verts)
    verts.append((0, sections[-1][1], sections[-1][0]))
    for i in range(segments):
        n = (i + 1) % segments
        faces.append((bottom, n, i))
        a = (rings - 1) * segments + i
        b = (rings - 1) * segments + n
        faces.append((top, a, b))
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    return finish_mesh(obj, mat, subdiv)


def loft_y(name, sections, segments, mat, subdiv=2):
    """Continuous closed surface built from vertical elliptical rings.
    section = (y, center_z, radius_x, radius_z), ordered back to front.
    """
    verts = []
    faces = []
    for y, cz, rx, rz in sections:
        for i in range(segments):
            a = 2.0 * math.pi * i / segments
            verts.append((rx * math.cos(a), y, cz + rz * math.sin(a)))
    rings = len(sections)
    for r in range(rings - 1):
        for i in range(segments):
            n = (i + 1) % segments
            a = r * segments + i
            b = (r + 1) * segments + i
            c = (r + 1) * segments + n
            d = r * segments + n
            faces.append((a, b, c, d))
    back = len(verts)
    verts.append((0, sections[0][0], sections[0][1]))
    front = len(verts)
    verts.append((0, sections[-1][0], sections[-1][1]))
    for i in range(segments):
        n = (i + 1) % segments
        faces.append((back, i, n))
        a = (rings - 1) * segments + i
        b = (rings - 1) * segments + n
        faces.append((front, b, a))
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    return finish_mesh(obj, mat, subdiv)


def uv(name, loc, scale, mat, seg=48, rings=32, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish_mesh(obj, mat, 1)


def cube(name, loc, scale, mat, bevel=0.08, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link_only(obj)
    obj.data.materials.append(mat)
    mod = obj.modifiers.new("Soft bevel", "BEVEL")
    mod.width = bevel
    mod.segments = 4
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def cylinder(name, loc, radius, depth, mat, vertices=64, rot=(0, 0, 0), scale=(1, 1, 1), bevel=0.035):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link_only(obj)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Soft bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 4
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def torus(name, loc, major, minor, mat, rot=(0, 0, 0), scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=64,
                                    minor_segments=16, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish_mesh(obj, mat, 1)


def curve_limb(name, points, radius, mat):
    curve = bpy.data.curves.new(name + "Curve", "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 4
    curve.bevel_depth = radius
    curve.bevel_resolution = 5
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for bp, co in zip(spline.bezier_points, points):
        bp.co = co
        bp.handle_left_type = "AUTO"
        bp.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    model.objects.link(obj)
    obj.data.materials.append(mat)
    return obj

# -----------------------------------------------------------------------------
# Clean continuous body and head
# -----------------------------------------------------------------------------
body_sections = [
    (0.24, 0.02, 0.36, 0.38),
    (0.38, 0.00, 0.64, 0.55),
    (0.72, 0.02, 0.88, 0.67),
    (1.15, 0.02, 1.00, 0.73),
    (1.55, -0.02, 1.02, 0.74),
    (1.92, -0.03, 0.93, 0.68),
    (2.25, 0.00, 0.82, 0.61),
    (2.50, 0.03, 0.73, 0.56),
    (2.72, 0.05, 0.62, 0.49),
]
body = loft_z("Body_Clean", body_sections, 48, MAT_FUR, 2)

head_sections = [
    (0.70, 3.43, 0.30, 0.30),
    (0.56, 3.46, 0.70, 0.56),
    (0.30, 3.47, 0.98, 0.72),
    (0.00, 3.45, 1.08, 0.78),
    (-0.28, 3.39, 1.02, 0.72),
    (-0.50, 3.31, 0.91, 0.61),
    (-0.68, 3.23, 0.80, 0.49),
    (-0.83, 3.15, 0.67, 0.36),
    (-0.96, 3.10, 0.52, 0.27),
    (-1.05, 3.10, 0.24, 0.14),
]
head = loft_y("Head_Clean", head_sections, 56, MAT_FUR, 2)

# Subtle integrated muzzle tone.
uv("Muzzle_Tone", (0, -1.045, 3.10), (0.50, 0.018, 0.205), MAT_FUR_LIGHT, 56, 32)

# Small ears partly hidden by the hat.
for side, sx in (("L", -1), ("R", 1)):
    uv(f"Ear_{side}", (0.78 * sx, 0.02, 3.91), (0.18, 0.10, 0.18), MAT_FUR_DARK, 40, 26,
       rot=(math.radians(6), math.radians(8 * sx), math.radians(-8 * sx)))
    uv(f"EarInner_{side}", (0.785 * sx, -0.078, 3.91), (0.095, 0.018, 0.095), MAT_FUR_LIGHT, 32, 20)

# Eyes: large enough for appeal, small enough to preserve capybara identity.
for side, sx in (("L", -1), ("R", 1)):
    x = 0.47 * sx
    uv(f"Eye_{side}", (x, -0.765, 3.52), (0.18, 0.105, 0.215), MAT_EYE, 56, 34)
    uv(f"EyeHighlight_{side}", (x - 0.045 * sx, -0.872, 3.595), (0.043, 0.010, 0.052), MAT_WHITE, 28, 18)
    uv(f"EyeHighlightSmall_{side}", (x + 0.047 * sx, -0.875, 3.465), (0.016, 0.007, 0.019), MAT_WHITE, 20, 14)

# Nose, open smile and small incisors.
uv("Nose", (0, -1.115, 3.19), (0.30, 0.075, 0.145), MAT_NOSE, 52, 32)
for side, sx in (("L", -1), ("R", 1)):
    uv(f"Nostril_{side}", (0.108 * sx, -1.189, 3.205), (0.042, 0.010, 0.024), MAT_MOUTH, 26, 16)
uv("Mouth", (0, -1.085, 2.98), (0.215, 0.020, 0.118), MAT_MOUTH, 48, 30)
uv("Tongue", (0, -1.110, 2.945), (0.12, 0.012, 0.045), MAT_TONGUE, 32, 20)
for side, sx in (("L", -1), ("R", 1)):
    cube(f"Tooth_{side}", (0.065 * sx, -1.108, 3.04), (0.050, 0.018, 0.073), MAT_TOOTH, 0.025,
         rot=(math.radians(-2), 0, math.radians(2 * sx)))

# -----------------------------------------------------------------------------
# Relaxed asymmetrical explorer pose
# -----------------------------------------------------------------------------
curve_limb("Arm_Wave", [(-0.64, -0.02, 2.26), (-0.82, -0.13, 2.48), (-0.94, -0.22, 2.76)], 0.22, MAT_FUR)
uv("Wave_Hand", (-0.98, -0.25, 2.93), (0.24, 0.16, 0.24), MAT_FUR_DARK, 44, 28,
   rot=(math.radians(-8), math.radians(-8), math.radians(-8)))
for i, x in enumerate((-1.13, -0.99, -0.85)):
    uv(f"Wave_Finger_{i}", (x, -0.28, 3.14), (0.061, 0.050, 0.16), MAT_FUR_DARK, 30, 18,
       rot=(math.radians(-7), math.radians(-4), math.radians((i - 1) * 8)))
curve_limb("Arm_Rest", [(0.68, -0.01, 2.22), (0.79, -0.10, 1.90), (0.73, -0.23, 1.62)], 0.22, MAT_FUR)
uv("Rest_Hand", (0.72, -0.25, 1.52), (0.23, 0.17, 0.23), MAT_FUR_DARK, 40, 26)

# Compact feet.
for side, sx in (("L", -1), ("R", 1)):
    uv(f"Foot_{side}", (0.38 * sx, -0.19, 0.28), (0.31, 0.40, 0.20), MAT_FUR_DARK, 48, 30)
    for toe in range(3):
        tx = 0.38 * sx + (toe - 1) * 0.075
        uv(f"Toe_{side}_{toe}", (tx, -0.575, 0.28), (0.036, 0.013, 0.025), MAT_NOSE, 22, 14)

# -----------------------------------------------------------------------------
# Explorer accessories
# -----------------------------------------------------------------------------
cylinder("Hat_Brim", (0, 0.00, 4.08), 0.96, 0.085, MAT_HAT, 72, scale=(1.06, 0.84, 1), bevel=0.045)
loft_z("Hat_Crown", [
    (4.10, 0.02, 0.70, 0.54),
    (4.24, 0.04, 0.68, 0.52),
    (4.42, 0.06, 0.58, 0.44),
    (4.51, 0.07, 0.43, 0.34),
], 48, MAT_HAT_LIGHT, 2)
torus("Hat_Band", (0, 0.01, 4.18), 0.65, 0.035, MAT_LEATHER, scale=(1.03, 0.83, 0.72))

cube("Backpack", (0, 0.64, 1.72), (0.52, 0.18, 0.60), MAT_HAT, 0.15,
     rot=(math.radians(-3), 0, 0))
cube("Backpack_Pocket", (0, 0.84, 1.57), (0.35, 0.07, 0.23), MAT_HAT_LIGHT, 0.075)
for side, sx in (("L", -1), ("R", 1)):
    torus(f"Backpack_Strap_{side}", (0.43 * sx, -0.01, 2.05), 0.54, 0.035, MAT_LEATHER,
          rot=(math.radians(90), 0, 0), scale=(0.35, 0.88, 1.0))

cube("Camera_Body", (0, -0.73, 1.72), (0.29, 0.11, 0.21), MAT_LEATHER_LIGHT, 0.055)
cylinder("Camera_Lens", (0, -0.89, 1.72), 0.145, 0.16, MAT_METAL, 48,
         rot=(math.radians(90), 0, 0), bevel=0.028)
cylinder("Camera_Glass", (0, -0.985, 1.72), 0.095, 0.028, MAT_GLASS, 48,
         rot=(math.radians(90), 0, 0), bevel=0.014)
torus("Camera_Strap", (0, -0.04, 2.24), 0.72, 0.022, MAT_LEATHER,
      rot=(math.radians(90), 0, 0), scale=(0.70, 1.0, 1.0))

for obj in model.all_objects:
    obj["capibara_version"] = VERSION
    obj["art_direction"] = "cute_capibara_explorer_clean_surface"

# -----------------------------------------------------------------------------
# Studio
# -----------------------------------------------------------------------------
cylinder("Platform", (0, 0, 0.01), 2.8, 0.18, MAT_FLOOR, 96, bevel=0.08)
platform = bpy.context.object
link_only(platform, studio)
cube("Backdrop", (0, 2.75, 2.55), (4.4, 0.12, 3.2), MAT_BACK, 0.45)
backdrop = bpy.context.object
link_only(backdrop, studio)

world = scene.world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.028, 0.036, 0.026, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.45


def add_area(name, loc, energy, size, color):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    studio.objects.link(obj)
    obj.location = loc
    return obj


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()

key = add_area("Key", (-3.5, -4.2, 6.2), 1050, 4.4, (1.0, 0.76, 0.52)); aim(key, (0, 0, 2.3))
fill = add_area("Fill", (3.5, -2.0, 4.8), 600, 4.5, (0.66, 0.80, 1.0)); aim(fill, (0, 0, 2.4))
rim = add_area("Rim", (0, 2.2, 5.8), 900, 3.2, (0.72, 1.0, 0.74)); aim(rim, (0, 0, 2.5))

cam_data = bpy.data.cameras.new("Camera")
cam = bpy.data.objects.new("Camera", cam_data)
studio.objects.link(cam)
scene.camera = cam


def render(name, location, target, lens=62):
    cam.location = location
    cam.data.lens = lens
    aim(cam, target)
    scene.render.filepath = os.path.join(OUT_DIR, name)
    bpy.ops.render.render(write_still=True)

blend = os.path.join(OUT_DIR, "capibara_v4_clean_surface.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend)
render("capibara_v4_front.png", (0, -8.7, 3.05), (0, -0.08, 2.20), 64)
render("capibara_v4_profile.png", (8.3, -0.10, 3.10), (0, -0.05, 2.20), 64)
render("capibara_v4_three_quarter.png", (5.6, -7.8, 3.42), (0, -0.06, 2.23), 61)
print("CAPIBARA_V4_CLEAN_SURFACE_OK", blend)
