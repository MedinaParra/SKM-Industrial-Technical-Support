from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "capibara-alpha-source/create_capybara_v4_clean_surface.py")
text = path.read_text(encoding="utf-8")
text = text.replace('VERSION = "4.2.0-target-proportions-fur"', 'VERSION = "4.3.0-face-body-fur-refine"', 1)

# Softer rounded rectangle: retain capybara breadth without a flat slab face.
text = text.replace('px = math.copysign(abs(c) ** 0.62, c)',
                    'px = math.copysign(abs(c) ** 0.78, c)', 1)
text = text.replace('pz = math.copysign(abs(s) ** 0.74, s)',
                    'pz = math.copysign(abs(s) ** 0.84, s)', 1)

# Fine, low-contrast anisotropic-looking colour noise. The former broad noise
# looked like stains rather than short capybara fur.
shader_replacements = {
    'apply_fur_shader(MAT_FUR, (0.105, 0.028, 0.008, 1), (0.405, 0.155, 0.045, 1), 7.5, 90.0)':
        'apply_fur_shader(MAT_FUR, (0.135, 0.040, 0.010, 1), (0.335, 0.125, 0.036, 1), 34.0, 155.0)',
    'apply_fur_shader(MAT_FUR_LIGHT, (0.19, 0.055, 0.014, 1), (0.48, 0.205, 0.070, 1), 8.0, 96.0)':
        'apply_fur_shader(MAT_FUR_LIGHT, (0.205, 0.070, 0.018, 1), (0.405, 0.165, 0.052, 1), 38.0, 165.0)',
    'apply_fur_shader(MAT_FUR_DARK, (0.045, 0.010, 0.004, 1), (0.22, 0.065, 0.016, 1), 8.5, 92.0)':
        'apply_fur_shader(MAT_FUR_DARK, (0.050, 0.012, 0.004, 1), (0.165, 0.046, 0.012, 1), 36.0, 160.0)',
}
for old, new in shader_replacements.items():
    if old not in text:
        raise RuntimeError(f'fur call not found: {old}')
    text = text.replace(old, new, 1)
text = text.replace('bump.inputs["Strength"].default_value = 0.20',
                    'bump.inputs["Strength"].default_value = 0.11', 1)
text = text.replace('bump.inputs["Distance"].default_value = 0.035',
                    'bump.inputs["Distance"].default_value = 0.018', 1)

# Broader chest and shoulders rise into the head, eliminating the collar seam.
body_start = text.index('body_sections = [')
body_end_marker = 'body = loft_z("Body_Clean", body_sections, 48, MAT_FUR, 2)'
body_end = text.index(body_end_marker, body_start) + len(body_end_marker)
body_block = '''body_sections = [
    (0.24, 0.02, 0.35, 0.37),
    (0.38, 0.00, 0.63, 0.54),
    (0.66, 0.02, 0.88, 0.65),
    (0.98, 0.01, 1.00, 0.71),
    (1.30, -0.02, 1.04, 0.73),
    (1.60, -0.03, 1.00, 0.71),
    (1.88, 0.00, 0.94, 0.67),
    (2.14, 0.03, 0.88, 0.63),
    (2.38, 0.05, 0.82, 0.59),
    (2.60, 0.07, 0.76, 0.55),
    (2.78, 0.08, 0.69, 0.50),
    (2.92, 0.08, 0.58, 0.43),
]
body = loft_z("Body_Clean", body_sections, 48, MAT_FUR, 2)'''
text = text[:body_start] + body_block + text[body_end:]

