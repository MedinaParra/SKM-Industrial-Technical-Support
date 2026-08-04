from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "capibara-alpha-source/create_capybara_v13_character_rebuild.py")
text = path.read_text(encoding="utf-8")
text = text.replace('VERSION = "13.0.0-character-rebuild"', 'VERSION = "14.0.0-fused-head-sculpt"', 1)

# Lower-contrast, finer fur; V13 appeared blotchy and dirty.
text = text.replace('noise.inputs["Scale"].default_value = 9.0', 'noise.inputs["Scale"].default_value = 16.0', 1)
text = text.replace('noise.inputs["Detail"].default_value = 3.2', 'noise.inputs["Detail"].default_value = 2.2', 1)
text = text.replace('noise.inputs["Roughness"].default_value = 0.62', 'noise.inputs["Roughness"].default_value = 0.52', 1)
text = text.replace('ramp.color_ramp.elements[0].position = 0.28', 'ramp.color_ramp.elements[0].position = 0.18', 1)
text = text.replace('ramp.color_ramp.elements[1].position = 0.72', 'ramp.color_ramp.elements[1].position = 0.82', 1)
text = text.replace('fine.inputs["Scale"].default_value = 115.0', 'fine.inputs["Scale"].default_value = 145.0', 1)
text = text.replace('bump.inputs["Strength"].default_value = 0.09', 'bump.inputs["Strength"].default_value = 0.055', 1)

# Add a robust voxel fusion helper before the character construction.
anchor = '\n# -----------------------------------------------------------------------------\n# Character surfaces\n# -----------------------------------------------------------------------------\n'
if anchor not in text:
    raise RuntimeError('V14 character anchor not found')
helper = '''

def fuse_head(name, objects, material, voxel_size=0.026):
    converted = []
    for obj in objects:
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.convert(target="MESH")
        converted.append(obj)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in converted:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = converted[0]
    bpy.ops.object.join()
    result = bpy.context.object
    result.name = name
    result.data.remesh_voxel_size = voxel_size
    result.data.remesh_voxel_adaptivity = 0.0
    bpy.ops.object.voxel_remesh()
    for p in result.data.polygons:
        p.use_smooth = True
    result.data.materials.clear()
    result.data.materials.append(material)
    smooth = result.modifiers.new("Organic face smoothing", "SMOOTH")
    smooth.factor = 0.25
    smooth.iterations = 7
    bpy.context.view_layer.objects.active = result
    bpy.ops.object.modifier_apply(modifier=smooth.name)
    sub = result.modifiers.new("Final face subdivision", "SUBSURF")
    sub.levels = 1
    sub.render_levels = 1
    return result

'''
text = text.replace(anchor, helper + anchor, 1)

# Capture all head components, then fuse them into one organic surface.
text = text.replace('uv("Neck_Fill", (0, 0.10, 2.72), (0.72, 0.55, 0.42), MAT_FUR, 48, 30)',
                    'neck_fill = uv("Neck_Fill", (0, 0.10, 2.72), (0.72, 0.55, 0.42), MAT_FUR, 48, 30)', 1)
text = text.replace('uv("Muzzle_Center", (0, -0.91, 2.98), (0.52, 0.23, 0.30), MAT_MUZZLE, 56, 34)',
                    'muzzle_center = uv("Muzzle_Center", (0, -0.82, 2.98), (0.52, 0.28, 0.30), MAT_FUR, 56, 34)', 1)
text = text.replace('uv("Muzzle_L", (-0.28, -0.86, 2.90), (0.37, 0.22, 0.28), MAT_MUZZLE, 48, 30)',
                    'muzzle_l = uv("Muzzle_L", (-0.27, -0.80, 2.90), (0.36, 0.26, 0.27), MAT_FUR, 48, 30)', 1)
