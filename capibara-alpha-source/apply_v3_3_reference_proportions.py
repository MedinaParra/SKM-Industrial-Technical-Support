from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "capibara-alpha-source/create_capybara_v3.py")
text = path.read_text(encoding="utf-8")
text = text.replace('VERSION = "3.2.0-face-simplification"', 'VERSION = "3.3.0-reference-proportions"')

# Compact torso, narrower than the head, with a high neck mass to remove the
# detached bobble-head seam.
start = text.index('body_pieces = [')
end_marker = 'body = union_voxel("Body", body_pieces, 0.052, MAT_FUR, 3)'
end = text.index(end_marker, start) + len(end_marker)
text = text[:start] + '''body_pieces = [
    add_uv("Body_Lower_Block", (0, 0.06, 1.18), (0.94, 0.70, 0.94), None, 48, 32),
    add_uv("Body_Belly_Block", (0, -0.06, 1.52), (0.98, 0.72, 0.83), None, 48, 32),
    add_uv("Body_Chest_Block", (0, -0.02, 2.02), (0.86, 0.64, 0.65), None, 48, 32),
    add_uv("Body_Shoulder_Block", (0, 0.02, 2.39), (0.80, 0.59, 0.48), None, 48, 32),
    add_uv("Body_Neck_Block", (0, 0.04, 2.67), (0.72, 0.55, 0.34), None, 44, 28),
]
body = union_voxel("Body", body_pieces, 0.050, MAT_FUR, 3)''' + text[end:]

# A smooth but slightly elongated capybara skull. The muzzle projects enough to
# read in profile without returning to the old stack-of-balls look.
start = text.index('head_pieces = [', start)
end_marker = '               rot=(math.radians(2), 0, 0))'
end = text.index(end_marker, start) + len(end_marker)
text = text[:start] + '''head_pieces = [
    add_uv("Head_Cranium_Block", (0, 0.08, 3.43), (1.03, 0.78, 0.74), None, 56, 36),
    add_uv("Head_Forehead_Block", (0, -0.16, 3.68), (0.90, 0.65, 0.42), None, 52, 34),
    add_uv("Head_Midface_Block", (0, -0.42, 3.30), (0.85, 0.54, 0.48), None, 56, 36),
    add_uv("Head_SnoutBridge_Block", (0, -0.68, 3.20), (0.74, 0.40, 0.34), None, 52, 34),
    add_uv("Head_Muzzle_Block", (0, -0.78, 3.07), (0.64, 0.31, 0.27), None, 48, 32),
]
head = union_voxel("Head", head_pieces, 0.038, MAT_FUR, 4)

# Flush tonal muzzle; no cream moustache disk in the sculpt review.
snout = add_uv("Snout", (0, -1.095, 3.125), (0.50, 0.008, 0.195), MAT_FUR, 48, 30,
               rot=(math.radians(2), 0, 0))''' + text[end:]

# Eyes are still expressive, but no longer dominate the whole face.
text = text.replace('(x, -0.735, 3.58), (0.225, 0.118, 0.255)',
                    '(x, -0.785, 3.53), (0.185, 0.105, 0.220)', 1)
text = text.replace('(x - 0.058 * sx, -0.857, 3.670),\n           (0.055, 0.010, 0.067)',
                    '(x - 0.048 * sx, -0.893, 3.605),\n           (0.045, 0.009, 0.054)', 1)
text = text.replace('(x + 0.055 * sx, -0.859, 3.515),\n           (0.020, 0.007, 0.024)',
                    '(x + 0.047 * sx, -0.895, 3.475),\n           (0.017, 0.006, 0.020)', 1)

# Nose and smile follow the slightly longer muzzle.
text = text.replace('nose = add_uv("Nose", (0, -1.045, 3.235), (0.285, 0.075, 0.140)',
                    'nose = add_uv("Nose", (0, -1.125, 3.205), (0.300, 0.078, 0.145)', 1)