# Slightly smaller, tapered head with fuller lower cheeks and a short broad
# muzzle. Its lower surface overlaps the raised shoulders naturally.
head_start = text.index('head_sections = [', body_start)
head_end_marker = 'uv("Neck_Bridge", (0, 0.03, 2.66), (0.72, 0.55, 0.34), MAT_FUR, 52, 32)'
head_end = text.index(head_end_marker, head_start) + len(head_end_marker)
head_block = '''head_sections = [
    (0.68, 3.25, 0.25, 0.24),
    (0.54, 3.29, 0.64, 0.46),
    (0.30, 3.31, 0.91, 0.60),
    (0.06, 3.30, 1.00, 0.66),
    (-0.18, 3.27, 1.00, 0.65),
    (-0.40, 3.21, 0.95, 0.59),
    (-0.59, 3.13, 0.89, 0.52),
    (-0.75, 3.05, 0.80, 0.43),
    (-0.89, 2.99, 0.69, 0.34),
    (-1.01, 2.98, 0.54, 0.25),
    (-1.09, 3.00, 0.33, 0.16),
    (-1.14, 3.02, 0.17, 0.09),
]
head = loft_y("Head_Clean", head_sections, 56, MAT_FUR, 2)'''
text = text[:head_start] + head_block + text[head_end:]

# Warm integrated muzzle, smaller nose and friendly but restrained smile.
face_replacements = {
    '(0, -1.125, 3.015), (0.55, 0.010, 0.185)': '(0, -1.112, 3.015), (0.48, 0.010, 0.175)',
    '(0.80 * sx, 0.04, 3.81), (0.155, 0.085, 0.155)': '(0.76 * sx, 0.05, 3.77), (0.145, 0.080, 0.145)',
    '(0.805 * sx, -0.043, 3.81), (0.078, 0.014, 0.078)': '(0.765 * sx, -0.030, 3.77), (0.070, 0.012, 0.070)',
    'x = 0.53 * sx': 'x = 0.47 * sx',
    '(x, -0.790, 3.41), (0.158, 0.088, 0.188)': '(x, -0.790, 3.36), (0.165, 0.092, 0.195)',
    '(x - 0.039 * sx, -0.880, 3.475), (0.037, 0.008, 0.044)': '(x - 0.041 * sx, -0.884, 3.430), (0.039, 0.008, 0.047)',
    '(x + 0.040 * sx, -0.882, 3.365), (0.014, 0.005, 0.017)': '(x + 0.041 * sx, -0.886, 3.310), (0.014, 0.005, 0.017)',
    '(0, -1.205, 3.085), (0.325, 0.073, 0.135)': '(0, -1.172, 3.070), (0.270, 0.065, 0.120)',
    '(0.118 * sx, -1.277, 3.096)': '(0.098 * sx, -1.237, 3.080)',
    '(0, -1.172, 2.885), (0.220, 0.018, 0.108)': '(0, -1.145, 2.875), (0.205, 0.017, 0.102)',
    '(0, -1.190, 2.855), (0.112, 0.010, 0.041)': '(0, -1.164, 2.845), (0.105, 0.009, 0.038)',
    '(0.060 * sx, -1.192, 2.940), (0.046, 0.015, 0.065)': '(0.056 * sx, -1.166, 2.930), (0.041, 0.014, 0.059)',
}
for old, new in face_replacements.items():
    if old not in text:
        raise RuntimeError(f'face replacement target not found: {old}')
    text = text.replace(old, new, 1)

# Hat follows the slightly lower crown.
hat_replacements = {
    '(0, 0.00, 3.98)': '(0, 0.00, 3.91)',
    '(4.00, 0.02, 0.70, 0.54)': '(3.93, 0.02, 0.68, 0.52)',
    '(4.14, 0.04, 0.68, 0.52)': '(4.07, 0.04, 0.66, 0.50)',
    '(4.32, 0.06, 0.58, 0.44)': '(4.25, 0.06, 0.57, 0.43)',
    '(4.41, 0.07, 0.43, 0.34)': '(4.34, 0.07, 0.42, 0.33)',
    '(0, 0.01, 4.08)': '(0, 0.01, 4.01)',
}
for old, new in hat_replacements.items():
    if old not in text:
        raise RuntimeError(f'hat target not found: {old}')
    text = text.replace(old, new, 1)

path.write_text(text, encoding='utf-8')
print('CAPIBARA_V4_3_FACE_BODY_FUR_REFINE_OK', path)
