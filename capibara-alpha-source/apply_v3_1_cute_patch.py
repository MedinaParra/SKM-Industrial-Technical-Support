from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "capibara-alpha-source/create_capybara_v3.py")
text = path.read_text(encoding="utf-8")


def replace_exact(old: str, new: str) -> None:
    global text
    if old not in text:
        raise RuntimeError(f"V3.1 patch target not found:\n{old[:180]}")
    text = text.replace(old, new, 1)


replace_exact('VERSION = "3.0.0-art-rebuild"', 'VERSION = "3.1.0-cute-proportion-rebuild"')

replace_exact('''body_pieces = [
    add_uv("Body_Lower_Block", (0, 0.10, 1.30), (0.94, 0.70, 1.08), None, 48, 32),
    add_uv("Body_Belly_Block", (0, -0.10, 1.60), (0.98, 0.72, 0.95), None, 48, 32),
    add_uv("Body_Chest_Block", (0, 0.00, 2.22), (0.78, 0.60, 0.78), None, 48, 32),
    add_uv("Body_Shoulder_Block", (0, 0.03, 2.56), (0.70, 0.56, 0.48), None, 48, 32),
]
body = union_voxel("Body", body_pieces, 0.058, MAT_FUR, 3)

head_pieces = [
    add_uv("Head_Cranium_Block", (0, 0.02, 3.42), (1.00, 0.75, 0.80), None, 56, 36),
    add_uv("Head_Forehead_Block", (0, -0.08, 3.70), (0.86, 0.65, 0.52), None, 48, 32),
    add_uv("Head_Midface_Block", (0, -0.29, 3.25), (0.92, 0.68, 0.61), None, 56, 36),
    add_uv("Head_SnoutBridge_Block", (0, -0.62, 3.23), (0.78, 0.55, 0.44), None, 48, 32),
    add_uv("Head_Muzzle_Block", (0, -0.83, 3.08), (0.66, 0.44, 0.34), None, 48, 32),
]
head = union_voxel("Head", head_pieces, 0.047, MAT_FUR, 3)

# A subtle muzzle patch follows the head instead of making two spherical cheeks.
snout = add_uv("Snout", (0, -0.905, 3.105), (0.62, 0.125, 0.31), MAT_FUR_LIGHT, 64, 40,
               rot=(math.radians(4), 0, 0))
''', '''body_pieces = [
    add_uv("Body_Lower_Block", (0, 0.08, 1.30), (1.03, 0.72, 1.12), None, 48, 32),
    add_uv("Body_Belly_Block", (0, -0.06, 1.72), (1.05, 0.74, 0.96), None, 48, 32),
    add_uv("Body_Chest_Block", (0, -0.02, 2.27), (0.88, 0.64, 0.72), None, 48, 32),
    add_uv("Body_Shoulder_Block", (0, 0.02, 2.60), (0.82, 0.60, 0.48), None, 48, 32),
]
body = union_voxel("Body", body_pieces, 0.052, MAT_FUR, 3)

# Wide, low cranium and integrated cheek/snout masses. The face must read as a
# capybara from profile without becoming a long cylindrical rodent muzzle.
head_pieces = [
    add_uv("Head_Cranium_Block", (0, 0.06, 3.48), (1.08, 0.70, 0.78), None, 56, 36),
    add_uv("Head_Forehead_Block", (0, -0.12, 3.78), (0.94, 0.58, 0.43), None, 48, 32),
    add_uv("Head_Cheek_L_Block", (-0.43, -0.36, 3.28), (0.58, 0.43, 0.48), None, 48, 32),
    add_uv("Head_Cheek_R_Block", (0.43, -0.36, 3.28), (0.58, 0.43, 0.48), None, 48, 32),
    add_uv("Head_Midface_Block", (0, -0.38, 3.34), (0.86, 0.46, 0.52), None, 56, 36),
    add_uv("Head_SnoutBridge_Block", (0, -0.59, 3.24), (0.72, 0.34, 0.34), None, 48, 32),
    add_uv("Head_Muzzle_Block", (0, -0.70, 3.13), (0.62, 0.27, 0.27), None, 48, 32),
    add_uv("Head_LowerJaw_Block", (0, -0.48, 2.99), (0.58, 0.35, 0.28), None, 48, 32),
]
head = union_voxel("Head", head_pieces, 0.040, MAT_FUR, 3)

# Thin colour patch, not an extra muzzle volume.
snout = add_uv("Snout", (0, -0.978, 3.155), (0.54, 0.024, 0.235), MAT_FUR_LIGHT, 56, 34,
               rot=(math.radians(2), 0, 0))
''')

