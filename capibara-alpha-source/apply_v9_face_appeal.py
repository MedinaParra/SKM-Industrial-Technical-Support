from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "capibara-alpha-source/create_capybara_v4_clean_surface.py")
text = path.read_text(encoding="utf-8")
text = text.replace('VERSION = "8.0.0-hero-proportions"', 'VERSION = "9.0.0-face-appeal"', 1)

# Replace elongated wood-grain mapping with short dense fur variation.
text = text.replace('mapping.inputs["Scale"].default_value = (24.0, 24.0, 4.0)',
                    'mapping.inputs["Scale"].default_value = (42.0, 42.0, 18.0)', 1)
text = text.replace('color_noise.inputs["Detail"].default_value = 2.3',
                    'color_noise.inputs["Detail"].default_value = 4.5', 1)
text = text.replace('color_noise.inputs["Roughness"].default_value = 0.58',
                    'color_noise.inputs["Roughness"].default_value = 0.66', 1)
text = text.replace('fine_mapping.inputs["Scale"].default_value = (72.0, 72.0, 8.0)',
                    'fine_mapping.inputs["Scale"].default_value = (115.0, 115.0, 34.0)', 1)
text = text.replace('fine.inputs["Detail"].default_value = 2.0',
                    'fine.inputs["Detail"].default_value = 3.2', 1)
text = text.replace('bump.inputs["Strength"].default_value = 0.075',
                    'bump.inputs["Strength"].default_value = 0.095', 1)
text = text.replace('bsdf.inputs["Roughness"].default_value = 0.78',
                    'bsdf.inputs["Roughness"].default_value = 0.70\n    if "Sheen Weight" in bsdf.inputs:\n        bsdf.inputs["Sheen Weight"].default_value = 0.10', 1)

# Less balloon-like forehead, fuller lower face.
start = text.index('core_sections = [')
end_marker = 'body = loft_z("Capibara_Unified_Core_Cage", core_sections, 56, MAT_FUR, 2)'
end = text.index(end_marker, start) + len(end_marker)
core = '''core_sections = [
    (0.24, 0.02, 0.34, 0.36),
    (0.38, 0.00, 0.56, 0.49),
    (0.62, 0.01, 0.75, 0.59),
    (0.88, 0.00, 0.84, 0.64),
    (1.14, -0.02, 0.88, 0.67),
    (1.38, -0.02, 0.86, 0.66),
    (1.60, 0.00, 0.82, 0.63),
    (1.80, 0.03, 0.78, 0.59),
    (1.98, 0.04, 0.73, 0.55),
    (2.13, 0.03, 0.67, 0.50),
    (2.26, 0.00, 0.70, 0.52),
    (2.38, -0.05, 0.83, 0.60),
    (2.53, -0.10, 0.98, 0.70),
    (2.72, -0.14, 1.08, 0.77),
    (2.94, -0.14, 1.08, 0.78),
    (3.15, -0.10, 1.02, 0.73),
    (3.33, -0.05, 0.90, 0.63),
    (3.48, 0.00, 0.72, 0.51),
    (3.59, 0.02, 0.47, 0.34),
    (3.65, 0.02, 0.21, 0.15),
]
body = loft_z("Capibara_Unified_Core_Cage", core_sections, 56, MAT_FUR, 2)'''
text = text[:start] + core + text[end:]

# Push the muzzle forward and slightly upward, while keeping broad cheeks.
cluster = {
    '(0, -0.700, 2.900), (0.60, 0.305, 0.315)': '(0, -0.790, 2.900), (0.62, 0.335, 0.325)',
    '(-0.36, -0.555, 2.890), (0.43, 0.285, 0.315)': '(-0.36, -0.625, 2.885), (0.44, 0.300, 0.320)',
    '(0.36, -0.555, 2.890), (0.43, 0.285, 0.315)': '(0.36, -0.625, 2.885), (0.44, 0.300, 0.320)',
    '(0, -0.555, 2.660), (0.45, 0.245, 0.230)': '(0, -0.635, 2.650), (0.47, 0.270, 0.245)',
}
for old, new in cluster.items():
    if old not in text:
        raise RuntimeError(f'V9 muzzle target not found: {old}')
    text = text.replace(old, new, 1)

