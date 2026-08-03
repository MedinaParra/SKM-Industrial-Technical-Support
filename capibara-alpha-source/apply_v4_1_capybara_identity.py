from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "capibara-alpha-source/create_capybara_v4_clean_surface.py")
text = path.read_text(encoding="utf-8")

text = text.replace('VERSION = "4.0.0-clean-surface"', 'VERSION = "4.1.0-capybara-identity"', 1)

# A rounded superellipse produces the characteristic broad, blocky capybara
# cranium instead of another spherical hamster/bear head.
old = '            verts.append((rx * math.cos(a), y, cz + rz * math.sin(a)))'
new = '''            c = math.cos(a)
            s = math.sin(a)
            px = math.copysign(abs(c) ** 0.62, c)
            pz = math.copysign(abs(s) ** 0.74, s)
            verts.append((rx * px, y, cz + rz * pz))'''
if old not in text:
    raise RuntimeError("loft_y coordinate target not found")
text = text.replace(old, new, 1)

# Warmer, deeper fur; the previous pale orange made the character read as a
# plastic hamster even when the silhouette improved.
text = text.replace('(0.36, 0.145, 0.050, 1), 0.88', '(0.255, 0.085, 0.025, 1), 0.90', 1)
text = text.replace('(0.50, 0.245, 0.095, 1), 0.90', '(0.355, 0.145, 0.050, 1), 0.92', 1)
text = text.replace('(0.19, 0.070, 0.025, 1), 0.92', '(0.135, 0.043, 0.015, 1), 0.94', 1)
text = text.replace('(0.25, 0.26, 0.10, 1), 0.86', '(0.16, 0.19, 0.055, 1), 0.88', 1)
text = text.replace('(0.39, 0.39, 0.16, 1), 0.84', '(0.27, 0.30, 0.095, 1), 0.86', 1)

body_start = text.index('body_sections = [')
body_end = text.index('body = loft_z("Body_Clean", body_sections, 48, MAT_FUR, 2)', body_start)
body_end += len('body = loft_z("Body_Clean", body_sections, 48, MAT_FUR, 2)')
body_block = '''body_sections = [
    (0.24, 0.02, 0.34, 0.36),
    (0.38, 0.00, 0.60, 0.52),
    (0.68, 0.02, 0.82, 0.63),
    (1.02, 0.01, 0.94, 0.69),
    (1.36, -0.02, 0.97, 0.71),
    (1.68, -0.03, 0.91, 0.67),
    (1.98, 0.00, 0.83, 0.62),
    (2.24, 0.03, 0.77, 0.58),
    (2.48, 0.05, 0.72, 0.54),
    (2.70, 0.07, 0.68, 0.51),
    (2.84, 0.08, 0.58, 0.44),
]
body = loft_z("Body_Clean", body_sections, 48, MAT_FUR, 2)'''
text = text[:body_start] + body_block + text[body_end:]

head_start = text.index('head_sections = [', body_start)
head_end = text.index('head = loft_y("Head_Clean", head_sections, 56, MAT_FUR, 2)', head_start)
head_end += len('head = loft_y("Head_Clean", head_sections, 56, MAT_FUR, 2)')
head_block = '''head_sections = [
    (0.72, 3.38, 0.28, 0.27),
    (0.58, 3.42, 0.70, 0.50),
    (0.34, 3.44, 0.98, 0.63),
    (0.08, 3.44, 1.08, 0.69),
    (-0.18, 3.41, 1.08, 0.68),
    (-0.42, 3.35, 1.00, 0.60),
    (-0.62, 3.27, 0.91, 0.51),
    (-0.79, 3.19, 0.80, 0.42),
    (-0.94, 3.13, 0.67, 0.33),
    (-1.07, 3.12, 0.49, 0.23),
    (-1.14, 3.14, 0.25, 0.13),
]
head = loft_y("Head_Clean", head_sections, 56, MAT_FUR, 2)'''
text = text[:head_start] + head_block + text[head_end:]

# Subtle broad muzzle, not a pale circular hamster patch.
text = text.replace('(0, -1.045, 3.10), (0.50, 0.018, 0.205)',
                    '(0, -1.125, 3.135), (0.55, 0.012, 0.190)', 1)

