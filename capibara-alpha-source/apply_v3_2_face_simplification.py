from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "capibara-alpha-source/create_capybara_v3.py")
text = path.read_text(encoding="utf-8")

text = text.replace('VERSION = "3.1.0-cute-proportion-rebuild"', 'VERSION = "3.2.0-face-simplification"')

# Make Blender Workbench display the actual material palette used by Eevee.
needle = '    mat = bpy.data.materials.new(name)\n    mat.use_nodes = True\n'
if needle not in text:
    raise RuntimeError('material function target not found')
text = text.replace(needle, '    mat = bpy.data.materials.new(name)\n    mat.diffuse_color = base\n    mat.use_nodes = True\n', 1)

# Shorter, wider pear body: less sausage-like and closer to the menu character.
body_start = text.index('body_pieces = [')
body_end_marker = 'body = union_voxel("Body", body_pieces, 0.052, MAT_FUR, 3)'
body_end = text.index(body_end_marker, body_start) + len(body_end_marker)
text = text[:body_start] + '''body_pieces = [
    add_uv("Body_Lower_Block", (0, 0.06, 1.22), (1.05, 0.74, 1.00), None, 48, 32),
    add_uv("Body_Belly_Block", (0, -0.06, 1.55), (1.08, 0.76, 0.88), None, 48, 32),
    add_uv("Body_Chest_Block", (0, -0.02, 2.05), (0.93, 0.66, 0.67), None, 48, 32),
    add_uv("Body_Shoulder_Block", (0, 0.02, 2.42), (0.84, 0.61, 0.45), None, 48, 32),
]
body = union_voxel("Body", body_pieces, 0.052, MAT_FUR, 3)''' + text[body_end:]

# Replace lumpy paired cheeks with one continuous capybara head volume.
head_start = text.index('head_pieces = [', body_start)
head_end_marker = '               rot=(math.radians(2), 0, 0))'
head_end = text.index(head_end_marker, head_start) + len(head_end_marker)
text = text[:head_start] + '''head_pieces = [
    add_uv("Head_Cranium_Block", (0, 0.06, 3.47), (1.08, 0.73, 0.80), None, 56, 36),
    add_uv("Head_Forehead_Block", (0, -0.15, 3.73), (0.94, 0.61, 0.46), None, 52, 34),
    add_uv("Head_Midface_Block", (0, -0.38, 3.34), (0.88, 0.50, 0.52), None, 56, 36),
    add_uv("Head_SnoutBridge_Block", (0, -0.60, 3.23), (0.74, 0.38, 0.36), None, 52, 34),
    add_uv("Head_Muzzle_Block", (0, -0.68, 3.09), (0.64, 0.32, 0.30), None, 48, 32),
]
head = union_voxel("Head", head_pieces, 0.038, MAT_FUR, 4)

# Colour patch is almost flush; it must not read as a separate dog muzzle.
snout = add_uv("Snout", (0, -1.005, 3.145), (0.50, 0.010, 0.205), MAT_FUR_LIGHT, 52, 32,
               rot=(math.radians(2), 0, 0))''' + text[head_end:]

# Clean face: black eyes + highlights only. No protruding iris rings, eyebrows,
# cheek buttons or caterpillar eyelids in the base expression.
face_start = text.index('face_meshes = []')
face_end = text.index('\nnose = add_uv', face_start)
face_block = '''face_meshes = []
for side, sx in (("L", -1), ("R", 1)):
    x = 0.49 * sx
    eye = add_uv(f"Eye_{side}", (x, -0.735, 3.58), (0.225, 0.118, 0.255), MAT_EYE, 60, 38,
                 rot=(0, math.radians(4 * sx), 0))
    add_shape(eye, f"eye_squint_{side}", lambda co, i: Vector((co.x, co.y, co.z * 0.70)))
    add_shape(eye, f"eye_wide_{side}", lambda co, i: Vector((co.x, co.y, co.z * 1.10)))
    face_meshes.append(eye)
    add_uv(f"EyeHighlight_{side}", (x - 0.058 * sx, -0.857, 3.670),
           (0.055, 0.010, 0.067), MAT_HIGHLIGHT, 26, 18)
    add_uv(f"EyeHighlightSmall_{side}", (x + 0.055 * sx, -0.859, 3.515),
           (0.020, 0.007, 0.024), MAT_HIGHLIGHT, 20, 14)
'''
text = text[:face_start] + face_block + text[face_end:]

# Nose and mouth become slightly smaller and higher, avoiding a pig/dog face.
text = text.replace('nose = add_uv("Nose", (0, -1.055, 3.245), (0.315, 0.090, 0.155), MAT_NOSE, 56, 34,',
                    'nose = add_uv("Nose", (0, -1.045, 3.235), (0.285, 0.075, 0.140), MAT_NOSE, 52, 32,', 1)
text = text.replace('(0.118 * sx, -1.139, 3.255), (0.052, 0.012, 0.030)',
                    '(0.105 * sx, -1.125, 3.245), (0.043, 0.009, 0.024)', 1)
text = text.replace('mouth = add_uv("Mouth", (0, -0.994, 3.020), (0.225, 0.016, 0.105), MAT_MOUTH, 48, 30)',
                    'mouth = add_uv("Mouth", (0, -1.000, 3.015), (0.195, 0.012, 0.085), MAT_MOUTH, 44, 28)', 1)
text = text.replace('(0.075 * sx, -1.018, 3.075), (0.060, 0.020, 0.082)',
                    '(0.065 * sx, -1.018, 3.065), (0.050, 0.016, 0.068)', 1)

# Remove the decorative finger dots from the silhouette review.
text = text.replace('        add_uv(f"Finger_{side}_{finger}", (fx, -0.555, 1.23), (0.040, 0.024, 0.034), MAT_NOSE, 24, 16)',
                    '        add_uv(f"Finger_{side}_{finger}", (fx, -0.31, 1.48), (0.018, 0.010, 0.015), MAT_FUR_DARK, 20, 12)', 1)

# Raise arms to match the shortened torso.
text = text.replace('[(-0.76, 0.00, 2.17), (-0.82, -0.12, 1.83), (-0.74, -0.25, 1.52)]',
                    '[(-0.78, 0.00, 2.10), (-0.84, -0.10, 1.78), (-0.76, -0.22, 1.49)]', 1)
text = text.replace('[(0.76, 0.00, 2.17), (0.82, -0.12, 1.83), (0.74, -0.25, 1.52)]',
                    '[(0.78, 0.00, 2.10), (0.84, -0.10, 1.78), (0.76, -0.22, 1.49)]', 1)

text = text.replace('"art_status": "V3.1 cute proportion candidate; requires visual approval before retopology/rig"',
                    '"art_status": "V3.2 simplified capybara face candidate; visual approval required"')
path.write_text(text, encoding="utf-8")
print("CAPIBARA_V3_2_FACE_SIMPLIFICATION_OK", path)