# Assign muzzle colour directly to the sculpt polygons instead of adding a
# floating oval patch. This follows the fused surface and survives animation.
anchor = '''sculpt_master = fuse_sculpt_master("Capibara_Sculpt_Master", [body, muzzle_core, cheek_core_l, cheek_core_r, lower_jaw_core], 0.024)'''
if anchor not in text:
    raise RuntimeError('V9 sculpt assignment anchor not found')
assignment = anchor + '''
sculpt_master.data.materials.append(MAT_FUR_LIGHT)
for poly in sculpt_master.data.polygons:
    center = sum((sculpt_master.data.vertices[i].co for i in poly.vertices), Vector()) / max(1, len(poly.vertices))
    if center.y < -0.77 and 2.58 < center.z < 3.15:
        poly.material_index = 1'''
text = text.replace(anchor, assignment, 1)

# Large friendly eyes, still lateral; substantial nose; open smile with a small
# tongue and discreet incisors.
face = {
    'x = 0.50 * sx': 'x = 0.49 * sx',
    '(x, -0.735, 3.045), (0.150, 0.080, 0.182)': '(x, -0.785, 3.045), (0.168, 0.088, 0.198)',
    '(x - 0.036 * sx, -0.817, 3.112), (0.034, 0.007, 0.041)': '(x - 0.040 * sx, -0.875, 3.120), (0.039, 0.008, 0.047)',
    '(x + 0.036 * sx, -0.820, 2.998), (0.012, 0.004, 0.015)': '(x + 0.041 * sx, -0.878, 2.985), (0.014, 0.005, 0.017)',
    '(0, -1.020, 2.875), (0.250, 0.055, 0.112)': '(0, -1.180, 2.905), (0.285, 0.075, 0.130)',
    '(0.090 * sx, -1.076, 2.886)': '(0.105 * sx, -1.250, 2.920)',
    '(0, -0.995, 2.630), (0.255, 0.025, 0.165)': '(0, -1.135, 2.615), (0.275, 0.030, 0.175)',
    '(0, -1.025, 2.555), (0.072, 0.008, 0.026)': '(0, -1.165, 2.530), (0.067, 0.008, 0.024)',
    '(0.050 * sx, -1.018, 2.720), (0.032, 0.010, 0.045)': '(0.050 * sx, -1.155, 2.720), (0.031, 0.010, 0.043)',
}
for old, new in face.items():
    if old not in text:
        raise RuntimeError(f'V9 face target not found: {old}')
    text = text.replace(old, new, 1)

# Ears become visible character features rather than tiny buttons.
text = text.replace('(0.78 * sx, 0.05, 3.39), (0.135, 0.074, 0.135)',
                    '(0.76 * sx, 0.02, 3.39), (0.165, 0.090, 0.165)', 1)
text = text.replace('(0.785 * sx, -0.022, 3.39), (0.064, 0.010, 0.064)',
                    '(0.765 * sx, -0.065, 3.39), (0.078, 0.013, 0.078)', 1)

# Wave hand is larger and further forward, making the greeting readable.
text = text.replace('(-0.95, -0.23, 2.38), (0.205, 0.145, 0.205)',
                    '(-0.98, -0.35, 2.38), (0.225, 0.170, 0.225)', 1)
text = text.replace('(x, -0.255, 2.555 +', '(x, -0.410, 2.555 +', 1)
text = text.replace('(-0.785, -0.255, 2.360)', '(-0.790, -0.405, 2.360)', 1)

# Hero three-quarter view is the main approval image.
text = text.replace('(4.35, -6.65, 2.90), (0, -0.08, 1.88), 66',
                    '(4.05, -6.30, 2.82), (0, -0.16, 1.92), 68', 1)

path.write_text(text, encoding='utf-8')
print('CAPIBARA_V9_FACE_APPEAL_OK', path)