# Ears high and small.
text = text.replace('(0.78 * sx, 0.02, 3.91), (0.18, 0.10, 0.18)',
                    '(0.80 * sx, 0.04, 3.93), (0.155, 0.085, 0.155)', 1)
text = text.replace('(0.785 * sx, -0.078, 3.91), (0.095, 0.018, 0.095)',
                    '(0.805 * sx, -0.043, 3.93), (0.078, 0.014, 0.078)', 1)

# Smaller, wider-set eyes restore the capybara identity while retaining charm.
text = text.replace('x = 0.47 * sx', 'x = 0.53 * sx', 1)
text = text.replace('(x, -0.765, 3.52), (0.18, 0.105, 0.215)',
                    '(x, -0.790, 3.53), (0.145, 0.082, 0.175)', 1)
text = text.replace('(x - 0.045 * sx, -0.872, 3.595), (0.043, 0.010, 0.052)',
                    '(x - 0.036 * sx, -0.874, 3.590), (0.034, 0.008, 0.041)', 1)
text = text.replace('(x + 0.047 * sx, -0.875, 3.465), (0.016, 0.007, 0.019)',
                    '(x + 0.038 * sx, -0.877, 3.485), (0.013, 0.005, 0.016)', 1)

# A broad flat nose, short smile and restrained incisors.
text = text.replace('(0, -1.115, 3.19), (0.30, 0.075, 0.145)',
                    '(0, -1.205, 3.205), (0.325, 0.073, 0.135)', 1)
text = text.replace('(0.108 * sx, -1.189, 3.205)', '(0.118 * sx, -1.277, 3.216)', 1)
text = text.replace('(0, -1.085, 2.98), (0.215, 0.020, 0.118)',
                    '(0, -1.172, 3.005), (0.205, 0.016, 0.098)', 1)
text = text.replace('(0, -1.110, 2.945), (0.12, 0.012, 0.045)',
                    '(0, -1.190, 2.980), (0.105, 0.009, 0.037)', 1)
text = text.replace('(0.065 * sx, -1.108, 3.04), (0.050, 0.018, 0.073)',
                    '(0.060 * sx, -1.192, 3.060), (0.043, 0.014, 0.060)', 1)

# Shorter arms match the compact torso; keep the wave readable.
text = text.replace('[(-0.64, -0.02, 2.26), (-0.82, -0.13, 2.48), (-0.94, -0.22, 2.76)]',
                    '[(-0.65, -0.02, 2.18), (-0.82, -0.13, 2.40), (-0.94, -0.22, 2.68)]', 1)
text = text.replace('(-0.98, -0.25, 2.93)', '(-0.98, -0.25, 2.85)', 1)
text = text.replace('(x, -0.28, 3.14)', '(x, -0.28, 3.06)', 1)
text = text.replace('[(0.68, -0.01, 2.22), (0.79, -0.10, 1.90), (0.73, -0.23, 1.62)]',
                    '[(0.67, -0.01, 2.14), (0.78, -0.10, 1.82), (0.72, -0.23, 1.55)]', 1)
text = text.replace('(0.72, -0.25, 1.52)', '(0.71, -0.25, 1.45)', 1)

# Hat follows the flatter skull without hiding the eyes.
text = text.replace('(0, 0.00, 4.08)', '(0, 0.00, 4.10)', 1)
text = text.replace('(4.10, 0.02, 0.70, 0.54)', '(4.12, 0.02, 0.70, 0.54)', 1)
text = text.replace('(4.24, 0.04, 0.68, 0.52)', '(4.26, 0.04, 0.68, 0.52)', 1)
text = text.replace('(4.42, 0.06, 0.58, 0.44)', '(4.44, 0.06, 0.58, 0.44)', 1)
text = text.replace('(4.51, 0.07, 0.43, 0.34)', '(4.53, 0.07, 0.43, 0.34)', 1)
text = text.replace('(0, 0.01, 4.18)', '(0, 0.01, 4.20)', 1)

path.write_text(text, encoding="utf-8")
print("CAPIBARA_V4_1_CAPYBARA_IDENTITY_OK", path)
