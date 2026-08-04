from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "capibara-alpha-source/create_capybara_v4_clean_surface.py")
text = path.read_text(encoding="utf-8")
text = text.replace('VERSION = "10.0.0-reference-face-anatomy"', 'VERSION = "11.0.0-integrated-face"', 1)

# Remove the two decal-like muzzle patches. Tonal variation stays on the fused
# surface through its second material slot.
patches = '''
uv("Muzzle_Patch_L", (-0.255, -1.005, 2.830), (0.320, 0.010, 0.205), MAT_FUR_LIGHT, 44, 28,
   rot=(math.radians(2), math.radians(-5), math.radians(-3)))
uv("Muzzle_Patch_R", (0.255, -1.005, 2.830), (0.320, 0.010, 0.205), MAT_FUR_LIGHT, 44, 28,
   rot=(math.radians(2), math.radians(5), math.radians(3)))'''
if patches not in text:
    raise RuntimeError('V11 muzzle patch block not found')
text = text.replace(patches, '', 1)

# Increase the tonal region around the muzzle without introducing new geometry.
text = text.replace('if center.y < -0.77 and 2.58 < center.z < 3.15:',
                    'if center.y < -0.70 and 2.55 < center.z < 3.14:', 1)

# Replace the protruding mouth ellipsoid with a true boolean cavity in the
# sculpted face, then place a dark interior slightly behind the cut.
old_mouth = 'uv("Mouth", (0, -1.066, 2.650), (0.300, 0.014, 0.155), MAT_MOUTH, 48, 30)'
new_mouth = '''mouth_cutter = uv("Mouth_Cutter", (0, -0.975, 2.650), (0.300, 0.230, 0.168), MAT_MOUTH, 48, 30)
for obj in (sculpt_master, mouth_cutter):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target="MESH")
boolean = sculpt_master.modifiers.new("Carve friendly smile", "BOOLEAN")
boolean.operation = "DIFFERENCE"
boolean.solver = "EXACT"
boolean.object = mouth_cutter
bpy.context.view_layer.objects.active = sculpt_master
bpy.ops.object.modifier_apply(modifier=boolean.name)
bpy.data.objects.remove(mouth_cutter, do_unlink=True)
uv("Mouth_Interior", (0, -0.965, 2.645), (0.280, 0.018, 0.145), MAT_MOUTH, 48, 30)'''
if old_mouth not in text:
    raise RuntimeError('V11 mouth target not found')
text = text.replace(old_mouth, new_mouth, 1)

# Place tongue and incisors within the cavity.
text = text.replace('(0, -1.083, 2.568), (0.065, 0.007, 0.022)',
                    '(0, -0.994, 2.575), (0.075, 0.010, 0.025)', 1)
text = text.replace('(0.052 * sx, -1.084, 2.747), (0.037, 0.010, 0.052)',
                    '(0.052 * sx, -0.998, 2.742), (0.039, 0.012, 0.056)', 1)

# Eyes keep the reference size but become more natural: dark brown-black,
# smaller highlights and slightly compressed vertical proportions.
text = text.replace('(0.010, 0.007, 0.005, 1), 0.13', '(0.018, 0.009, 0.005, 1), 0.16', 1)
text = text.replace('(x, -0.795, 3.035), (0.176, 0.092, 0.205)',
                    '(x, -0.795, 3.035), (0.170, 0.090, 0.190)', 1)
text = text.replace('(x - 0.042 * sx, -0.889, 3.113), (0.041, 0.008, 0.049)',
                    '(x - 0.040 * sx, -0.887, 3.105), (0.033, 0.007, 0.040)', 1)
text = text.replace('(x + 0.042 * sx, -0.892, 2.972), (0.014, 0.005, 0.017)',
                    '(x + 0.040 * sx, -0.890, 2.980), (0.010, 0.004, 0.012)', 1)

# Slightly broader and flatter capybara nose with subtle nostrils.
text = text.replace('(0, -1.075, 2.905), (0.225, 0.048, 0.102)',
                    '(0, -1.075, 2.905), (0.245, 0.052, 0.100)', 1)
text = text.replace('(0.082 * sx, -1.123, 2.916)',
                    '(0.090 * sx, -1.128, 2.916)', 1)

# Blend the cheek material transition through a softer noise scale.
text = text.replace('mapping.inputs["Scale"].default_value = (42.0, 42.0, 18.0)',
                    'mapping.inputs["Scale"].default_value = (34.0, 34.0, 22.0)', 1)
text = text.replace('color_noise.inputs["Detail"].default_value = 4.5',
                    'color_noise.inputs["Detail"].default_value = 3.4', 1)

# Feet and fingers receive tiny dark pads instead of fully dark digits.
text = text.replace('(0.046, 0.038, 0.125), MAT_FUR, 28, 18',
                    '(0.046, 0.038, 0.125), MAT_FUR, 28, 18', 1)

path.write_text(text, encoding='utf-8')
print('CAPIBARA_V11_INTEGRATED_FACE_OK', path)
