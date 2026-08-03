from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "capibara-alpha-source/create_capybara_v4_clean_surface.py")
text = path.read_text(encoding="utf-8")
text = text.replace('VERSION = "5.0.0-sculpt-master"', 'VERSION = "6.0.0-reference-match"', 1)

# -----------------------------------------------------------------------------
# V6: match the supplied explorer capybara reference instead of preserving the
# previous procedural proportions. The target has a compact pear body, a broad
# rounded capybara skull, a short muzzle, lateral eyes and a warm fine coat.
# -----------------------------------------------------------------------------

# Softer head outline. The V5 superellipse was too boxy from the front.
text = text.replace('px = math.copysign(abs(c) ** 0.78, c)',
                    'px = math.copysign(abs(c) ** 0.88, c)', 1)
text = text.replace('pz = math.copysign(abs(s) ** 0.84, s)',
                    'pz = math.copysign(abs(s) ** 0.90, s)', 1)

# Replace the spotty shader with stretched, low-contrast procedural fibres.
start = text.index('def apply_fur_shader(')
end = text.index('apply_fur_shader(MAT_FUR,', start)
new_shader = '''def apply_fur_shader(mat, dark, light, color_scale=1.0, bump_scale=1.0):
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")

    tex = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (24.0, 24.0, 4.0)
    color_noise = nodes.new("ShaderNodeTexNoise")
    color_noise.inputs["Scale"].default_value = 1.0
    color_noise.inputs["Detail"].default_value = 2.3
    color_noise.inputs["Roughness"].default_value = 0.58
    color_noise.inputs["Distortion"].default_value = 0.035
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.31
    ramp.color_ramp.elements[0].color = dark
    ramp.color_ramp.elements[1].position = 0.69
    ramp.color_ramp.elements[1].color = light
    links.new(tex.outputs["Generated"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], color_noise.inputs["Vector"])
    links.new(color_noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

    fine_mapping = nodes.new("ShaderNodeMapping")
    fine_mapping.inputs["Scale"].default_value = (72.0, 72.0, 8.0)
    fine = nodes.new("ShaderNodeTexNoise")
    fine.inputs["Scale"].default_value = 1.0
    fine.inputs["Detail"].default_value = 2.0
    fine.inputs["Roughness"].default_value = 0.52
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.075
    bump.inputs["Distance"].default_value = 0.010
    links.new(tex.outputs["Generated"], fine_mapping.inputs["Vector"])
    links.new(fine_mapping.outputs["Vector"], fine.inputs["Vector"])
    links.new(fine.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Roughness"].default_value = 0.78

'''
text = text[:start] + new_shader + text[end:]

# Calls are deliberately low contrast, matching the warm reference fur.
call_start = text.index('apply_fur_shader(MAT_FUR,')
call_end = text.index('\n\n#', call_start)
new_calls = '''apply_fur_shader(MAT_FUR, (0.145, 0.050, 0.016, 1), (0.315, 0.135, 0.052, 1))
apply_fur_shader(MAT_FUR_LIGHT, (0.205, 0.085, 0.032, 1), (0.365, 0.175, 0.075, 1))
apply_fur_shader(MAT_FUR_DARK, (0.050, 0.016, 0.006, 1), (0.145, 0.050, 0.017, 1))'''
text = text[:call_start] + new_calls + text[call_end:]

# Compact pear body: clearly narrower than the head, shorter than V5.
body_start = text.index('body_sections = [')
body_end_marker = 'body = loft_z("Body_Clean", body_sections, 48, MAT_FUR, 2)'
body_end = text.index(body_end_marker, body_start) + len(body_end_marker)
body_block = '''body_sections = [
    (0.24, 0.02, 0.34, 0.36),
    (0.37, 0.00, 0.55, 0.49),
    (0.62, 0.01, 0.73, 0.59),
    (0.90, 0.00, 0.84, 0.65),
    (1.18, -0.02, 0.88, 0.67),
    (1.45, -0.03, 0.86, 0.66),
    (1.70, 0.00, 0.82, 0.63),
    (1.94, 0.03, 0.78, 0.59),
    (2.16, 0.05, 0.74, 0.55),
    (2.36, 0.07, 0.70, 0.51),
    (2.52, 0.08, 0.63, 0.46),
    (2.64, 0.08, 0.53, 0.39),
]
body = loft_z("Body_Clean", body_sections, 48, MAT_FUR, 2)'''
text = text[:body_start] + body_block + text[body_end:]

