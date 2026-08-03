from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "capibara-alpha-source/create_capybara_v4_clean_surface.py")
text = path.read_text(encoding="utf-8")
text = text.replace('VERSION = "11.0.0-integrated-face"', 'VERSION = "12.0.0-hero-likeness"', 1)

# Broader compact torso like the supplied hero, without increasing height.
start = text.index('core_sections = [')
end_marker = 'body = loft_z("Capibara_Unified_Core_Cage", core_sections, 56, MAT_FUR, 2)'
end = text.index(end_marker, start) + len(end_marker)
core = '''core_sections = [
    (0.24, 0.02, 0.36, 0.37),
    (0.38, 0.00, 0.61, 0.52),
    (0.62, 0.01, 0.82, 0.62),
    (0.88, 0.00, 0.92, 0.68),
    (1.14, -0.02, 0.96, 0.71),
    (1.38, -0.02, 0.94, 0.70),
    (1.60, 0.00, 0.90, 0.67),
    (1.80, 0.03, 0.85, 0.63),
    (1.98, 0.04, 0.79, 0.59),
    (2.13, 0.03, 0.72, 0.54),
    (2.26, 0.00, 0.72, 0.53),
    (2.38, -0.05, 0.82, 0.59),
    (2.53, -0.10, 0.94, 0.68),
    (2.72, -0.14, 1.02, 0.74),
    (2.94, -0.14, 1.03, 0.75),
    (3.15, -0.10, 0.98, 0.70),
    (3.33, -0.05, 0.87, 0.61),
    (3.48, 0.00, 0.70, 0.49),
    (3.59, 0.02, 0.45, 0.32),
    (3.65, 0.02, 0.20, 0.14),
]
body = loft_z("Capibara_Unified_Core_Cage", core_sections, 56, MAT_FUR, 2)'''
text = text[:start] + core + text[end:]

# Eye placement is lateral and slightly rearward. In three-quarter view the
# near eye dominates while the far eye recedes, matching the original render.
face = {
    'x = 0.485 * sx': 'x = 0.565 * sx',
    '(x, -0.795, 3.035), (0.170, 0.090, 0.190)': '(x, -0.685, 3.030), (0.158, 0.085, 0.188)',
    '(x - 0.040 * sx, -0.887, 3.105), (0.033, 0.007, 0.040)': '(x - 0.037 * sx, -0.773, 3.103), (0.031, 0.007, 0.038)',
    '(x + 0.040 * sx, -0.890, 2.980), (0.010, 0.004, 0.012)': '(x + 0.037 * sx, -0.776, 2.978), (0.009, 0.004, 0.011)',
    '(0, -1.075, 2.905), (0.245, 0.052, 0.100)': '(0, -1.060, 2.890), (0.215, 0.047, 0.095)',
    '(0.090 * sx, -1.128, 2.916)': '(0.078 * sx, -1.110, 2.900)',
}
for old, new in face.items():
    if old not in text:
        raise RuntimeError(f'V12 facial target not found: {old}')
    text = text.replace(old, new, 1)

# Deeper and wider smile cavity, lower on the muzzle. Keep the interior inset.
text = text.replace('(0, -0.975, 2.650), (0.300, 0.230, 0.168)',
                    '(0, -0.965, 2.625), (0.325, 0.235, 0.185)', 1)
text = text.replace('(0, -0.965, 2.645), (0.280, 0.018, 0.145)',
                    '(0, -0.970, 2.620), (0.305, 0.020, 0.162)', 1)
text = text.replace('(0, -0.994, 2.575), (0.075, 0.010, 0.025)',
                    '(0, -0.998, 2.545), (0.075, 0.010, 0.025)', 1)
text = text.replace('(0.052 * sx, -0.998, 2.742), (0.039, 0.012, 0.056)',
                    '(0.050 * sx, -1.000, 2.724), (0.035, 0.011, 0.052)', 1)

# Soften the muzzle transition by reducing the cheek bulbs and moving them
# closer to the central muzzle.
cluster = {
    '(0, -0.745, 2.875), (0.55, 0.245, 0.275)': '(0, -0.745, 2.870), (0.54, 0.250, 0.270)',
    '(-0.31, -0.655, 2.835), (0.39, 0.275, 0.280)': '(-0.27, -0.650, 2.825), (0.36, 0.260, 0.270)',
    '(0.31, -0.655, 2.835), (0.39, 0.275, 0.280)': '(0.27, -0.650, 2.825), (0.36, 0.260, 0.270)',
}
for old, new in cluster.items():
    if old not in text:
        raise RuntimeError(f'V12 cheek target not found: {old}')
    text = text.replace(old, new, 1)

# Larger, warmer waving hand brought forward toward the camera.
text = text.replace('(-0.98, -0.35, 2.38), (0.225, 0.170, 0.225)',
                    '(-1.00, -0.44, 2.38), (0.245, 0.190, 0.245)', 1)
text = text.replace('(x, -0.410, 2.555 +', '(x, -0.510, 2.555 +', 1)
text = text.replace('(-0.790, -0.405, 2.360)', '(-0.800, -0.505, 2.360)', 1)

# Feet are smaller and less shoe-like.
text = text.replace('(0.285, 0.365, 0.185)', '(0.260, 0.330, 0.175)', 1)

# Warmer explorer hat materials, closer to olive cloth rather than plastic.
text = text.replace('MAT_HAT = material("Explorer olive", (0.25, 0.26, 0.10, 1), 0.86)',
                    'MAT_HAT = material("Explorer olive", (0.21, 0.22, 0.075, 1), 0.92)', 1)
text = text.replace('MAT_HAT_LIGHT = material("Explorer olive light", (0.39, 0.39, 0.16, 1), 0.84)',
                    'MAT_HAT_LIGHT = material("Explorer olive light", (0.32, 0.33, 0.12, 1), 0.90)', 1)

# Stronger three-quarter angle for the approval render.
text = text.replace('(4.05, -6.30, 2.82), (0, -0.16, 1.92), 68',
                    '(4.85, -6.10, 2.80), (0, -0.15, 1.92), 68', 1)

path.write_text(text, encoding='utf-8')
print('CAPIBARA_V12_HERO_LIKENESS_OK', path)
