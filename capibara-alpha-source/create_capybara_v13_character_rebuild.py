import bpy
import math
import os
import sys
from mathutils import Vector

VERSION = "13.0.0-character-rebuild"
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT_DIR = os.path.abspath(ARGS[0] if ARGS else "preview-output")
os.makedirs(OUT_DIR, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 768
scene.render.resolution_y = 768
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.film_transparent = False
scene.view_settings.look = "AgX - Medium High Contrast"

model = bpy.data.collections.new("CAPIBARA_V13_CHARACTER")
studio = bpy.data.collections.new("STUDIO")
scene.collection.children.link(model)
scene.collection.children.link(studio)


def link_only(obj, collection=model):
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def material(name, color, roughness=0.7, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def fur_material(name, dark, light):
    mat = material(name, dark, 0.72)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    tex = nodes.new("ShaderNodeTexCoord")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 9.0
    noise.inputs["Detail"].default_value = 3.2
    noise.inputs["Roughness"].default_value = 0.62
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.28
    ramp.color_ramp.elements[0].color = dark
    ramp.color_ramp.elements[1].position = 0.72
    ramp.color_ramp.elements[1].color = light
    links.new(tex.outputs["Generated"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

    fine = nodes.new("ShaderNodeTexNoise")
    fine.inputs["Scale"].default_value = 115.0
    fine.inputs["Detail"].default_value = 2.5
    fine.inputs["Roughness"].default_value = 0.58
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.09
    bump.inputs["Distance"].default_value = 0.012
    links.new(tex.outputs["Generated"], fine.inputs["Vector"])
    links.new(fine.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    if "Sheen Weight" in bsdf.inputs:
        bsdf.inputs["Sheen Weight"].default_value = 0.12
    return mat


MAT_FUR = fur_material("Warm golden capybara fur", (0.12, 0.040, 0.010, 1), (0.37, 0.155, 0.050, 1))
MAT_MUZZLE = fur_material("Soft muzzle fur", (0.19, 0.070, 0.020, 1), (0.43, 0.205, 0.080, 1))
MAT_DARK_FUR = fur_material("Dark paw fur", (0.055, 0.014, 0.004, 1), (0.14, 0.042, 0.012, 1))
MAT_EYE = material("Deep glossy eyes", (0.012, 0.006, 0.003, 1), 0.10)
MAT_HIGHLIGHT = material("Eye catchlight", (1.0, 0.98, 0.92, 1), 0.05)
MAT_NOSE = material("Soft brown nose", (0.105, 0.034, 0.018, 1), 0.34)
MAT_NOSTRIL = material("Nostrils", (0.022, 0.006, 0.003, 1), 0.62)
MAT_MOUTH = material("Mouth interior", (0.055, 0.008, 0.006, 1), 0.78)
MAT_TONGUE = material("Tongue", (0.45, 0.075, 0.085, 1), 0.58)
MAT_TOOTH = material("Warm incisors", (0.86, 0.73, 0.50, 1), 0.58)
MAT_HAT = material("Explorer olive", (0.20, 0.22, 0.075, 1), 0.88)
MAT_HAT_LIGHT = material("Explorer olive highlight", (0.34, 0.35, 0.13, 1), 0.86)
MAT_LEATHER = material("Dark leather", (0.16, 0.050, 0.014, 1), 0.72)
MAT_LEATHER_LIGHT = material("Camera leather", (0.37, 0.13, 0.035, 1), 0.62)
MAT_METAL = material("Camera metal", (0.38, 0.38, 0.34, 1), 0.26, 0.62)
MAT_GLASS = material("Camera glass", (0.035, 0.18, 0.26, 1), 0.10, 0.20)
MAT_BACKDROP = material("Backdrop", (0.10, 0.12, 0.095, 1), 0.96)
MAT_FLOOR = material("Floor", (0.13, 0.16, 0.115, 1), 0.98)


def finish_mesh(obj, mat, subdiv=1):
    link_only(obj)
    obj.data.materials.append(mat)
    for p in obj.data.polygons:
        p.use_smooth = True
    if subdiv:
        mod = obj.modifiers.new("Subdivision", "SUBSURF")
        mod.levels = subdiv
        mod.render_levels = subdiv
    return obj


def uv(name, loc, scale, mat, seg=48, rings=32, rot=(0, 0, 0), subdiv=1):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish_mesh(obj, mat, subdiv)


def cube(name, loc, scale, mat, bevel=0.06, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link_only(obj)
    obj.data.materials.append(mat)
    mod = obj.modifiers.new("Rounded", "BEVEL")
    mod.width = bevel
    mod.segments = 5
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def cylinder(name, loc, radius, depth, mat, vertices=64, rot=(0, 0, 0), scale=(1, 1, 1), bevel=0.03):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link_only(obj)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Rounded", "BEVEL")
        mod.width = bevel
        mod.segments = 4
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def torus(name, loc, major, minor, mat, rot=(0, 0, 0), scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=64,
                                    minor_segments=20, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish_mesh(obj, mat, 1)


def loft_z(name, sections, segments, mat):
    verts, faces = [], []
    for z, cy, rx, ry in sections:
        for i in range(segments):
            a = 2.0 * math.pi * i / segments
            verts.append((rx * math.cos(a), cy + ry * math.sin(a), z))
    for r in range(len(sections) - 1):
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
        a = (len(sections) - 1) * segments + i
        b = (len(sections) - 1) * segments + n
        faces.append((top, a, b))
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return finish_mesh(bpy.data.objects.new(name, mesh), mat, 2)


def loft_y(name, sections, segments, mat):
    verts, faces = [], []
    for y, cz, rx, rz in sections:
        for i in range(segments):
            a = 2.0 * math.pi * i / segments
            c = math.cos(a)
            s = math.sin(a)
            px = math.copysign(abs(c) ** 0.88, c)
            pz = math.copysign(abs(s) ** 0.92, s)
            verts.append((rx * px, y, cz + rz * pz))
    for r in range(len(sections) - 1):
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
        a = (len(sections) - 1) * segments + i
        b = (len(sections) - 1) * segments + n
        faces.append((front, b, a))
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return finish_mesh(bpy.data.objects.new(name, mesh), mat, 2)


def curve_limb(name, points, radius, mat):
    curve = bpy.data.curves.new(name + "Curve", "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 5
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
# Character surfaces
# -----------------------------------------------------------------------------
body_sections = [
    (0.23, 0.04, 0.34, 0.36),
    (0.38, 0.02, 0.58, 0.50),
    (0.68, 0.02, 0.82, 0.63),
    (1.02, 0.00, 0.94, 0.70),
    (1.38, -0.01, 0.98, 0.73),
    (1.72, 0.00, 0.94, 0.71),
    (2.02, 0.03, 0.86, 0.65),
    (2.28, 0.06, 0.76, 0.58),
    (2.50, 0.08, 0.66, 0.50),
    (2.67, 0.09, 0.55, 0.42),
]
body = loft_z("Body_Pear", body_sections, 52, MAT_FUR)

head_sections = [
    (0.55, 3.28, 0.34, 0.28),
    (0.40, 3.30, 0.70, 0.53),
    (0.20, 3.31, 0.94, 0.68),
    (0.00, 3.31, 1.03, 0.75),
    (-0.20, 3.28, 1.04, 0.75),
    (-0.40, 3.22, 1.00, 0.70),
    (-0.58, 3.14, 0.92, 0.61),
    (-0.72, 3.06, 0.82, 0.50),
    (-0.83, 3.00, 0.68, 0.39),
    (-0.90, 2.98, 0.48, 0.27),
]
head = loft_y("Head_Authored", head_sections, 56, MAT_FUR)

# Head overlaps shoulders deeply, hiding the seam from all hero views.
uv("Neck_Fill", (0, 0.10, 2.72), (0.72, 0.55, 0.42), MAT_FUR, 48, 30)

# Integrated-looking muzzle made from overlapping soft masses.
uv("Muzzle_Center", (0, -0.91, 2.98), (0.52, 0.23, 0.30), MAT_MUZZLE, 56, 34)
uv("Muzzle_L", (-0.28, -0.86, 2.90), (0.37, 0.22, 0.28), MAT_MUZZLE, 48, 30)
uv("Muzzle_R", (0.28, -0.86, 2.90), (0.37, 0.22, 0.28), MAT_MUZZLE, 48, 30)

# Eyes are glossy and partially buried in the head; eyelids hug their top edge.
for side, sx in (("L", -1), ("R", 1)):
    x = 0.50 * sx
    uv(f"Eye_{side}", (x, -0.70, 3.32), (0.155, 0.095, 0.205), MAT_EYE, 56, 34)
    uv(f"Eye_Highlight_{side}", (x - 0.035 * sx, -0.792, 3.395), (0.034, 0.008, 0.043), MAT_HIGHLIGHT, 28, 18)
    uv(f"Eye_Highlight_Small_{side}", (x + 0.037 * sx, -0.795, 3.270), (0.010, 0.004, 0.013), MAT_HIGHLIGHT, 20, 14)
    uv(f"Upper_Lid_{side}", (x, -0.725, 3.465), (0.175, 0.075, 0.075), MAT_FUR, 44, 28,
       rot=(math.radians(-3), 0, math.radians(-3 * sx)))

# Nose, recessed smile, tongue and incisors.
uv("Nose", (0, -1.145, 3.02), (0.245, 0.075, 0.125), MAT_NOSE, 52, 32)
for side, sx in (("L", -1), ("R", 1)):
    uv(f"Nostril_{side}", (0.090 * sx, -1.217, 3.035), (0.037, 0.010, 0.022), MAT_NOSTRIL, 24, 16)
uv("Mouth_Interior", (0, -1.105, 2.72), (0.285, 0.025, 0.165), MAT_MOUTH, 48, 30)
uv("Tongue", (0, -1.130, 2.645), (0.080, 0.012, 0.030), MAT_TONGUE, 30, 18)
for side, sx in (("L", -1), ("R", 1)):
    cube(f"Incisor_{side}", (0.052 * sx, -1.128, 2.825), (0.037, 0.014, 0.058), MAT_TOOTH, 0.018,
         rot=(math.radians(-2), 0, math.radians(2 * sx)))

# Small round ears.
for side, sx in (("L", -1), ("R", 1)):
    uv(f"Ear_{side}", (0.78 * sx, 0.02, 3.83), (0.16, 0.09, 0.16), MAT_DARK_FUR, 40, 26,
       rot=(math.radians(5), math.radians(8 * sx), math.radians(-8 * sx)))
    uv(f"Ear_Inner_{side}", (0.785 * sx, -0.065, 3.83), (0.075, 0.012, 0.075), MAT_MUZZLE, 30, 18)

# Relaxed hero pose.
curve_limb("Arm_Wave", [(-0.62, 0.00, 2.20), (-0.82, -0.18, 2.47), (-0.96, -0.36, 2.73)], 0.205, MAT_FUR)
uv("Wave_Palm", (-1.00, -0.43, 2.86), (0.235, 0.175, 0.235), MAT_FUR, 44, 28)
for i, x in enumerate((-1.135, -1.045, -0.955, -0.865)):
    uv(f"Wave_Finger_{i}", (x, -0.49, 3.040 + (0.018 if i in (1, 2) else 0.0)),
       (0.046, 0.040, 0.125), MAT_FUR, 28, 18,
       rot=(math.radians(-8), math.radians(-5), math.radians((i - 1.5) * 7)))
uv("Wave_Thumb", (-0.82, -0.47, 2.82), (0.060, 0.048, 0.110), MAT_FUR, 28, 18,
   rot=(math.radians(-12), math.radians(-8), math.radians(55)))

curve_limb("Arm_Rest", [(0.66, 0.00, 2.16), (0.77, -0.11, 1.80), (0.70, -0.25, 1.48)], 0.205, MAT_FUR)
uv("Rest_Palm", (0.69, -0.28, 1.38), (0.19, 0.15, 0.19), MAT_FUR, 40, 26)

for side, sx in (("L", -1), ("R", 1)):
    uv(f"Foot_{side}", (0.38 * sx, -0.18, 0.27), (0.285, 0.34, 0.18), MAT_DARK_FUR, 48, 30)
    for toe in range(4):
        tx = 0.38 * sx + (toe - 1.5) * 0.060
        uv(f"Toe_{side}_{toe}", (tx, -0.515, 0.275), (0.027, 0.010, 0.020), MAT_NOSTRIL, 20, 14)

# -----------------------------------------------------------------------------
# Explorer accessories
# -----------------------------------------------------------------------------
cylinder("Hat_Brim", (0, 0.00, 4.00), 0.92, 0.075, MAT_HAT, 72,
         rot=(math.radians(3), math.radians(-5), math.radians(-2)), scale=(1.05, 0.83, 1), bevel=0.04)
hat_sections = [
    (4.03, 0.02, 0.64, 0.48),
    (4.17, 0.04, 0.62, 0.46),
    (4.34, 0.06, 0.54, 0.40),
    (4.43, 0.07, 0.40, 0.30),
]
loft_z("Hat_Crown", hat_sections, 48, MAT_HAT_LIGHT)
torus("Hat_Band", (0, 0.01, 4.10), 0.62, 0.035, MAT_LEATHER, scale=(1.02, 0.82, 0.72))

cube("Backpack", (0, 0.66, 1.56), (0.48, 0.18, 0.60), MAT_HAT, 0.13,
     rot=(math.radians(-4), 0, 0))
cube("Backpack_Pocket", (0, 0.86, 1.40), (0.34, 0.07, 0.22), MAT_HAT_LIGHT, 0.07)
for side, sx in (("L", -1), ("R", 1)):
    torus(f"Pack_Strap_{side}", (0.43 * sx, -0.01, 1.98), 0.55, 0.030, MAT_LEATHER,
          rot=(math.radians(90), 0, 0), scale=(0.36, 0.90, 1.0))

cube("Camera_Body", (0, -0.76, 1.54), (0.31, 0.12, 0.22), MAT_LEATHER_LIGHT, 0.055)
cube("Camera_Top", (0, -0.775, 1.72), (0.26, 0.10, 0.055), MAT_METAL, 0.025)
uv("Camera_Button", (-0.16, -0.88, 1.78), (0.035, 0.020, 0.022), MAT_METAL, 24, 16)
cylinder("Camera_Lens", (0, -0.93, 1.54), 0.145, 0.16, MAT_METAL, 48,
         rot=(math.radians(90), 0, 0), bevel=0.025)
cylinder("Camera_Glass", (0, -1.025, 1.54), 0.095, 0.028, MAT_GLASS, 48,
         rot=(math.radians(90), 0, 0), bevel=0.015)
torus("Camera_Strap", (0, -0.04, 2.12), 0.72, 0.023, MAT_LEATHER,
      rot=(math.radians(90), 0, 0), scale=(0.70, 1.0, 1.0))

# -----------------------------------------------------------------------------
# Studio
# -----------------------------------------------------------------------------
cylinder("Platform", (0, 0, 0.02), 2.9, 0.20, MAT_FLOOR, 96, bevel=0.09)
platform = bpy.context.object
link_only(platform, studio)
cube("Backdrop", (0, 2.85, 2.65), (4.6, 0.14, 3.35), MAT_BACKDROP, 0.50)
backdrop = bpy.context.object
link_only(backdrop, studio)

world = bpy.data.worlds.new("Capibara World")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.030, 0.038, 0.027, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.42


def area(name, loc, energy, size, color):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    studio.objects.link(obj)
    obj.location = loc
    return obj

area("Key", (-3.5, -4.4, 6.3), 1200, 4.4, (1.0, 0.75, 0.52))
area("Fill", (3.5, -2.3, 4.8), 650, 4.8, (0.60, 0.78, 1.0))
area("Rim", (0, 2.3, 5.8), 1000, 3.4, (0.72, 1.0, 0.76))

cam_data = bpy.data.cameras.new("Camera")
cam = bpy.data.objects.new("Camera", cam_data)
studio.objects.link(cam)
scene.camera = cam


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def render(name, location, target, lens=66):
    cam.location = location
    cam.data.lens = lens
    look_at(cam, target)
    scene.render.filepath = os.path.join(OUT_DIR, name)
    bpy.ops.render.render(write_still=True)

blend_path = os.path.join(OUT_DIR, "capibara_v13_character_rebuild.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
render("capibara_v13_front.png", (0, -7.75, 3.10), (0, -0.10, 2.20), 67)
render("capibara_v13_profile.png", (7.7, -0.10, 3.10), (0, 0.00, 2.20), 67)
render("capibara_v13_three_quarter.png", (4.85, -6.45, 3.18), (0, -0.15, 2.22), 68)
print("CAPIBARA_V13_CHARACTER_REBUILD_OK", blend_path)
