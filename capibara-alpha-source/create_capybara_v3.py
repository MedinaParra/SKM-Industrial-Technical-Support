import bpy
import math
import os
import sys
import json
from mathutils import Vector

# -----------------------------------------------------------------------------
# Capibara V3 — Art Rebuild
# Objetivo: semejanza visual con el capibara explorador tierno de referencia.
# Esta versión prioriza silueta, rostro y materiales; el rig final se rehace
# después de aprobar estas vistas reales de Blender.
# -----------------------------------------------------------------------------

VERSION = "3.0.0-art-rebuild"
ART_STAGES = [
    "A_blockout_silueta",
    "B_rostro_tierno",
    "C_extremidades_postura",
    "D_materiales_pelaje_base",
]


def parse_args():
    args = sys.argv
    if "--" in args:
        args = args[args.index("--") + 1:]
    out_dir = os.path.abspath(args[0]) if args else os.path.abspath("output")
    project_dir = os.path.abspath(args[1]) if len(args) > 1 else os.getcwd()
    return out_dir, project_dir


OUT_DIR, PROJECT_DIR = parse_args()
ASSET_DIR = os.path.join(PROJECT_DIR, "assets")
DATA_DIR = os.path.join(PROJECT_DIR, "data")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(ASSET_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Scene reset.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.image_settings.color_depth = "8"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.render.film_transparent = False
scene.world.color = (0.035, 0.035, 0.035)
scene.frame_start = 1
scene.frame_end = 120
scene.render.fps = 30

# Collections.
MODEL = bpy.data.collections.new("CAPIBARA_BETA_LOD0")
STUDIO = bpy.data.collections.new("STUDIO")
scene.collection.children.link(MODEL)
scene.collection.children.link(STUDIO)


def srgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)) + (1.0,)


def smooth(obj):
    if getattr(obj, "data", None) and hasattr(obj.data, "polygons"):
        for p in obj.data.polygons:
            p.use_smooth = True


def move_to_collection(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)