replace_exact('''    ear = add_uv(f"Ear_{side}", (0.74 * sx, 0.02, 3.80), (0.22, 0.12, 0.22), MAT_FUR_DARK,
                 48, 32, rot=(math.radians(8), math.radians(12 * sx), math.radians(-8 * sx)))
    inner = add_uv(f"EarInner_{side}", (0.755 * sx, -0.105, 3.80), (0.125, 0.030, 0.125), MAT_FUR_LIGHT,
                   40, 26, rot=(math.radians(8), math.radians(12 * sx), math.radians(-8 * sx)))
''', '''    ear = add_uv(f"Ear_{side}", (0.78 * sx, 0.05, 3.95), (0.18, 0.10, 0.18), MAT_FUR_DARK,
                 44, 28, rot=(math.radians(8), math.radians(12 * sx), math.radians(-8 * sx)))
    inner = add_uv(f"EarInner_{side}", (0.785 * sx, -0.055, 3.95), (0.095, 0.022, 0.095), MAT_FUR_LIGHT,
                   36, 22, rot=(math.radians(8), math.radians(12 * sx), math.radians(-8 * sx)))
''')

replace_exact('''    x = 0.43 * sx
    eye = add_uv(f"Eye_{side}", (x, -0.675, 3.49), (0.205, 0.105, 0.235), MAT_EYE, 64, 40,
                 rot=(0, math.radians(3 * sx), 0))
    iris = add_uv(f"Iris_{side}", (x, -0.778, 3.49), (0.125, 0.022, 0.150), MAT_IRIS, 48, 32)
    hi = add_uv(f"EyeHighlight_{side}", (x - 0.052 * sx, -0.806, 3.575), (0.052, 0.015, 0.064), MAT_HIGHLIGHT, 32, 22)
    hi2 = add_uv(f"EyeHighlightSmall_{side}", (x + 0.055 * sx, -0.808, 3.435), (0.022, 0.010, 0.026), MAT_HIGHLIGHT, 24, 16)
    # Brown upper eyelid hugs the eye and removes the staring expression.
    lid = add_uv(f"Eyelid_{side}", (x, -0.789, 3.595), (0.225, 0.026, 0.090), MAT_FUR_DARK, 56, 34,
                 rot=(math.radians(-4), 0, math.radians(-4 * sx)))
''', '''    x = 0.46 * sx
    # Large dark eyes are the main cute feature. They sit proud of the face and
    # are not buried under the eyelids or hat brim.
    eye = add_uv(f"Eye_{side}", (x, -0.725, 3.58), (0.235, 0.125, 0.270), MAT_EYE, 64, 40,
                 rot=(0, math.radians(3 * sx), 0))
    iris = add_uv(f"Iris_{side}", (x, -0.846, 3.58), (0.112, 0.014, 0.132), MAT_IRIS, 44, 28)
    hi = add_uv(f"EyeHighlight_{side}", (x - 0.060 * sx, -0.866, 3.675), (0.058, 0.011, 0.070), MAT_HIGHLIGHT, 28, 18)
    hi2 = add_uv(f"EyeHighlightSmall_{side}", (x + 0.060 * sx, -0.868, 3.515), (0.022, 0.008, 0.026), MAT_HIGHLIGHT, 20, 14)
    # A narrow upper lid frames the eye instead of covering it.
    lid = add_uv(f"Eyelid_{side}", (x, -0.842, 3.765), (0.225, 0.016, 0.050), MAT_FUR_DARK, 48, 30,
                 rot=(math.radians(-3), 0, math.radians(-4 * sx)))
''')