text = text.replace('uv("Muzzle_R", (0.28, -0.86, 2.90), (0.37, 0.22, 0.28), MAT_MUZZLE, 48, 30)',
                    'muzzle_r = uv("Muzzle_R", (0.27, -0.80, 2.90), (0.36, 0.26, 0.27), MAT_FUR, 48, 30)\nhead_master = fuse_head("Head_Fused_Sculpt", [head, neck_fill, muzzle_center, muzzle_l, muzzle_r], MAT_FUR, 0.025)\nhead_master.data.materials.append(MAT_MUZZLE)\nfor poly in head_master.data.polygons:\n    center = sum((head_master.data.vertices[i].co for i in poly.vertices), Vector()) / max(1, len(poly.vertices))\n    if center.y < -0.62 and 2.68 < center.z < 3.20:\n        poly.material_index = 1', 1)

# Remove the floating upper eyelid objects completely.
lid = '''    uv(f"Upper_Lid_{side}", (x, -0.725, 3.465), (0.175, 0.075, 0.075), MAT_FUR, 44, 28,
       rot=(math.radians(-3), 0, math.radians(-3 * sx)))
'''
if lid not in text:
    raise RuntimeError('V14 eyelid block not found')
text = text.replace(lid, '', 1)

# Carve a real smile cavity into the fused head instead of displaying a dark
# disk in front of the muzzle.
old_mouth = 'uv("Mouth_Interior", (0, -1.105, 2.72), (0.285, 0.025, 0.165), MAT_MOUTH, 48, 30)'
new_mouth = '''mouth_cutter = uv("Mouth_Cutter", (0, -0.995, 2.72), (0.290, 0.225, 0.170), MAT_MOUTH, 48, 30)
for obj in (head_master, mouth_cutter):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target="MESH")
boolean = head_master.modifiers.new("Carve integrated smile", "BOOLEAN")
boolean.operation = "DIFFERENCE"
boolean.solver = "EXACT"
boolean.object = mouth_cutter
bpy.context.view_layer.objects.active = head_master
bpy.ops.object.modifier_apply(modifier=boolean.name)
bpy.data.objects.remove(mouth_cutter, do_unlink=True)
uv("Mouth_Interior", (0, -0.985, 2.715), (0.268, 0.018, 0.150), MAT_MOUTH, 48, 30)'''
if old_mouth not in text:
    raise RuntimeError('V14 mouth target not found')
text = text.replace(old_mouth, new_mouth, 1)

# More natural eye scale and smaller catchlights.
text = text.replace('(0.155, 0.095, 0.205)', '(0.145, 0.088, 0.185)', 1)
text = text.replace('(0.034, 0.008, 0.043)', '(0.027, 0.007, 0.034)', 1)
text = text.replace('(0.010, 0.004, 0.013)', '(0.008, 0.003, 0.010)', 1)

# Nose and mouth sit closer to the fused surface.
text = text.replace('(0, -1.145, 3.02), (0.245, 0.075, 0.125)',
                    '(0, -1.080, 3.02), (0.225, 0.060, 0.110)', 1)
text = text.replace('(0.090 * sx, -1.217, 3.035)', '(0.082 * sx, -1.137, 3.035)', 1)
text = text.replace('(0, -1.130, 2.645)', '(0, -1.008, 2.645)', 1)
text = text.replace('(0.052 * sx, -1.128, 2.825)', '(0.050 * sx, -1.010, 2.820)', 1)

# Reduce overall head width slightly and lower the hat for a more capybara-like
# silhouette. This transformation is applied after all face objects are added.
transform_anchor = '# Small round ears.\n'
if transform_anchor not in text:
    raise RuntimeError('V14 transform anchor not found')
text = text.replace(transform_anchor,
'''# Refine the fused skull proportions after remeshing.
head_master.scale.x = 0.94
head_master.scale.z = 0.96
bpy.context.view_layer.objects.active = head_master
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Small round ears.
''', 1)

# Slightly wider body to balance the reduced head.
body_scale_anchor = 'body = loft_z("Body_Pear", body_sections, 52, MAT_FUR)'
text = text.replace(body_scale_anchor,
body_scale_anchor + '\nbody.scale.x = 1.06\nbpy.context.view_layer.objects.active = body\nbpy.ops.object.transform_apply(location=False, rotation=False, scale=True)', 1)

path.write_text(text, encoding='utf-8')
print('CAPIBARA_V14_FUSED_HEAD_SCULPT_OK', path)
