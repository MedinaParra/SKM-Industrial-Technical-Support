from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "capibara-alpha-source/create_capybara_v4_clean_surface.py")
text = path.read_text(encoding="utf-8")
text = text.replace('VERSION = "7.0.0-unified-character-core"', 'VERSION = "8.0.0-hero-proportions"', 1)

# Darker, warmer coat closer to the supplied hero character.
text = text.replace(
    'apply_fur_shader(MAT_FUR, (0.145, 0.050, 0.016, 1), (0.315, 0.135, 0.052, 1))',
    'apply_fur_shader(MAT_FUR, (0.095, 0.026, 0.007, 1), (0.245, 0.090, 0.028, 1))', 1)
text = text.replace(
    'apply_fur_shader(MAT_FUR_LIGHT, (0.205, 0.085, 0.032, 1), (0.365, 0.175, 0.075, 1))',
    'apply_fur_shader(MAT_FUR_LIGHT, (0.145, 0.050, 0.016, 1), (0.290, 0.120, 0.045, 1))', 1)

# Short body, dominant head, narrow shoulder transition. This follows the
# visual ratio in the supplied menu screenshot instead of a natural otter body.
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
    (2.13, 0.03, 0.68, 0.51),
    (2.26, 0.00, 0.70, 0.52),
    (2.38, -0.04, 0.82, 0.59),
    (2.53, -0.08, 0.96, 0.68),
    (2.72, -0.11, 1.07, 0.75),
    (2.94, -0.11, 1.10, 0.77),
    (3.15, -0.08, 1.06, 0.73),
    (3.33, -0.04, 0.94, 0.64),
    (3.48, 0.00, 0.76, 0.52),
    (3.59, 0.02, 0.50, 0.35),
    (3.65, 0.02, 0.23, 0.16),
]
body = loft_z("Capibara_Unified_Core_Cage", core_sections, 56, MAT_FUR, 2)'''
text = text[:start] + core + text[end:]

# Replace one blunt muzzle with a sculpt cluster: broad muzzle, two cheek masses
# and lower jaw. All become one voxel-remeshed surface.
old = '''muzzle_core = uv("Muzzle_Core", (0, -0.765, 3.075), (0.60, 0.285, 0.285), MAT_FUR, 56, 34)
sculpt_master = fuse_sculpt_master("Capibara_Sculpt_Master", [body, muzzle_core], 0.024)'''
new = '''muzzle_core = uv("Muzzle_Core", (0, -0.700, 2.900), (0.60, 0.305, 0.315), MAT_FUR, 56, 34)
cheek_core_l = uv("Cheek_Core_L", (-0.36, -0.555, 2.890), (0.43, 0.285, 0.315), MAT_FUR, 48, 30)
cheek_core_r = uv("Cheek_Core_R", (0.36, -0.555, 2.890), (0.43, 0.285, 0.315), MAT_FUR, 48, 30)
lower_jaw_core = uv("Lower_Jaw_Core", (0, -0.555, 2.660), (0.45, 0.245, 0.230), MAT_FUR, 48, 30)
sculpt_master = fuse_sculpt_master("Capibara_Sculpt_Master", [body, muzzle_core, cheek_core_l, cheek_core_r, lower_jaw_core], 0.024)'''
if old not in text:
    raise RuntimeError('V8 muzzle cluster target not found')
text = text.replace(old, new, 1)
text = text.replace('smooth.factor = 0.30', 'smooth.factor = 0.24', 1)
text = text.replace('smooth.iterations = 10', 'smooth.iterations = 8', 1)

# Face follows the lower, larger head. Eyes remain lateral and glossy.
face = {
    'x = 0.49 * sx': 'x = 0.50 * sx',
    '(x, -0.765, 3.365), (0.150, 0.078, 0.182)': '(x, -0.735, 3.045), (0.150, 0.080, 0.182)',
    '(x - 0.036 * sx, -0.845, 3.430), (0.034, 0.007, 0.041)': '(x - 0.036 * sx, -0.817, 3.112), (0.034, 0.007, 0.041)',
    '(x + 0.036 * sx, -0.848, 3.315), (0.012, 0.004, 0.015)': '(x + 0.036 * sx, -0.820, 2.998), (0.012, 0.004, 0.015)',
    '(0, -1.065, 3.105), (0.255, 0.055, 0.115)': '(0, -1.020, 2.875), (0.250, 0.055, 0.112)',
    '(0.092 * sx, -1.120, 3.115)': '(0.090 * sx, -1.076, 2.886)',
    '(0, -1.035, 2.905), (0.245, 0.024, 0.158)': '(0, -0.995, 2.630), (0.255, 0.025, 0.165)',
    '(0, -1.065, 2.835), (0.080, 0.009, 0.030)': '(0, -1.025, 2.555), (0.072, 0.008, 0.026)',
    '(0.050 * sx, -1.060, 2.985), (0.034, 0.011, 0.048)': '(0.050 * sx, -1.018, 2.720), (0.032, 0.010, 0.045)',
}
for old_value, new_value in face.items():
    if old_value not in text:
        raise RuntimeError(f'V8 face target not found: {old_value}')
    text = text.replace(old_value, new_value, 1)

# Ears and hat move down with the cranium.
placements = {
    '(0.78 * sx, 0.05, 3.72)': '(0.78 * sx, 0.05, 3.39)',
    '(0.785 * sx, -0.022, 3.72)': '(0.785 * sx, -0.022, 3.39)',
    '(0, 0.00, 3.91)': '(0, 0.00, 3.57)',
    '(3.86, 0.02, 0.64, 0.48)': '(3.59, 0.02, 0.64, 0.48)',
    '(4.00, 0.04, 0.62, 0.46)': '(3.73, 0.04, 0.62, 0.46)',
    '(4.18, 0.06, 0.54, 0.40)': '(3.91, 0.06, 0.54, 0.40)',
    '(4.27, 0.07, 0.40, 0.30)': '(4.00, 0.07, 0.40, 0.30)',
    '(0, 0.01, 3.94)': '(0, 0.01, 3.67)',
}
for old_value, new_value in placements.items():
    if old_value not in text:
        raise RuntimeError(f'V8 placement target not found: {old_value}')
    text = text.replace(old_value, new_value, 1)

# Compact hero pose and accessories.
pose = {
    '[(-0.60, -0.01, 1.98), (-0.79, -0.12, 2.24), (-0.91, -0.20, 2.52)]': '[(-0.60, -0.01, 1.72), (-0.79, -0.12, 1.98), (-0.91, -0.20, 2.24)]',
    '(-0.95, -0.23, 2.66)': '(-0.95, -0.23, 2.38)',
    '2.835 + (0.015 if i in (1, 2) else 0.0)': '2.555 + (0.015 if i in (1, 2) else 0.0)',
    '(-0.785, -0.255, 2.640)': '(-0.785, -0.255, 2.360)',
    '[(0.61, -0.01, 1.94), (0.71, -0.10, 1.63), (0.67, -0.22, 1.36)]': '[(0.61, -0.01, 1.70), (0.71, -0.10, 1.42), (0.67, -0.22, 1.18)]',
    '(0.66, -0.24, 1.27)': '(0.66, -0.24, 1.08)',
    '(0, 0.61, 1.36)': '(0, 0.58, 1.18)',
    '(0, 0.80, 1.23)': '(0, 0.77, 1.06)',
    '(0.39 * sx, -0.01, 1.72)': '(0.39 * sx, -0.01, 1.52)',
    '(0, -0.69, 1.36)': '(0, -0.67, 1.16)',
    '(0, -0.705, 1.515)': '(0, -0.685, 1.315)',
    '(-0.15, -0.805, 1.570)': '(-0.15, -0.785, 1.370)',
    '(0, -0.855, 1.36)': '(0, -0.835, 1.16)',
    '(0, -0.955, 1.36)': '(0, -0.935, 1.16)',
    '(0, -0.04, 1.86)': '(0, -0.04, 1.64)',
}
for old_value, new_value in pose.items():
    if old_value not in text:
        raise RuntimeError(f'V8 pose target not found: {old_value}')
    text = text.replace(old_value, new_value, 1)

# Reframe around the shorter character.
text = text.replace('(0, -7.65, 3.05), (0, -0.10, 2.13), 66',
                    '(0, -7.05, 2.78), (0, -0.08, 1.88), 67', 1)
text = text.replace('(8.0, -0.1, 3.00), (0, 0, 2.05), 65',
                    '(7.35, -0.1, 2.78), (0, 0, 1.88), 67', 1)
text = text.replace('(4.65, -7.35, 3.18), (0, -0.10, 2.05), 64',
                    '(4.35, -6.65, 2.90), (0, -0.08, 1.88), 66', 1)

path.write_text(text, encoding='utf-8')
print('CAPIBARA_V8_HERO_PROPORTIONS_OK', path)