def mat_principled(name, base, roughness=0.65, metallic=0.0, specular=0.30,
                   subsurface=0.0, procedural_fur=False):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = base
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = specular
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = subsurface
    if procedural_fur:
        tex = nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = 7.0
        tex.inputs["Detail"].default_value = 4.0
        tex.inputs["Roughness"].default_value = 0.60
        tex.inputs["Distortion"].default_value = 0.08
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.20
        ramp.color_ramp.elements[0].color = srgb("#7A4325")
        ramp.color_ramp.elements[1].position = 0.82
        ramp.color_ramp.elements[1].color = srgb("#C98245")
        nt.links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
        bump_tex = nt.nodes.new("ShaderNodeTexNoise")
        bump_tex.inputs["Scale"].default_value = 54.0
        bump_tex.inputs["Detail"].default_value = 2.2
        bump_tex.inputs["Roughness"].default_value = 0.55
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.16
        bump.inputs["Distance"].default_value = 0.025
        nt.links.new(bump_tex.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


MAT_FUR = mat_principled("Fur_Warm_Stylized", srgb("#A96332"), 0.72, specular=0.23,
                         subsurface=0.018, procedural_fur=True)
MAT_FUR_LIGHT = mat_principled("Muzzle_Warm", srgb("#B97849"), 0.76, specular=0.20,
                               subsurface=0.025)
MAT_FUR_DARK = mat_principled("Fur_Dark", srgb("#5B321F"), 0.78, specular=0.18)
MAT_EYE = mat_principled("Eye_Deep_Brown", srgb("#160E0A"), 0.10, specular=0.70)
MAT_IRIS = mat_principled("Iris_Warm", srgb("#4E2714"), 0.18, specular=0.58)
MAT_HIGHLIGHT = mat_principled("Eye_Highlight", srgb("#FFFFFF"), 0.04, specular=0.90)
MAT_NOSE = mat_principled("Nose_Soft", srgb("#3B241B"), 0.32, specular=0.42)
MAT_NOSTRIL = mat_principled("Nostril", srgb("#110B08"), 0.52, specular=0.15)
MAT_MOUTH = mat_principled("Mouth_Interior", srgb("#351514"), 0.72, specular=0.12)
MAT_TONGUE = mat_principled("Tongue", srgb("#A94E55"), 0.58, specular=0.26)
MAT_TOOTH = mat_principled("Teeth_Warm", srgb("#F3E4C7"), 0.42, specular=0.30)
MAT_HAT = mat_principled("Hat_Olive", srgb("#777443"), 0.82, specular=0.16)
MAT_HAT_LIGHT = mat_principled("Hat_Olive_Light", srgb("#99955B"), 0.80, specular=0.16)
MAT_LEATHER = mat_principled("Leather_Dark", srgb("#49321F"), 0.58, specular=0.26)
MAT_LEATHER_LIGHT = mat_principled("Leather_Warm", srgb("#8A5530"), 0.55, specular=0.28)
MAT_METAL = mat_principled("Camera_Metal", srgb("#B8B6A9"), 0.30, metallic=0.70, specular=0.55)
MAT_GLASS = mat_principled("Lens", srgb("#203D4B"), 0.12, metallic=0.05, specular=0.85)
MAT_CLAY = mat_principled("Clay_Check", srgb("#B7B1A4"), 0.82, specular=0.12)
MAT_FLOOR = mat_principled("Studio_Floor", srgb("#596A56"), 0.92, specular=0.10)
MAT_BACK = mat_principled("Studio_Back", srgb("#C4D0BE"), 0.96, specular=0.08)


def add_uv(name, loc, scale, mat=None, segments=64, rings=40, col=MODEL, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings,
                                        location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    smooth(obj)
    if mat:
        obj.data.materials.append(mat)
    move_to_collection(obj, col)
    return obj


def add_ico(name, loc, scale, mat=None, subdivisions=3, col=MODEL, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1.0,
                                         location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    smooth(obj)
    if mat:
        obj.data.materials.append(mat)
    move_to_collection(obj, col)
    return obj


def add_cube(name, loc, scale, mat=None, bevel=0.08, col=MODEL, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new("Rounded", "BEVEL")
        mod.width = bevel
        mod.segments = 5
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    smooth(obj)
    if mat:
        obj.data.materials.append(mat)
    move_to_collection(obj, col)
    return obj


def add_cylinder(name, loc, radius, depth, mat=None, vertices=64, col=MODEL,
                 rot=(0, 0, 0), scale=(1, 1, 1), bevel=0.04):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth,
                                        location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new("Rounded", "BEVEL")
        mod.width = bevel
        mod.segments = 4
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    smooth(obj)
    if mat:
        obj.data.materials.append(mat)
    move_to_collection(obj, col)
    return obj


def add_torus(name, loc, major, minor, mat=None, col=MODEL, rot=(0, 0, 0), scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                    major_segments=64, minor_segments=20,
                                    location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    smooth(obj)
    if mat:
        obj.data.materials.append(mat)
    move_to_collection(obj, col)
    return obj


def union_voxel(name, pieces, voxel_size=0.055, material=None, smooth_iterations=2):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in pieces:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = pieces[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = name
    # Voxel remesh fuses intersecting ellipsoids into one sculpt-like volume.
    try:
        obj.data.remesh_voxel_size = voxel_size
        obj.data.remesh_voxel_adaptivity = 0.0
        bpy.ops.object.voxel_remesh()
    except Exception as exc:
        print("VOXEL_REMESH_WARNING", name, repr(exc))
    smooth(obj)
    if material:
        obj.data.materials.clear()
        obj.data.materials.append(material)
    if smooth_iterations:
        mod = obj.modifiers.new("Sculpt_Smooth", "SMOOTH")
        mod.factor = 0.52
        mod.iterations = smooth_iterations
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    sub = obj.modifiers.new("Subdivision_Final", "SUBSURF")
    sub.levels = 1
    sub.render_levels = 1
    return obj


def add_shape(obj, name, transform):
    if obj.data.shape_keys is None:
        obj.shape_key_add(name="Basis")
    key = obj.shape_key_add(name=name)
    for i, point in enumerate(key.data):
        point.co = transform(point.co.copy(), i)
    return key


# -----------------------------------------------------------------------------
# A — Organic silhouette. Head and body are fused sculpt volumes, not a stack of
# visible spheres. Proportions intentionally use a large head and pear body.
# -----------------------------------------------------------------------------
body_pieces = [
    add_uv("Body_Lower_Block", (0, 0.10, 1.30), (0.94, 0.70, 1.08), None, 48, 32),
    add_uv("Body_Belly_Block", (0, -0.10, 1.60), (0.98, 0.72, 0.95), None, 48, 32),
    add_uv("Body_Chest_Block", (0, 0.00, 2.22), (0.78, 0.60, 0.78), None, 48, 32),
    add_uv("Body_Shoulder_Block", (0, 0.03, 2.56), (0.70, 0.56, 0.48), None, 48, 32),
]
body = union_voxel("Body", body_pieces, 0.058, MAT_FUR, 3)

head_pieces = [
    add_uv("Head_Cranium_Block", (0, 0.02, 3.42), (1.00, 0.75, 0.80), None, 56, 36),
    add_uv("Head_Forehead_Block", (0, -0.08, 3.70), (0.86, 0.65, 0.52), None, 48, 32),
    add_uv("Head_Midface_Block", (0, -0.29, 3.25), (0.92, 0.68, 0.61), None, 56, 36),
    add_uv("Head_SnoutBridge_Block", (0, -0.62, 3.23), (0.78, 0.55, 0.44), None, 48, 32),
    add_uv("Head_Muzzle_Block", (0, -0.83, 3.08), (0.66, 0.44, 0.34), None, 48, 32),
]
head = union_voxel("Head", head_pieces, 0.047, MAT_FUR, 3)

# A subtle muzzle patch follows the head instead of making two spherical cheeks.
snout = add_uv("Snout", (0, -0.905, 3.105), (0.62, 0.125, 0.31), MAT_FUR_LIGHT, 64, 40,
               rot=(math.radians(4), 0, 0))

# Ears: small, high and slightly behind the eyes.
for side, sx in (("L", -1), ("R", 1)):
    ear = add_uv(f"Ear_{side}", (0.74 * sx, 0.02, 3.80), (0.22, 0.12, 0.22), MAT_FUR_DARK,
                 48, 32, rot=(math.radians(8), math.radians(12 * sx), math.radians(-8 * sx)))
    inner = add_uv(f"EarInner_{side}", (0.755 * sx, -0.105, 3.80), (0.125, 0.030, 0.125), MAT_FUR_LIGHT,
                   40, 26, rot=(math.radians(8), math.radians(12 * sx), math.radians(-8 * sx)))

# -----------------------------------------------------------------------------
# B — Face. Eyes are glossy dark eyes with tiny highlights, no giant white
# sclera. Nose is wide/flat and the smile is compact.
# -----------------------------------------------------------------------------
face_meshes = []
for side, sx in (("L", -1), ("R", 1)):
    x = 0.43 * sx
    eye = add_uv(f"Eye_{side}", (x, -0.675, 3.49), (0.205, 0.105, 0.235), MAT_EYE, 64, 40,
                 rot=(0, math.radians(3 * sx), 0))
    iris = add_uv(f"Iris_{side}", (x, -0.778, 3.49), (0.125, 0.022, 0.150), MAT_IRIS, 48, 32)
    hi = add_uv(f"EyeHighlight_{side}", (x - 0.052 * sx, -0.806, 3.575), (0.052, 0.015, 0.064), MAT_HIGHLIGHT, 32, 22)
    hi2 = add_uv(f"EyeHighlightSmall_{side}", (x + 0.055 * sx, -0.808, 3.435), (0.022, 0.010, 0.026), MAT_HIGHLIGHT, 24, 16)
    # Brown upper eyelid hugs the eye and removes the staring expression.
    lid = add_uv(f"Eyelid_{side}", (x, -0.789, 3.595), (0.225, 0.026, 0.090), MAT_FUR_DARK, 56, 34,
                 rot=(math.radians(-4), 0, math.radians(-4 * sx)))
    add_shape(lid, f"blink_{side}", lambda co, i: Vector((co.x, co.y, co.z - 0.17)))
    add_shape(lid, f"eye_wide_{side}", lambda co, i: Vector((co.x, co.y, co.z + 0.06)))
    add_shape(lid, f"eye_squint_{side}", lambda co, i: Vector((co.x, co.y, co.z - 0.075)))
    face_meshes.append(lid)

    # Very subtle brow; no thick cartoon caterpillar.
    brow = add_uv(f"Brow_{side}", (x, -0.695, 3.76), (0.19, 0.025, 0.035), MAT_FUR_DARK, 40, 22,
                  rot=(0, 0, math.radians(-5 * sx)))
    add_shape(brow, f"brow_up_{side}", lambda co, i: Vector((co.x, co.y, co.z + 0.09)))
    add_shape(brow, f"brow_down_{side}", lambda co, i: Vector((co.x, co.y, co.z - 0.07)))
    add_shape(brow, f"brow_sad_{side}", lambda co, i, sx=sx: Vector((co.x, co.y, co.z + 0.055 - sx * co.x * 0.06)))
    face_meshes.append(brow)

    # Tiny cheek warmth pads, mostly hidden in the fur.
    cheek = add_uv(f"Cheek_{side}", (0.45 * sx, -1.006, 3.03), (0.16, 0.018, 0.095), MAT_FUR_LIGHT, 36, 22)
    add_shape(cheek, f"cheek_raise_{side}", lambda co, i: Vector((co.x, co.y, co.z + 0.055)))
    add_shape(cheek, f"cheek_puff_{side}", lambda co, i, sx=sx: Vector((co.x + sx * 0.035, co.y - 0.018, co.z)))
    face_meshes.append(cheek)

nose = add_uv("Nose", (0, -1.194, 3.205), (0.39, 0.145, 0.205), MAT_NOSE, 64, 40,
              rot=(math.radians(4), 0, 0))
add_shape(nose, "nose_scrunch", lambda co, i: Vector((co.x * 1.04, co.y, co.z * 0.88 + 0.015)))
face_meshes.append(nose)
for side, sx in (("L", -1), ("R", 1)):
    add_uv(f"Nostril_{side}", (0.145 * sx, -1.325, 3.225), (0.068, 0.020, 0.038), MAT_NOSTRIL, 32, 20,
           rot=(0, 0, math.radians(8 * sx)))

mouth = add_uv("Mouth", (0, -1.135, 2.925), (0.30, 0.035, 0.155), MAT_MOUTH, 56, 34)
add_shape(mouth, "mouth_smile", lambda co, i: Vector((co.x * 1.13, co.y, co.z + 0.035 * (abs(co.x) / 0.30))))
add_shape(mouth, "jaw_open", lambda co, i: Vector((co.x, co.y, co.z - 0.085)))
add_shape(mouth, "mouth_o", lambda co, i: Vector((co.x * 0.62, co.y, co.z * 1.28)))
add_shape(mouth, "mouth_frown", lambda co, i: Vector((co.x, co.y, co.z - 0.045 * (abs(co.x) / 0.30))))
add_shape(mouth, "mouth_pucker", lambda co, i: Vector((co.x * 0.55, co.y - 0.025, co.z)))
add_shape(mouth, "mouth_left", lambda co, i: Vector((co.x - 0.06, co.y, co.z)))
add_shape(mouth, "mouth_right", lambda co, i: Vector((co.x + 0.06, co.y, co.z)))
face_meshes.append(mouth)

tongue = add_uv("Tongue", (0, -1.170, 2.885), (0.18, 0.024, 0.070), MAT_TONGUE, 40, 24)
add_shape(tongue, "tongue_out", lambda co, i: Vector((co.x, co.y - 0.06, co.z - 0.02)))
face_meshes.append(tongue)

# Small incisors, partly hidden by the upper lip.
for side, sx in (("L", -1), ("R", 1)):
    add_cube(f"Tooth_{side}", (0.095 * sx, -1.177, 3.005), (0.082, 0.034, 0.115), MAT_TOOTH, 0.045,
             rot=(math.radians(-2), 0, math.radians(2 * sx)))

# -----------------------------------------------------------------------------
# C — Compact limbs and relaxed pose.
# -----------------------------------------------------------------------------
def soft_limb(name, points, radii, material, voxel=0.045):
    pieces = []
    for i, (point, radius) in enumerate(zip(points, radii)):
        pieces.append(add_uv(f"{name}_part_{i}", point, radius, None, 40, 26))
    return union_voxel(name, pieces, voxel, material, 2)

left_arm = soft_limb("Arm_L", [(-0.69, -0.02, 2.16), (-0.80, -0.18, 1.72), (-0.75, -0.34, 1.28)],
                     [(0.27, 0.25, 0.38), (0.25, 0.23, 0.37), (0.27, 0.22, 0.29)], MAT_FUR, 0.045)
right_arm = soft_limb("Arm_R", [(0.69, -0.01, 2.15), (0.79, -0.17, 1.70), (0.72, -0.35, 1.25)],
                      [(0.27, 0.25, 0.38), (0.25, 0.23, 0.37), (0.27, 0.22, 0.29)], MAT_FUR, 0.045)

# Feet are short, broad and slightly forward, matching the compact body.
for side, sx in (("L", -1), ("R", 1)):
    add_uv(f"Foot_{side}", (0.43 * sx, -0.20, 0.30), (0.43, 0.52, 0.25), MAT_FUR_DARK, 56, 34,
           rot=(0, 0, math.radians(-3 * sx)))
    for toe in range(3):
        tx = 0.43 * sx + (toe - 1) * 0.105
        add_uv(f"Toe_{side}_{toe}", (tx, -0.685, 0.30), (0.055, 0.025, 0.040), MAT_NOSE, 28, 18)
    # fingers are subtle dark pads, not claws.
    for finger in range(3):
        fx = 0.72 * sx + (finger - 1) * 0.07
        add_uv(f"Finger_{side}_{finger}", (fx, -0.555, 1.23), (0.040, 0.024, 0.034), MAT_NOSE, 24, 16)

# -----------------------------------------------------------------------------
# Accessories kept close to the approved reference, but subordinate to the face.
# -----------------------------------------------------------------------------
hat_brim = add_cylinder("Hat_Brim", (0, -0.015, 4.00), 1.02, 0.10, MAT_HAT, 80,
                        scale=(1.08, 0.88, 1.0), bevel=0.055)
hat_crown_parts = [
    add_uv("Hat_Crown_Block", (0, 0.02, 4.22), (0.76, 0.60, 0.32), None, 56, 34),
    add_uv("Hat_Top_Block", (0, 0.05, 4.40), (0.62, 0.49, 0.20), None, 48, 30),
]
hat_crown = union_voxel("Hat_Crown", hat_crown_parts, 0.045, MAT_HAT_LIGHT, 2)
hat_band = add_torus("Hat_Band", (0, 0.015, 4.09), 0.67, 0.042, MAT_LEATHER,
                     rot=(0, 0, 0), scale=(1.04, 0.85, 0.70))

# Backpack behind the torso.
add_cube("Backpack", (0, 0.63, 1.78), (0.56, 0.20, 0.64), MAT_HAT, 0.16,
         rot=(math.radians(-4), 0, 0))
add_cube("Backpack_Pocket", (0, 0.85, 1.62), (0.39, 0.08, 0.24), MAT_HAT_LIGHT, 0.08)
for side, sx in (("L", -1), ("R", 1)):
    add_torus(f"Backpack_Strap_{side}", (0.43 * sx, -0.05, 1.95), 0.55, 0.042, MAT_LEATHER,
              rot=(math.radians(90), 0, 0), scale=(0.36, 0.90, 1.0))

# Camera, smaller and lower than before so the face remains dominant.
add_cube("Camera_Body", (0, -0.73, 1.68), (0.36, 0.14, 0.25), MAT_LEATHER_LIGHT, 0.065)
add_cylinder("Camera_Lens", (0, -0.93, 1.68), 0.17, 0.20, MAT_METAL, 56,
             rot=(math.radians(90), 0, 0), bevel=0.035)
add_cylinder("Camera_Glass", (0, -1.045, 1.68), 0.115, 0.035, MAT_GLASS, 56,
             rot=(math.radians(90), 0, 0), bevel=0.018)
add_torus("Camera_Strap", (0, -0.07, 2.21), 0.75, 0.025, MAT_LEATHER,
          rot=(math.radians(90), 0, 0), scale=(0.72, 1.00, 1.0))

# Minimal armature placeholder for export. Final deformation rig starts after art approval.
bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
ARM = bpy.context.object
ARM.name = "CapibaraRig_V3_Placeholder"
ARM.data.name = "CapibaraRig_V3_Placeholder"
move_to_collection(ARM, MODEL)
root_bone = ARM.data.edit_bones[0]
root_bone.name = "root"
root_bone.head = (0, 0, 0.12)
root_bone.tail = (0, 0, 1.00)

def ebone(name, head_co, tail_co, parent=None):
    b = ARM.data.edit_bones.new(name)
    b.head = head_co
    b.tail = tail_co
    if parent:
        b.parent = ARM.data.edit_bones.get(parent)
    return b

ebone("spine", (0, 0, 0.85), (0, 0, 2.30), "root")
ebone("head", (0, 0, 2.30), (0, 0, 3.60), "spine")
ebone("jaw", (0, -0.25, 3.08), (0, -0.90, 3.00), "head")
for side, sx in (("L", -1), ("R", 1)):
    ebone(f"arm_{side}", (0.55 * sx, 0, 2.30), (0.75 * sx, -0.15, 1.30), "spine")
    ebone(f"leg_{side}", (0.35 * sx, 0, 1.05), (0.43 * sx, -0.15, 0.28), "root")
bpy.ops.object.mode_set(mode="OBJECT")
ARM.show_in_front = True

# Custom metadata for pipeline and Godot.
for obj in MODEL.all_objects:
    obj["capibara_version"] = VERSION
    obj["art_direction"] = "cute_stylized_explorer"

# -----------------------------------------------------------------------------
# Facial expression presets used in real Blender renders.
# -----------------------------------------------------------------------------
EXPRESSIONS = {
    "neutral": {},
    "soft_smile": {"mouth_smile": 0.52, "cheek_raise_L": 0.15, "cheek_raise_R": 0.15},
    "big_smile": {"mouth_smile": 0.92, "jaw_open": 0.30, "cheek_raise_L": 0.32, "cheek_raise_R": 0.32},
    "surprise": {"mouth_o": 0.85, "jaw_open": 0.55, "eye_wide_L": 0.60, "eye_wide_R": 0.60,
                 "brow_up_L": 0.50, "brow_up_R": 0.50},
    "curious": {"mouth_pucker": 0.18, "brow_up_L": 0.48, "brow_down_R": 0.16},
    "sleepy": {"blink_L": 0.66, "blink_R": 0.66, "mouth_o": 0.18},
}


def reset_shape_keys():
    for obj in face_meshes:
        if getattr(obj.data, "shape_keys", None):
            for key in obj.data.shape_keys.key_blocks:
                if key.name != "Basis":
                    key.value = 0.0


def apply_expression(name):
    reset_shape_keys()
    values = EXPRESSIONS.get(name, {})
    for obj in face_meshes:
        if not getattr(obj.data, "shape_keys", None):
            continue
        for key in obj.data.shape_keys.key_blocks:
            if key.name == "Basis":
                continue
            key.value = float(values.get(key.name, 0.0))

# -----------------------------------------------------------------------------
# Studio and real renders. Clean background avoids hiding silhouette problems.
# -----------------------------------------------------------------------------
add_cylinder("Studio_Platform", (0, 0, 0.02), 2.95, 0.20, MAT_FLOOR, 96, STUDIO,
             scale=(1, 1, 1), bevel=0.10)
add_cube("Studio_Backdrop", (0, 2.85, 2.55), (4.6, 0.14, 3.25), MAT_BACK, 0.55, STUDIO)

world = scene.world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value = (0.055, 0.065, 0.052, 1)
bg.inputs["Strength"].default_value = 0.36


def area(name, loc, energy, size, color, rot):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    STUDIO.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = rot
    return obj

area("Key_Warm", (-3.4, -4.4, 6.4), 1250, 4.4, (1.0, 0.74, 0.49),
     (math.radians(30), 0, math.radians(-35)))
area("Fill_Soft", (3.5, -2.0, 4.6), 650, 4.8, (0.62, 0.78, 1.0),
     (math.radians(48), 0, math.radians(42)))
area("Rim", (0, 2.4, 5.8), 1100, 3.4, (0.72, 1.0, 0.75),
     (math.radians(-18), 0, math.radians(180)))

cam_data = bpy.data.cameras.new("Camera")
cam = bpy.data.objects.new("Camera", cam_data)
STUDIO.objects.link(cam)
scene.camera = cam
cam.data.lens = 62


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def render_view(filename, location, target=(0, 0, 2.25), lens=62, expression="soft_smile", res=(1024, 1024)):
    apply_expression(expression)
    cam.location = location
    cam.data.lens = lens
    look_at(cam, target)
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.filepath = os.path.join(OUT_DIR, filename)
    bpy.ops.render.render(write_still=True)

# Beauty model save.
blend_path = os.path.join(OUT_DIR, "capibara_beta_1_0.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

render_view("capibara_beta_front.png", (0, -8.9, 3.10), (0, -0.08, 2.18), 65, "soft_smile")
render_view("capibara_beta_profile.png", (8.5, -0.15, 3.10), (0, -0.02, 2.18), 65, "neutral")
render_view("capibara_beta_three_quarter.png", (5.7, -8.0, 3.48), (0, -0.05, 2.22), 61, "big_smile")
render_view("capibara_beta_rear.png", (4.7, 8.2, 3.35), (0, 0.05, 2.15), 61, "neutral")
render_view("capibara_beta_face.png", (2.70, -5.70, 3.68), (0, -0.45, 3.32), 78, "soft_smile")
render_view("capibara_beta_expression_surprise.png", (2.70, -5.70, 3.68), (0, -0.45, 3.32), 78, "surprise")
render_view("capibara_beta_expression_curious.png", (2.70, -5.70, 3.68), (0, -0.45, 3.32), 78, "curious")
render_view("capibara_beta_expression_sleepy.png", (2.70, -5.70, 3.68), (0, -0.45, 3.32), 78, "sleepy")
render_view("capibara_beta_icon.png", (2.78, -5.92, 3.68), (0, -0.44, 3.32), 76, "big_smile", (512, 512))
scene.render.filepath = os.path.join(PROJECT_DIR, "icon.png")
bpy.ops.render.render(write_still=True)
apply_expression("neutral")

# Clay silhouette renders are generated by temporarily overriding model materials.
original_materials = {}
for obj in MODEL.all_objects:
    if obj.type == "MESH" and obj.data.materials:
        original_materials[obj.name] = [m for m in obj.data.materials]
        obj.data.materials.clear()
        obj.data.materials.append(MAT_CLAY)
render_view("capibara_v3_clay_front.png", (0, -8.9, 3.10), (0, -0.08, 2.18), 65, "neutral")
render_view("capibara_v3_clay_profile.png", (8.5, -0.15, 3.10), (0, -0.02, 2.18), 65, "neutral")
render_view("capibara_v3_clay_three_quarter.png", (5.7, -8.0, 3.48), (0, -0.05, 2.22), 61, "neutral")
for obj in MODEL.all_objects:
    mats = original_materials.get(obj.name)
    if mats is not None:
        obj.data.materials.clear()
        for mat in mats:
            obj.data.materials.append(mat)

# Save again after restoring beauty materials.
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

# Validation report. No false claim that the final rig/20 expressions are done.
def metrics_for(col):
    meshes = [o for o in col.all_objects if o.type == "MESH"]
    for obj in meshes:
        obj.data.calc_loop_triangles()
    return {
        "objects": len(col.all_objects),
        "meshes": len(meshes),
        "vertices": sum(len(o.data.vertices) for o in meshes),
        "triangles": sum(len(o.data.loop_triangles) for o in meshes),
        "materials": len({m.name for o in meshes for m in o.data.materials if m}),
    }

shape_count = sum(
    max(0, len(obj.data.shape_keys.key_blocks) - 1)
    for obj in face_meshes if getattr(obj.data, "shape_keys", None)
)
report = {
    "version": VERSION,
    "art_stages_completed": ART_STAGES,
    "art_status": "V3 blockout + face candidate; requires visual approval before final retopology/rig",
    "lod0": metrics_for(MODEL),
    "bones_placeholder": len(ARM.data.bones),
    "morph_targets_preview": shape_count,
    "expressions_preview": list(EXPRESSIONS.keys()),
    "android_abis": ["armeabi-v7a", "arm64-v8a"],
    "renderer": "Godot GL Compatibility",
}
with open(os.path.join(OUT_DIR, "capibara_beta_validation.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
with open(os.path.join(OUT_DIR, "ITERATIONS_COMPLETED.txt"), "w", encoding="utf-8") as f:
    f.write("CAPIBARA V3 — ART REBUILD\n")
    for i, name in enumerate(ART_STAGES, 1):
        f.write(f"{i:02d}. {name}: IMPLEMENTADA\n")
    f.write("05. retopologia_final: PENDIENTE DE APROBACION VISUAL\n")
    f.write("06. rig_corporal_final: PENDIENTE\n")
    f.write("07. rig_facial_completo: PENDIENTE\n")
    f.write("08. veinte_expresiones: PENDIENTE\n")
print("CAPIBARA_V3_ART_REBUILD_OK")
print("REPORT", json.dumps(report, ensure_ascii=False))
