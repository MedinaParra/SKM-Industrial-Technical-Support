from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "capibara-alpha-source/create_capybara_v13_character_rebuild.py")
text = path.read_text(encoding="utf-8")
text = text.replace('VERSION = "15.0.0-capybara-skull"', 'VERSION = "16.0.0-head-assembly-correction"', 1)

# Refine the muzzle before fusion. V15 pushed the cheek cluster too far and
# created a giant lower lip.
repls = {
    '(0, -0.94, 2.96), (0.54, 0.30, 0.29)': '(0, -0.84, 2.96), (0.47, 0.245, 0.245)',
    '(-0.27, -0.89, 2.88), (0.37, 0.27, 0.27)': '(-0.25, -0.82, 2.88), (0.31, 0.225, 0.235)',
    '(0.27, -0.89, 2.88), (0.37, 0.27, 0.27)': '(0.25, -0.82, 2.88), (0.31, 0.225, 0.235)',
}
for old, new in repls.items():
    if old not in text:
        raise RuntimeError(f'V16 muzzle target not found: {old}')
    text = text.replace(old, new, 1)

# Use a moderate skull transform. The V15 transform was too aggressive and was
# applied only to the fused surface, causing all features to float.
old_transform = '''bpy.context.view_layer.objects.active = head_master
bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
head_master.scale = (0.92, 1.10, 0.82)
head_master.location.z -= 0.04
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)'''
new_transform = '''bpy.context.view_layer.objects.active = head_master
bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
head_master.scale = (0.96, 1.03, 0.91)
head_master.location.z -= 0.015
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)'''
if old_transform not in text:
    raise RuntimeError('V16 head transform target not found')
text = text.replace(old_transform, new_transform, 1)

# Place all facial components on the corrected surface.
face = {
    '(x, -0.80, 3.22), (0.132, 0.082, 0.168)': '(x, -0.755, 3.245), (0.135, 0.082, 0.172)',
    '(x - 0.032 * sx, -0.880, 3.282), (0.025, 0.006, 0.031)': '(x - 0.032 * sx, -0.837, 3.307), (0.026, 0.006, 0.032)',
    '(x + 0.032 * sx, -0.883, 3.170), (0.007, 0.003, 0.009)': '(x + 0.032 * sx, -0.840, 3.193), (0.007, 0.003, 0.009)',
    '(0, -1.205, 2.955), (0.225, 0.065, 0.105)': '(0, -1.095, 2.965), (0.215, 0.055, 0.100)',
    '(0.082 * sx, -1.267, 2.968)': '(0.078 * sx, -1.148, 2.978)',
    '(0, -1.095, 2.690), (0.295, 0.225, 0.165)': '(0, -1.000, 2.715), (0.270, 0.205, 0.155)',
    '(0, -1.132, 2.685), (0.270, 0.018, 0.145)': '(0, -1.060, 2.710), (0.255, 0.018, 0.140)',
    '(0, -1.150, 2.615)': '(0, -1.080, 2.640)',
    '(0.050 * sx, -1.150, 2.790)': '(0.050 * sx, -1.080, 2.815)',
}
for old, new in face.items():
    if old not in text:
        raise RuntimeError(f'V16 feature target not found: {old}')
    text = text.replace(old, new, 1)

# Reattach ears and explorer hat to the skull.
text = text.replace('(0.70 * sx, 0.00, 3.61), (0.145, 0.085, 0.145)',
                    '(0.70 * sx, 0.01, 3.72), (0.145, 0.085, 0.145)', 1)
text = text.replace('(0.705 * sx, -0.075, 3.61), (0.068, 0.011, 0.068)',
                    '(0.705 * sx, -0.067, 3.72), (0.068, 0.011, 0.068)', 1)
text = text.replace('(0, 0.00, 3.78), 0.87, 0.070', '(0, 0.00, 3.88), 0.88, 0.070', 1)
for old, new in {
    '(3.81, 0.02, 0.60, 0.45)': '(3.91, 0.02, 0.60, 0.45)',
    '(3.94, 0.04, 0.58, 0.43)': '(4.04, 0.04, 0.58, 0.43)',
    '(4.10, 0.06, 0.51, 0.37)': '(4.20, 0.06, 0.51, 0.37)',
    '(4.19, 0.07, 0.38, 0.28)': '(4.29, 0.07, 0.38, 0.28)',
    '(0, 0.01, 3.88)': '(0, 0.01, 3.98)',
}.items():
    if old not in text:
        raise RuntimeError(f'V16 hat target not found: {old}')
    text = text.replace(old, new, 1)

# The lower face should not dominate the body. Slightly increase shoulder mass
# and keep the head/body transition hidden.
text = text.replace('(2.50, 0.08, 0.66, 0.50)', '(2.50, 0.08, 0.70, 0.53)', 1)
text = text.replace('(2.67, 0.09, 0.55, 0.42)', '(2.67, 0.09, 0.61, 0.46)', 1)
text = text.replace('(0, 0.10, 2.72), (0.72, 0.55, 0.42)',
                    '(0, 0.09, 2.72), (0.76, 0.58, 0.44)', 1)

# Use close colours to remove remaining camouflage-like mottling.
text = text.replace('(0.12, 0.040, 0.010, 1), (0.37, 0.155, 0.050, 1)',
                    '(0.135, 0.050, 0.015, 1), (0.30, 0.125, 0.040, 1)', 1)
text = text.replace('(0.19, 0.070, 0.020, 1), (0.43, 0.205, 0.080, 1)',
                    '(0.18, 0.065, 0.020, 1), (0.34, 0.150, 0.055, 1)', 1)

path.write_text(text, encoding='utf-8')
print('CAPIBARA_V16_HEAD_ASSEMBLY_CORRECTION_OK', path)
