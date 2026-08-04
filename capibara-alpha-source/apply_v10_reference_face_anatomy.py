from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "capibara-alpha-source/create_capybara_v4_clean_surface.py")
text = path.read_text(encoding="utf-8")
text = text.replace('VERSION = "9.0.0-face-appeal"', 'VERSION = "10.0.0-reference-face-anatomy"', 1)

# Slightly reduce the skull width while maintaining broad lower cheeks.
start = text.index('core_sections = [')
end_marker = 'body = loft_z("Capibara_Unified_Core_Cage", core_sections, 56, MAT_FUR, 2)'
end = text.index(end_marker, start) + len(end_marker)
core = '''core_sections = [
    (0.24, 0.02, 0.34, 0.36),
    (0.38, 0.00, 0.58, 0.50),
    (0.62, 0.01, 0.78, 0.60),
    (0.88, 0.00, 0.87, 0.65),
    (1.14, -0.02, 0.91, 0.68),
    (1.38, -0.02, 0.89, 0.67),
    (1.60, 0.00, 0.85, 0.64),
    (1.80, 0.03, 0.81, 0.60),
    (1.98, 0.04, 0.76, 0.56),
    (2.13, 0.03, 0.70, 0.52),
    (2.26, 0.00, 0.72, 0.53),
    (2.38, -0.05, 0.83, 0.60),
    (2.53, -0.10, 0.95, 0.69),
    (2.72, -0.14, 1.03, 0.75),
    (2.94, -0.14, 1.04, 0.76),
    (3.15, -0.10, 0.99, 0.71),
    (3.33, -0.05, 0.88, 0.62),
    (3.48, 0.00, 0.71, 0.50),
    (3.59, 0.02, 0.46, 0.33),
    (3.65, 0.02, 0.20, 0.14),
]
body = loft_z("Capibara_Unified_Core_Cage", core_sections, 56, MAT_FUR, 2)'''
text = text[:start] + core + text[end:]

# Less spherical cheek cluster. The central muzzle is broad and flat, while
# cheek masses sit to each side and blend into the jaw.
cluster = {
    '(0, -0.790, 2.900), (0.62, 0.335, 0.325)': '(0, -0.745, 2.875), (0.55, 0.245, 0.275)',
    '(-0.36, -0.625, 2.885), (0.44, 0.300, 0.320)': '(-0.31, -0.655, 2.835), (0.39, 0.275, 0.280)',
    '(0.36, -0.625, 2.885), (0.44, 0.300, 0.320)': '(0.31, -0.655, 2.835), (0.39, 0.275, 0.280)',
    '(0, -0.635, 2.650), (0.47, 0.270, 0.245)': '(0, -0.635, 2.655), (0.42, 0.245, 0.220)',
}
for old, new in cluster.items():
    if old not in text:
        raise RuntimeError(f'V10 face mass target not found: {old}')
    text = text.replace(old, new, 1)

# Add two nearly flush warm cheek/muzzle colour zones after the fused mesh.
anchor = '''for poly in sculpt_master.data.polygons:
    center = sum((sculpt_master.data.vertices[i].co for i in poly.vertices), Vector()) / max(1, len(poly.vertices))
    if center.y < -0.77 and 2.58 < center.z < 3.15:
        poly.material_index = 1'''
if anchor not in text:
    raise RuntimeError('V10 material assignment anchor not found')
patches = anchor + '''
uv("Muzzle_Patch_L", (-0.255, -1.005, 2.830), (0.320, 0.010, 0.205), MAT_FUR_LIGHT, 44, 28,
   rot=(math.radians(2), math.radians(-5), math.radians(-3)))
uv("Muzzle_Patch_R", (0.255, -1.005, 2.830), (0.320, 0.010, 0.205), MAT_FUR_LIGHT, 44, 28,
   rot=(math.radians(2), math.radians(5), math.radians(3)))'''
text = text.replace(anchor, patches, 1)

# Reference facial proportions: large glossy eyes, modest oval nose, broad flat
# mouth cavity, small incisors and only a hint of tongue.
face = {
    'x = 0.49 * sx': 'x = 0.485 * sx',
    '(x, -0.785, 3.045), (0.168, 0.088, 0.198)': '(x, -0.795, 3.035), (0.176, 0.092, 0.205)',
    '(x - 0.040 * sx, -0.875, 3.120), (0.039, 0.008, 0.047)': '(x - 0.042 * sx, -0.889, 3.113), (0.041, 0.008, 0.049)',
    '(x + 0.041 * sx, -0.878, 2.985), (0.014, 0.005, 0.017)': '(x + 0.042 * sx, -0.892, 2.972), (0.014, 0.005, 0.017)',
    '(0, -1.180, 2.905), (0.285, 0.075, 0.130)': '(0, -1.075, 2.905), (0.225, 0.048, 0.102)',
    '(0.105 * sx, -1.250, 2.920)': '(0.082 * sx, -1.123, 2.916)',
    '(0, -1.135, 2.615), (0.275, 0.030, 0.175)': '(0, -1.066, 2.650), (0.300, 0.014, 0.155)',
    '(0, -1.165, 2.530), (0.067, 0.008, 0.024)': '(0, -1.083, 2.568), (0.065, 0.007, 0.022)',
    '(0.050 * sx, -1.155, 2.720), (0.031, 0.010, 0.043)': '(0.052 * sx, -1.084, 2.747), (0.037, 0.010, 0.052)',
}
for old, new in face.items():
    if old not in text:
        raise RuntimeError(f'V10 feature target not found: {old}')
    text = text.replace(old, new, 1)

# Teeth are warmer and slightly wider at the top; the mouth remains the main
# smile shape rather than a protruding red oval.
text = text.replace('(0.93, 0.82, 0.59, 1), 0.72', '(0.88, 0.76, 0.55, 1), 0.70', 1)

# Fingers use warm fur; only tiny nail pads stay dark.
text = text.replace('(0.046, 0.038, 0.125), MAT_FUR_DARK, 28, 18',
                    '(0.046, 0.038, 0.125), MAT_FUR, 28, 18', 1)
text = text.replace('(0.055, 0.044, 0.105), MAT_FUR_DARK, 28, 18',
                    '(0.055, 0.044, 0.105), MAT_FUR, 28, 18', 1)

# Reduce the hat brim and rotate it to frame the eyes like the original.
text = text.replace('0.92, 0.075, MAT_HAT, 72, rot=(math.radians(2), math.radians(-4), math.radians(-2)), scale=(1.05, 0.83, 1)',
                    '0.88, 0.070, MAT_HAT, 72, rot=(math.radians(3), math.radians(-5), math.radians(-2)), scale=(1.05, 0.82, 1)', 1)

path.write_text(text, encoding='utf-8')
print('CAPIBARA_V10_REFERENCE_FACE_ANATOMY_OK', path)