text = text.replace('(0.105 * sx, -1.125, 3.245)', '(0.108 * sx, -1.207, 3.218)', 1)
text = text.replace('mouth = add_uv("Mouth", (0, -1.000, 3.015), (0.195, 0.012, 0.085)',
                    'mouth = add_uv("Mouth", (0, -1.096, 2.995), (0.215, 0.018, 0.112)', 1)
text = text.replace('tongue = add_uv("Tongue", (0, -1.014, 2.985)',
                    'tongue = add_uv("Tongue", (0, -1.115, 2.965)', 1)
text = text.replace('(0.065 * sx, -1.018, 3.065), (0.050, 0.016, 0.068)',
                    '(0.067 * sx, -1.116, 3.055), (0.052, 0.018, 0.074)', 1)

# Asymmetric explorer pose: left arm waves beside the face; right arm rests.
arm_start = text.index('left_arm = soft_limb(')
arm_end = text.index('\n\n# Feet are short', arm_start)
arm_block = '''left_arm = soft_limb("Arm_L", [(-0.70, 0.00, 2.18), (-0.91, -0.10, 2.45), (-1.00, -0.22, 2.72)],
                     [(0.27, 0.25, 0.32), (0.24, 0.22, 0.29), (0.22, 0.19, 0.22)], MAT_FUR, 0.042)
right_arm = soft_limb("Arm_R", [(0.72, 0.00, 2.12), (0.80, -0.10, 1.78), (0.72, -0.22, 1.48)],
                      [(0.27, 0.25, 0.33), (0.24, 0.22, 0.30), (0.23, 0.20, 0.22)], MAT_FUR, 0.042)
wave_hand = add_uv("Wave_Hand", (-1.03, -0.27, 2.90), (0.25, 0.17, 0.25), MAT_FUR_DARK, 44, 28,
                   rot=(math.radians(-8), math.radians(-8), math.radians(-10)))
for finger in range(3):
    fx = -1.19 + finger * 0.15
    add_uv(f"Wave_Finger_{finger}", (fx, -0.305, 3.12), (0.070, 0.055, 0.17), MAT_FUR_DARK, 32, 20,
           rot=(math.radians(-8), math.radians(-5), math.radians((finger - 1) * 8)))
'''
text = text[:arm_start] + arm_block + text[arm_end:]

# Existing tiny finger-pad loop belongs only to the resting hand and is hidden.
text = text.replace('    # fingers are subtle dark pads, not claws.\n    for finger in range(3):\n        fx = 0.72 * sx + (finger - 1) * 0.07\n        add_uv(f"Finger_{side}_{finger}", (fx, -0.31, 1.48), (0.018, 0.010, 0.015), MAT_FUR_DARK, 20, 12)\n', '')

# Smaller feet and a camera that hangs like the reference rather than a belly button.
text = text.replace('(0.41 * sx, -0.15, 0.30), (0.34, 0.44, 0.22)',
                    '(0.38 * sx, -0.14, 0.28), (0.31, 0.40, 0.20)', 1)
text = text.replace('add_cube("Camera_Body", (0, -0.76, 1.70), (0.31, 0.12, 0.22)',
                    'add_cube("Camera_Body", (0, -0.73, 1.76), (0.29, 0.11, 0.21)', 1)
text = text.replace('add_cylinder("Camera_Lens", (0, -0.92, 1.70)',
                    'add_cylinder("Camera_Lens", (0, -0.88, 1.76)', 1)
text = text.replace('add_cylinder("Camera_Glass", (0, -1.015, 1.70)',
                    'add_cylinder("Camera_Glass", (0, -0.975, 1.76)', 1)

text = text.replace('"art_status": "V3.2 simplified capybara face candidate; visual approval required"',
                    '"art_status": "V3.3 reference proportions + waving explorer pose candidate"')
path.write_text(text, encoding="utf-8")
print("CAPIBARA_V3_3_REFERENCE_PROPORTIONS_OK", path)