# Broad skull with a short forward taper. V5 looked like an anteater in profile.
head_start = text.index('head_sections = [', body_start)
head_end_marker = 'head = loft_y("Head_Clean", head_sections, 56, MAT_FUR, 2)'
head_end = text.index(head_end_marker, head_start) + len(head_end_marker)
head_block = '''head_sections = [
    (0.63, 3.20, 0.28, 0.25),
    (0.48, 3.24, 0.66, 0.47),
    (0.26, 3.27, 0.94, 0.61),
    (0.04, 3.27, 1.04, 0.68),
    (-0.17, 3.25, 1.05, 0.68),
    (-0.36, 3.21, 1.02, 0.63),
    (-0.52, 3.15, 0.96, 0.57),
    (-0.65, 3.09, 0.87, 0.49),
    (-0.76, 3.04, 0.76, 0.40),
    (-0.84, 3.01, 0.62, 0.31),
    (-0.90, 3.01, 0.44, 0.22),
    (-0.94, 3.02, 0.24, 0.13),
]
head = loft_y("Head_Clean", head_sections, 56, MAT_FUR, 2)'''
text = text[:head_start] + head_block + text[head_end:]

# Real overlap for a single neck/chest silhouette and a broad but short muzzle.
replacements = {
    'muzzle_core = uv("Muzzle_Core", (0, -1.015, 3.015), (0.54, 0.285, 0.245), MAT_FUR, 56, 34)':
        'muzzle_core = uv("Muzzle_Core", (0, -0.825, 3.015), (0.58, 0.205, 0.245), MAT_FUR, 56, 34)',
    'neck_core = uv("Neck_Core", (0, 0.035, 2.900), (0.66, 0.54, 0.32), MAT_FUR, 52, 32)':
        'neck_core = uv("Neck_Core", (0, 0.045, 2.650), (0.72, 0.56, 0.42), MAT_FUR, 52, 32)',
    'fuse_sculpt_master("Capibara_Sculpt_Master", [body, head, muzzle_core, neck_core], 0.030)':
        'fuse_sculpt_master("Capibara_Sculpt_Master", [body, head, muzzle_core, neck_core], 0.025)',
    'uv("Muzzle_Tone", (0, -1.286, 3.015), (0.47, 0.018, 0.172), MAT_FUR_LIGHT, 52, 32)':
        'uv("Muzzle_Tone", (0, -1.035, 3.015), (0.49, 0.010, 0.175), MAT_FUR_LIGHT, 52, 32)',
}
for old, new in replacements.items():
    if old not in text:
        raise RuntimeError(f'V6 sculpt target not found: {old}')
    text = text.replace(old, new, 1)

# Small lateral eyes, restrained lids, short nose and a wide friendly smile.
face_replacements = {
    'x = 0.47 * sx': 'x = 0.49 * sx',
    '(x, -0.790, 3.36), (0.165, 0.092, 0.195)': '(x, -0.735, 3.33), (0.142, 0.073, 0.174)',
    '(x - 0.041 * sx, -0.884, 3.430), (0.039, 0.008, 0.047)': '(x - 0.034 * sx, -0.809, 3.392), (0.032, 0.007, 0.039)',
    '(x + 0.041 * sx, -0.886, 3.310), (0.014, 0.005, 0.017)': '(x + 0.035 * sx, -0.812, 3.282), (0.012, 0.004, 0.015)',
    '(x, -0.894, 3.485), (0.172, 0.014, 0.052)': '(x, -0.813, 3.455), (0.150, 0.010, 0.026)',
    '(0, -1.330, 3.075), (0.270, 0.070, 0.120)': '(0, -1.085, 3.065), (0.245, 0.052, 0.108)',
    '(0.098 * sx, -1.398, 3.085)': '(0.088 * sx, -1.137, 3.074)',
    '(0, -1.312, 2.875), (0.210, 0.019, 0.108)': '(0, -1.055, 2.870), (0.225, 0.021, 0.132)',
    '(0, -1.332, 2.842), (0.108, 0.010, 0.040)': '(0, -1.077, 2.818), (0.105, 0.010, 0.038)',
    '(0.056 * sx, -1.334, 2.930), (0.042, 0.015, 0.061)': '(0.052 * sx, -1.078, 2.955), (0.037, 0.012, 0.054)',
}
for old, new in face_replacements.items():
    if old not in text:
        raise RuntimeError(f'V6 face target not found: {old}')
    text = text.replace(old, new, 1)

# Small ears and a hat that frames the face instead of flattening it.
hat_and_ear = {
    '(0.76 * sx, 0.05, 3.77), (0.145, 0.080, 0.145)': '(0.78 * sx, 0.05, 3.72), (0.135, 0.074, 0.135)',
    '(0.765 * sx, -0.030, 3.77), (0.070, 0.012, 0.070)': '(0.785 * sx, -0.022, 3.72), (0.064, 0.010, 0.064)',
    '(0, 0.00, 3.91)': '(0, 0.00, 3.84)',
    '(3.93, 0.02, 0.68, 0.52)': '(3.86, 0.02, 0.64, 0.48)',
    '(4.07, 0.04, 0.66, 0.50)': '(4.00, 0.04, 0.62, 0.46)',
    '(4.25, 0.06, 0.57, 0.43)': '(4.18, 0.06, 0.54, 0.40)',
    '(4.34, 0.07, 0.42, 0.33)': '(4.27, 0.07, 0.40, 0.30)',
    '(0, 0.01, 4.01)': '(0, 0.01, 3.94)',
}
for old, new in hat_and_ear.items():
    if old not in text:
        raise RuntimeError(f'V6 hat/ear target not found: {old}')
    text = text.replace(old, new, 1)

