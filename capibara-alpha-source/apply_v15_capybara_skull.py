from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "capibara-alpha-source/create_capybara_v13_character_rebuild.py")
text = path.read_text(encoding="utf-8")
text = text.replace('VERSION = "14.0.0-fused-head-sculpt"', 'VERSION = "15.0.0-capybara-skull"', 1)

# Finer, lower-contrast fur instead of large cloudy spots.
text = text.replace('noise.inputs["Scale"].default_value = 16.0', 'noise.inputs["Scale"].default_value = 34.0', 1)
text = text.replace('noise.inputs["Detail"].default_value = 2.2', 'noise.inputs["Detail"].default_value = 2.7', 1)
text = text.replace('noise.inputs["Roughness"].default_value = 0.52', 'noise.inputs["Roughness"].default_value = 0.58', 1)

# Push cheek and muzzle masses forward before voxel fusion to create a short,
# broad capybara snout rather than a bear face.
repls = {
    '(0, -0.82, 2.98), (0.52, 0.28, 0.30)': '(0, -0.94, 2.96), (0.54, 0.30, 0.29)',
    '(-0.27, -0.80, 2.90), (0.36, 0.26, 0.27)': '(-0.27, -0.89, 2.88), (0.37, 0.27, 0.27)',
    '(0.27, -0.80, 2.90), (0.36, 0.26, 0.27)': '(0.27, -0.89, 2.88), (0.37, 0.27, 0.27)',
}
for old, new in repls.items():
    if old not in text:
        raise RuntimeError(f'V15 muzzle target not found: {old}')
    text = text.replace(old, new, 1)

# Remove the hard polygon material mask. Uniform fur plus geometry gives a much
# cleaner face; localized colour can be painted after retopology.
mask = '''head_master.data.materials.append(MAT_MUZZLE)
for poly in head_master.data.polygons:
    center = sum((head_master.data.vertices[i].co for i in poly.vertices), Vector()) / max(1, len(poly.vertices))
    if center.y < -0.62 and 2.68 < center.z < 3.20:
        poly.material_index = 1'''
if mask not in text:
    raise RuntimeError('V15 material mask not found')
text = text.replace(mask, '', 1)

# True capybara skull: lower, longer front-to-back, slightly narrower. Set the
# origin to the actual head center before scaling so it does not slide away.
old_transform = '''head_master.scale.x = 0.94
head_master.scale.z = 0.96
bpy.context.view_layer.objects.active = head_master
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)'''
new_transform = '''bpy.context.view_layer.objects.active = head_master
bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
head_master.scale = (0.92, 1.10, 0.82)
head_master.location.z -= 0.04
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)'''
if old_transform not in text:
    raise RuntimeError('V15 head transform not found')
text = text.replace(old_transform, new_transform, 1)

# Reposition facial features on the lower, elongated skull.
face = {
    '(x, -0.70, 3.32), (0.145, 0.088, 0.185)': '(x, -0.80, 3.22), (0.132, 0.082, 0.168)',
    '(x - 0.035 * sx, -0.792, 3.395), (0.027, 0.007, 0.034)': '(x - 0.032 * sx, -0.880, 3.282), (0.025, 0.006, 0.031)',
    '(x + 0.037 * sx, -0.795, 3.270), (0.008, 0.003, 0.010)': '(x + 0.032 * sx, -0.883, 3.170), (0.007, 0.003, 0.009)',
    '(0, -1.080, 3.02), (0.225, 0.060, 0.110)': '(0, -1.205, 2.955), (0.225, 0.065, 0.105)',
    '(0.082 * sx, -1.137, 3.035)': '(0.082 * sx, -1.267, 2.968)',
    '(0, -0.995, 2.72), (0.290, 0.225, 0.170)': '(0, -1.095, 2.690), (0.295, 0.225, 0.165)',
    '(0, -0.985, 2.715), (0.268, 0.018, 0.150)': '(0, -1.132, 2.685), (0.270, 0.018, 0.145)',
    '(0, -1.008, 2.645)': '(0, -1.150, 2.615)',
    '(0.050 * sx, -1.010, 2.820)': '(0.050 * sx, -1.150, 2.790)',
}
for old, new in face.items():
    if old not in text:
        raise RuntimeError(f'V15 face placement not found: {old}')
    text = text.replace(old, new, 1)

# Attach ears to the flattened skull.
text = text.replace('(0.78 * sx, 0.02, 3.83), (0.16, 0.09, 0.16)',
                    '(0.70 * sx, 0.00, 3.61), (0.145, 0.085, 0.145)', 1)
text = text.replace('(0.785 * sx, -0.065, 3.83), (0.075, 0.012, 0.075)',
                    '(0.705 * sx, -0.075, 3.61), (0.068, 0.011, 0.068)', 1)

# Lower and slightly shrink the explorer hat to sit on the new cranium.
text = text.replace('(0, 0.00, 4.00), 0.92, 0.075', '(0, 0.00, 3.78), 0.87, 0.070', 1)
for old, new in {
    '(4.03, 0.02, 0.64, 0.48)': '(3.81, 0.02, 0.60, 0.45)',
    '(4.17, 0.04, 0.62, 0.46)': '(3.94, 0.04, 0.58, 0.43)',
    '(4.34, 0.06, 0.54, 0.40)': '(4.10, 0.06, 0.51, 0.37)',
    '(4.43, 0.07, 0.40, 0.30)': '(4.19, 0.07, 0.38, 0.28)',
    '(0, 0.01, 4.10)': '(0, 0.01, 3.88)',
}.items():
    if old not in text:
        raise RuntimeError(f'V15 hat target not found: {old}')
    text = text.replace(old, new, 1)

# Make teeth clearly visible inside the smile.
text = text.replace('(0.037, 0.014, 0.058)', '(0.042, 0.016, 0.064)', 1)

# Reframe the shorter skull.
text = text.replace('(0, -7.75, 3.10), (0, -0.10, 2.20), 67',
                    '(0, -7.55, 2.95), (0, -0.14, 2.08), 67', 1)
text = text.replace('(7.7, -0.10, 3.10), (0, 0.00, 2.20), 67',
                    '(7.45, -0.10, 2.95), (0, 0.00, 2.08), 67', 1)
text = text.replace('(4.85, -6.45, 3.18), (0, -0.15, 2.22), 68',
                    '(4.65, -6.35, 3.00), (0, -0.18, 2.08), 68', 1)

path.write_text(text, encoding='utf-8')
print('CAPIBARA_V15_CAPYBARA_SKULL_OK', path)