replace_exact('''    brow = add_uv(f"Brow_{side}", (x, -0.695, 3.76), (0.19, 0.025, 0.035), MAT_FUR_DARK, 40, 22,
                  rot=(0, 0, math.radians(-5 * sx)))
''', '''    brow = add_uv(f"Brow_{side}", (x, -0.720, 3.865), (0.14, 0.014, 0.022), MAT_FUR_DARK, 32, 18,
                  rot=(0, 0, math.radians(-5 * sx)))
''')

replace_exact('''    cheek = add_uv(f"Cheek_{side}", (0.45 * sx, -1.006, 3.03), (0.16, 0.018, 0.095), MAT_FUR_LIGHT, 36, 22)
''', '''    cheek = add_uv(f"Cheek_{side}", (0.43 * sx, -0.985, 3.18), (0.14, 0.012, 0.075), MAT_FUR_LIGHT, 32, 20)
''')

replace_exact('''nose = add_uv("Nose", (0, -1.194, 3.205), (0.39, 0.145, 0.205), MAT_NOSE, 64, 40,
              rot=(math.radians(4), 0, 0))
''', '''nose = add_uv("Nose", (0, -1.055, 3.245), (0.315, 0.090, 0.155), MAT_NOSE, 56, 34,
              rot=(math.radians(3), 0, 0))
''')
replace_exact('''        add_uv(f"Nostril_{side}", (0.145 * sx, -1.325, 3.225), (0.068, 0.020, 0.038), MAT_NOSTRIL, 32, 20,
''', '''        add_uv(f"Nostril_{side}", (0.118 * sx, -1.139, 3.255), (0.052, 0.012, 0.030), MAT_NOSTRIL, 28, 18,
''')

replace_exact('''mouth = add_uv("Mouth", (0, -1.135, 2.925), (0.30, 0.035, 0.155), MAT_MOUTH, 56, 34)
''', '''mouth = add_uv("Mouth", (0, -0.994, 3.020), (0.225, 0.016, 0.105), MAT_MOUTH, 48, 30)
''')
replace_exact('''tongue = add_uv("Tongue", (0, -1.170, 2.885), (0.18, 0.024, 0.070), MAT_TONGUE, 40, 24)
''', '''tongue = add_uv("Tongue", (0, -1.014, 2.985), (0.125, 0.010, 0.045), MAT_TONGUE, 32, 20)
''')
replace_exact('''    add_cube(f"Tooth_{side}", (0.095 * sx, -1.177, 3.005), (0.082, 0.034, 0.115), MAT_TOOTH, 0.045,
''', '''    add_cube(f"Tooth_{side}", (0.075 * sx, -1.018, 3.075), (0.060, 0.020, 0.082), MAT_TOOTH, 0.032,
''')