# Rebuild the wave with four readable rounded digits and a compact opposite arm.
old_wave_start = text.index('curve_limb("Arm_Wave"')
old_wave_end = text.index('# Compact feet.', old_wave_start)
new_wave = '''curve_limb("Arm_Wave", [(-0.60, -0.01, 1.98), (-0.79, -0.12, 2.24), (-0.91, -0.20, 2.52)], 0.195, MAT_FUR)
uv("Wave_Hand", (-0.95, -0.23, 2.66), (0.205, 0.145, 0.205), MAT_FUR_DARK, 44, 28,
   rot=(math.radians(-8), math.radians(-8), math.radians(-8)))
for i, x in enumerate((-1.085, -0.995, -0.905, -0.815)):
    uv(f"Wave_Finger_{i}", (x, -0.255, 2.835 + (0.015 if i in (1, 2) else 0.0)),
       (0.046, 0.038, 0.125), MAT_FUR_DARK, 28, 18,
       rot=(math.radians(-7), math.radians(-4), math.radians((i - 1.5) * 7)))
uv("Wave_Thumb", (-0.785, -0.255, 2.640), (0.055, 0.044, 0.105), MAT_FUR_DARK, 28, 18,
   rot=(math.radians(-12), math.radians(-8), math.radians(55)))
curve_limb("Arm_Rest", [(0.61, -0.01, 1.94), (0.71, -0.10, 1.63), (0.67, -0.22, 1.36)], 0.195, MAT_FUR)
uv("Rest_Hand", (0.66, -0.24, 1.27), (0.19, 0.145, 0.19), MAT_FUR_DARK, 40, 26)

'''
text = text[:old_wave_start] + new_wave + text[old_wave_end:]

# Feet with four small toes, closer to the reference silhouette.
feet_start = text.index('# Compact feet.')
feet_end = text.index('# -----------------------------------------------------------------------------\n# Explorer accessories', feet_start)
new_feet = '''# Compact feet with four short toes.
for side, sx in (("L", -1), ("R", 1)):
    uv(f"Foot_{side}", (0.34 * sx, -0.18, 0.27), (0.285, 0.365, 0.185), MAT_FUR_DARK, 48, 30)
    for toe in range(4):
        tx = 0.34 * sx + (toe - 1.5) * 0.057
        uv(f"Toe_{side}_{toe}", (tx, -0.535, 0.275), (0.028, 0.010, 0.021), MAT_NOSE, 20, 14)

'''
text = text[:feet_start] + new_feet + text[feet_end:]

# Accessories follow the shorter torso and stay secondary to the face.
accessory_replacements = {
    '(0, 0.64, 1.48)': '(0, 0.61, 1.36)',
    '(0, 0.84, 1.34)': '(0, 0.80, 1.23)',
    '(0.43 * sx, -0.01, 1.83)': '(0.39 * sx, -0.01, 1.72)',
    '(0, -0.73, 1.48), (0.30, 0.11, 0.215)': '(0, -0.69, 1.36), (0.27, 0.10, 0.195)',
    '(0, -0.745, 1.665), (0.25, 0.105, 0.055)': '(0, -0.705, 1.515), (0.225, 0.095, 0.050)',
    '(-0.17, -0.865, 1.735)': '(-0.15, -0.805, 1.570)',
    '(0, -0.90, 1.48), 0.155, 0.18': '(0, -0.855, 1.36), 0.138, 0.16',
    '(0, -1.008, 1.48), 0.100, 0.030': '(0, -0.955, 1.36), 0.090, 0.027',
    '(0, -0.04, 2.00)': '(0, -0.04, 1.86)',
}
for old, new in accessory_replacements.items():
    if old not in text:
        raise RuntimeError(f'V6 accessory target not found: {old}')
    text = text.replace(old, new, 1)

# Render a closer three-quarter view resembling the supplied hero framing.
text = text.replace('(5.1, -7.2, 3.25), (0, -0.05, 2.18), 62',
                    '(4.65, -7.35, 3.18), (0, -0.10, 2.05), 64', 1)

path.write_text(text, encoding="utf-8")
print("CAPIBARA_V6_REFERENCE_MATCH_OK", path)
