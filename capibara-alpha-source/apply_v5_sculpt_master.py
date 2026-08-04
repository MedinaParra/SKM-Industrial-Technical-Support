from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "capibara-alpha-source/create_capybara_v4_clean_surface.py")
text = path.read_text(encoding="utf-8")
text = text.replace('VERSION = "4.3.0-face-body-fur-refine"', 'VERSION = "5.0.0-sculpt-master"', 1)

# Add an actual sculpt-master fusion stage. Body, neck, cranium and muzzle are
# converted to evaluated meshes, voxel-remeshed as one organic mass and gently
# smoothed. Retopology happens only after visual approval.
anchor = '''def curve_limb(name, points, radius, mat):
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
'''
if anchor not in text:
    raise RuntimeError('fusion function insertion anchor not found')
fusion = anchor + '''

def fuse_sculpt_master(name, objects, voxel_size=0.030):
    # Apply subdivision before fusion so the remesh follows the intended cage.
    converted = []
    for obj in objects:
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.convert(target="MESH")
        converted.append(bpy.context.object)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in converted:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = converted[0]
    bpy.ops.object.join()
    fused = bpy.context.object
    fused.name = name
    fused.data.name = name + "Mesh"
    fused.data.remesh_voxel_size = voxel_size
    fused.data.remesh_voxel_adaptivity = 0.0
    bpy.ops.object.voxel_remesh()
    smooth = fused.modifiers.new("Sculpt polish", "SMOOTH")
    smooth.factor = 0.22
    smooth.iterations = 7
    bpy.context.view_layer.objects.active = fused
    bpy.ops.object.modifier_apply(modifier=smooth.name)
    corrective = fused.modifiers.new("Sculpt subdivision", "SUBSURF")
    corrective.levels = 1
    corrective.render_levels = 1
    corrective.subdivision_type = "CATMULL_CLARK"
    for poly in fused.data.polygons:
        poly.use_smooth = True
    return fused
'''
text = text.replace(anchor, fusion, 1)

# Replace the paper-thin muzzle patch with a real broad capybara muzzle volume,
# plus a hidden neck core that gives the fusion enough overlap.
old_muzzle = '''# Warm integrated muzzle, smaller nose and friendly but restrained smile.
face_replacements = {'''
# The previous comment lives only in the patch source, not the generated model.
# Locate the generated Muzzle_Tone call directly instead.
old_call = 'uv("Muzzle_Tone", (0, -1.112, 3.015), (0.48, 0.010, 0.175), MAT_FUR_LIGHT, 56, 32)'
new_call = '''muzzle_core = uv("Muzzle_Core", (0, -1.015, 3.015), (0.54, 0.285, 0.245), MAT_FUR, 56, 34)
neck_core = uv("Neck_Core", (0, 0.035, 2.900), (0.66, 0.54, 0.32), MAT_FUR, 52, 32)
sculpt_master = fuse_sculpt_master("Capibara_Sculpt_Master", [body, head, muzzle_core, neck_core], 0.030)
# A flush tonal patch is kept outside the fusion for art direction and can be
# baked later into the final mobile texture.
uv("Muzzle_Tone", (0, -1.286, 3.015), (0.47, 0.018, 0.172), MAT_FUR_LIGHT, 52, 32)'''
if old_call not in text:
    raise RuntimeError('generated muzzle call not found')
text = text.replace(old_call, new_call, 1)

# Eyes sit deeper into the fused cheeks and are framed with subtle upper lids.
eye_anchor = '''    uv(f"EyeHighlightSmall_{side}", (x + 0.041 * sx, -0.886, 3.310), (0.014, 0.005, 0.017), MAT_WHITE, 20, 14)
'''
if eye_anchor not in text:
    raise RuntimeError('eye insertion anchor not found')
eye_insert = eye_anchor + '''    uv(f"UpperLid_{side}", (x, -0.894, 3.485), (0.172, 0.014, 0.052), MAT_FUR_DARK, 42, 26,
       rot=(math.radians(-3), 0, math.radians(-3 * sx)))
'''
text = text.replace(eye_anchor, eye_insert, 1)

# Facial features follow the new projecting muzzle.
face = {
    '(0, -1.172, 3.070), (0.270, 0.065, 0.120)': '(0, -1.330, 3.075), (0.270, 0.070, 0.120)',
    '(0.098 * sx, -1.237, 3.080)': '(0.098 * sx, -1.398, 3.085)',
    '(0, -1.145, 2.875), (0.205, 0.017, 0.102)': '(0, -1.312, 2.875), (0.210, 0.019, 0.108)',
    '(0, -1.164, 2.845), (0.105, 0.009, 0.038)': '(0, -1.332, 2.842), (0.108, 0.010, 0.040)',
    '(0.056 * sx, -1.166, 2.930), (0.041, 0.014, 0.059)': '(0.056 * sx, -1.334, 2.930), (0.042, 0.015, 0.061)',
}
for old, new in face.items():
    if old not in text:
        raise RuntimeError(f'sculpt facial target not found: {old}')
    text = text.replace(old, new, 1)

# More characterful explorer camera: rounded leather body, silver top plate,
# lens rings and shutter button. These remain simple game-ready pieces.
camera_anchor = 'cube("Camera_Body", (0, -0.73, 1.48), (0.29, 0.11, 0.21), MAT_LEATHER_LIGHT, 0.055)'
if camera_anchor not in text:
    raise RuntimeError('camera anchor not found')
camera_replacement = '''cube("Camera_Body", (0, -0.73, 1.48), (0.30, 0.11, 0.215), MAT_LEATHER_LIGHT, 0.070)
cube("Camera_Top", (0, -0.745, 1.665), (0.25, 0.105, 0.055), MAT_METAL, 0.025)
uv("Camera_Shutter", (-0.17, -0.865, 1.735), (0.045, 0.018, 0.028), MAT_METAL, 24, 16)'''
text = text.replace(camera_anchor, camera_replacement, 1)
text = text.replace('cylinder("Camera_Lens", (0, -0.89, 1.48), 0.145, 0.16, MAT_METAL, 48,',
                    'cylinder("Camera_Lens", (0, -0.90, 1.48), 0.155, 0.18, MAT_METAL, 56,', 1)
text = text.replace('cylinder("Camera_Glass", (0, -0.985, 1.48), 0.095, 0.028, MAT_GLASS, 48,',
                    'cylinder("Camera_Glass", (0, -1.008, 1.48), 0.100, 0.030, MAT_GLASS, 52,', 1)

# Slightly warmer key light and softer fill for the fur evaluation.
text = text.replace('1050, 4.4, (1.0, 0.76, 0.52)', '1180, 4.8, (1.0, 0.72, 0.46)', 1)
text = text.replace('600, 4.5, (0.66, 0.80, 1.0)', '720, 5.0, (0.70, 0.82, 1.0)', 1)

path.write_text(text, encoding='utf-8')
print('CAPIBARA_V5_SCULPT_MASTER_OK', path)