replace_exact('''left_arm = soft_limb("Arm_L", [(-0.69, -0.02, 2.16), (-0.80, -0.18, 1.72), (-0.75, -0.34, 1.28)],
                     [(0.27, 0.25, 0.38), (0.25, 0.23, 0.37), (0.27, 0.22, 0.29)], MAT_FUR, 0.045)
right_arm = soft_limb("Arm_R", [(0.69, -0.01, 2.15), (0.79, -0.17, 1.70), (0.72, -0.35, 1.25)],
                      [(0.27, 0.25, 0.38), (0.25, 0.23, 0.37), (0.27, 0.22, 0.29)], MAT_FUR, 0.045)
''', '''left_arm = soft_limb("Arm_L", [(-0.76, 0.00, 2.17), (-0.82, -0.12, 1.83), (-0.74, -0.25, 1.52)],
                     [(0.29, 0.27, 0.34), (0.26, 0.24, 0.31), (0.25, 0.22, 0.23)], MAT_FUR, 0.043)
right_arm = soft_limb("Arm_R", [(0.76, 0.00, 2.17), (0.82, -0.12, 1.83), (0.74, -0.25, 1.52)],
                      [(0.29, 0.27, 0.34), (0.26, 0.24, 0.31), (0.25, 0.22, 0.23)], MAT_FUR, 0.043)
''')
replace_exact('''    add_uv(f"Foot_{side}", (0.43 * sx, -0.20, 0.30), (0.43, 0.52, 0.25), MAT_FUR_DARK, 56, 34,
''', '''    add_uv(f"Foot_{side}", (0.41 * sx, -0.15, 0.30), (0.34, 0.44, 0.22), MAT_FUR_DARK, 52, 32,
''')
replace_exact('''        add_uv(f"Toe_{side}_{toe}", (tx, -0.685, 0.30), (0.055, 0.025, 0.040), MAT_NOSE, 28, 18)
''', '''        add_uv(f"Toe_{side}_{toe}", (tx, -0.555, 0.30), (0.045, 0.018, 0.030), MAT_NOSE, 24, 16)
''')

replace_exact('''hat_brim = add_cylinder("Hat_Brim", (0, -0.015, 4.00), 1.02, 0.10, MAT_HAT, 80,
                        scale=(1.08, 0.88, 1.0), bevel=0.055)
hat_crown_parts = [
    add_uv("Hat_Crown_Block", (0, 0.02, 4.22), (0.76, 0.60, 0.32), None, 56, 34),
    add_uv("Hat_Top_Block", (0, 0.05, 4.40), (0.62, 0.49, 0.20), None, 48, 30),
]
hat_crown = union_voxel("Hat_Crown", hat_crown_parts, 0.045, MAT_HAT_LIGHT, 2)
hat_band = add_torus("Hat_Band", (0, 0.015, 4.09), 0.67, 0.042, MAT_LEATHER,
''', '''hat_brim = add_cylinder("Hat_Brim", (0, -0.005, 4.16), 0.96, 0.085, MAT_HAT, 72,
                        scale=(1.05, 0.84, 1.0), bevel=0.045)
hat_crown_parts = [
    add_uv("Hat_Crown_Block", (0, 0.03, 4.36), (0.72, 0.55, 0.30), None, 52, 32),
    add_uv("Hat_Top_Block", (0, 0.06, 4.53), (0.58, 0.45, 0.18), None, 44, 28),
]
hat_crown = union_voxel("Hat_Crown", hat_crown_parts, 0.042, MAT_HAT_LIGHT, 2)
hat_band = add_torus("Hat_Band", (0, 0.020, 4.25), 0.63, 0.036, MAT_LEATHER,
''')

replace_exact('''add_cube("Camera_Body", (0, -0.73, 1.68), (0.36, 0.14, 0.25), MAT_LEATHER_LIGHT, 0.065)
add_cylinder("Camera_Lens", (0, -0.93, 1.68), 0.17, 0.20, MAT_METAL, 56,
''', '''add_cube("Camera_Body", (0, -0.76, 1.70), (0.31, 0.12, 0.22), MAT_LEATHER_LIGHT, 0.055)
add_cylinder("Camera_Lens", (0, -0.92, 1.70), 0.145, 0.16, MAT_METAL, 48,
''')
replace_exact('''add_cylinder("Camera_Glass", (0, -1.045, 1.68), 0.115, 0.035, MAT_GLASS, 56,
''', '''add_cylinder("Camera_Glass", (0, -1.015, 1.70), 0.095, 0.028, MAT_GLASS, 48,
''')

text = text.replace('"art_status": "V3 blockout + face candidate; requires visual approval before final retopology/rig"',
                    '"art_status": "V3.1 cute proportion candidate; requires visual approval before retopology/rig"')
path.write_text(text, encoding="utf-8")
print("CAPIBARA_V3_1_CUTE_PATCH_OK", path)
