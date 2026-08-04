from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "capibara-alpha-source/create_capybara_v4_clean_surface.py")
text = path.read_text(encoding="utf-8")
text = text.replace('VERSION = "6.0.0-reference-match"', 'VERSION = "7.0.0-unified-character-core"', 1)

# -----------------------------------------------------------------------------
# Build the torso, shoulders, neck and cranium as one continuous vertical loft.
# This removes the collar seam that survived every previous voxel fusion.
# -----------------------------------------------------------------------------
body_start = text.index('body_sections = [')
head_end_marker = 'head = loft_y("Head_Clean", head_sections, 56, MAT_FUR, 2)'
body_end = text.index(head_end_marker, body_start) + len(head_end_marker)
unified = '''core_sections = [
    (0.24, 0.02, 0.34, 0.36),
    (0.38, 0.00, 0.56, 0.49),
    (0.66, 0.01, 0.75, 0.59),
    (0.98, 0.00, 0.85, 0.65),
    (1.30, -0.02, 0.88, 0.67),
    (1.60, -0.02, 0.86, 0.66),
    (1.90, 0.00, 0.82, 0.63),
    (2.18, 0.03, 0.77, 0.59),
    (2.42, 0.04, 0.73, 0.56),
    (2.62, 0.02, 0.76, 0.57),
    (2.78, -0.03, 0.87, 0.63),
    (2.94, -0.08, 0.98, 0.70),
    (3.14, -0.10, 1.06, 0.75),
    (3.36, -0.09, 1.07, 0.75),
    (3.56, -0.06, 1.02, 0.70),
    (3.73, -0.02, 0.91, 0.61),
    (3.87, 0.01, 0.72, 0.49),
    (3.97, 0.02, 0.45, 0.31),
    (4.02, 0.02, 0.20, 0.14),
]
body = loft_z("Capibara_Unified_Core_Cage", core_sections, 56, MAT_FUR, 2)'''
text = text[:body_start] + unified + text[body_end:]

# Short, broad muzzle fused into the unified head. There is no separate neck.
replacements = {
    'muzzle_core = uv("Muzzle_Core", (0, -0.825, 3.015), (0.58, 0.205, 0.245), MAT_FUR, 56, 34)':
        'muzzle_core = uv("Muzzle_Core", (0, -0.765, 3.075), (0.60, 0.285, 0.285), MAT_FUR, 56, 34)',
    'neck_core = uv("Neck_Core", (0, 0.045, 2.650), (0.72, 0.56, 0.42), MAT_FUR, 52, 32)\n': '',
    'fuse_sculpt_master("Capibara_Sculpt_Master", [body, head, muzzle_core, neck_core], 0.025)':
        'fuse_sculpt_master("Capibara_Sculpt_Master", [body, muzzle_core], 0.024)',
    'uv("Muzzle_Tone", (0, -1.035, 3.015), (0.49, 0.010, 0.175), MAT_FUR_LIGHT, 52, 32)\n': '',
}
for old, new in replacements.items():
    if old not in text:
        raise RuntimeError(f'V7 core target not found: {old}')
    text = text.replace(old, new, 1)

# Increase polish enough to eliminate the last visible transition without
# flattening the muzzle and cheek silhouette.
text = text.replace('smooth.factor = 0.22', 'smooth.factor = 0.30', 1)
text = text.replace('smooth.iterations = 7', 'smooth.iterations = 10', 1)

# Remove the floating eyebrow-like upper lids. Posed eyelids are added later as
# true facial topology / blendshapes after the neutral face is approved.
lid_call = '''    uv(f"UpperLid_{side}", (x, -0.813, 3.455), (0.150, 0.010, 0.026), MAT_FUR_DARK, 42, 26,
       rot=(math.radians(-3), 0, math.radians(-3 * sx)))
'''
if lid_call not in text:
    raise RuntimeError('V7 lid target not found')
text = text.replace(lid_call, '', 1)

# Facial layout copied from the proportions of the supplied hero image: eyes
# sit laterally, nose is modest, the mouth cavity is broad and the tongue is a
# small lower accent rather than a pink capsule covering the smile.
face = {
    '(x, -0.735, 3.33), (0.142, 0.073, 0.174)': '(x, -0.765, 3.365), (0.150, 0.078, 0.182)',
    '(x - 0.034 * sx, -0.809, 3.392), (0.032, 0.007, 0.039)': '(x - 0.036 * sx, -0.845, 3.430), (0.034, 0.007, 0.041)',
    '(x + 0.035 * sx, -0.812, 3.282), (0.012, 0.004, 0.015)': '(x + 0.036 * sx, -0.848, 3.315), (0.012, 0.004, 0.015)',
    '(0, -1.085, 3.065), (0.245, 0.052, 0.108)': '(0, -1.065, 3.105), (0.255, 0.055, 0.115)',
    '(0.088 * sx, -1.137, 3.074)': '(0.092 * sx, -1.120, 3.115)',
    '(0, -1.055, 2.870), (0.225, 0.021, 0.132)': '(0, -1.035, 2.905), (0.245, 0.024, 0.158)',
    '(0, -1.077, 2.818), (0.105, 0.010, 0.038)': '(0, -1.065, 2.835), (0.080, 0.009, 0.030)',
    '(0.052 * sx, -1.078, 2.955), (0.037, 0.012, 0.054)': '(0.050 * sx, -1.060, 2.985), (0.034, 0.011, 0.048)',
}
for old, new in face.items():
    if old not in text:
        raise RuntimeError(f'V7 face target not found: {old}')
    text = text.replace(old, new, 1)

# Paws use body fur with only darker fingertips, matching the original.
text = text.replace('(0.205, 0.145, 0.205), MAT_FUR_DARK, 44, 28',
                    '(0.205, 0.145, 0.205), MAT_FUR, 44, 28', 1)
text = text.replace('(0.19, 0.145, 0.19), MAT_FUR_DARK, 40, 26',
                    '(0.19, 0.145, 0.19), MAT_FUR, 40, 26', 1)
text = text.replace('(0.285, 0.365, 0.185), MAT_FUR_DARK, 48, 30',
                    '(0.285, 0.365, 0.185), MAT_FUR, 48, 30', 1)

# Hat is slightly tilted and lowered like the reference explorer hat.
text = text.replace('cylinder("Hat_Brim", (0, 0.00, 3.84), 0.96, 0.085, MAT_HAT, 72, scale=(1.06, 0.84, 1), bevel=0.045)',
                    'cylinder("Hat_Brim", (0, 0.00, 3.91), 0.92, 0.075, MAT_HAT, 72, rot=(math.radians(2), math.radians(-4), math.radians(-2)), scale=(1.05, 0.83, 1), bevel=0.040)', 1)

# Slightly closer beauty framing for judging the neutral face.
text = text.replace('(0, -8.2, 3.00), (0, -0.08, 2.05), 65',
                    '(0, -7.65, 3.05), (0, -0.10, 2.13), 66', 1)

path.write_text(text, encoding='utf-8')
print('CAPIBARA_V7_UNIFIED_CHARACTER_CORE_OK', path)
