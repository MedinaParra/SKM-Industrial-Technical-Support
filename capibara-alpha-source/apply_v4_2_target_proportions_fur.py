from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "capibara-alpha-source/create_capybara_v4_clean_surface.py")
text = path.read_text(encoding="utf-8")
text = text.replace('VERSION = "4.1.0-capybara-identity"', 'VERSION = "4.2.0-target-proportions-fur"', 1)

# Bring muzzle and explorer palette closer to the warm reference.
text = text.replace('(0.355, 0.145, 0.050, 1), 0.92', '(0.305, 0.110, 0.038, 1), 0.92', 1)
text = text.replace('(0.16, 0.19, 0.055, 1), 0.88', '(0.105, 0.135, 0.034, 1), 0.90', 1)
text = text.replace('(0.27, 0.30, 0.095, 1), 0.86', '(0.205, 0.235, 0.065, 1), 0.88', 1)

# Procedural mobile-friendly fur: broad colour variation plus a fine bump. It
# is shader detail, not millions of strand particles.
anchor = 'MAT_FLOOR = material("Floor", (0.12, 0.15, 0.11, 1), 0.98)\n'
if anchor not in text:
    raise RuntimeError('fur shader insertion anchor not found')
fur_code = r'''

def apply_fur_shader(mat, dark, light, color_scale=7.0, bump_scale=82.0):
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    color_noise = nodes.new("ShaderNodeTexNoise")
    color_noise.inputs["Scale"].default_value = color_scale
    color_noise.inputs["Detail"].default_value = 5.0
    color_noise.inputs["Roughness"].default_value = 0.72
    color_noise.inputs["Distortion"].default_value = 0.16
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.26
    ramp.color_ramp.elements[0].color = dark
    ramp.color_ramp.elements[1].position = 0.76
    ramp.color_ramp.elements[1].color = light
    links.new(color_noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    fine = nodes.new("ShaderNodeTexNoise")
    fine.inputs["Scale"].default_value = bump_scale
    fine.inputs["Detail"].default_value = 3.0
    fine.inputs["Roughness"].default_value = 0.78
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.20
    bump.inputs["Distance"].default_value = 0.035
    links.new(fine.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

apply_fur_shader(MAT_FUR, (0.105, 0.028, 0.008, 1), (0.405, 0.155, 0.045, 1), 7.5, 90.0)
apply_fur_shader(MAT_FUR_LIGHT, (0.19, 0.055, 0.014, 1), (0.48, 0.205, 0.070, 1), 8.0, 96.0)
apply_fur_shader(MAT_FUR_DARK, (0.045, 0.010, 0.004, 1), (0.22, 0.065, 0.016, 1), 8.5, 92.0)
'''
text = text.replace(anchor, anchor + fur_code, 1)

# Short, wide pear torso matching the reference rather than a tall bean.
start = text.index('body_sections = [')
end_marker = 'body = loft_z("Body_Clean", body_sections, 48, MAT_FUR, 2)'
end = text.index(end_marker, start) + len(end_marker)
body = '''body_sections = [
    (0.24, 0.02, 0.35, 0.37),
    (0.38, 0.00, 0.62, 0.53),
    (0.64, 0.02, 0.86, 0.64),
    (0.94, 0.01, 0.98, 0.70),
    (1.24, -0.02, 1.02, 0.72),
    (1.52, -0.03, 0.99, 0.70),
    (1.80, 0.00, 0.92, 0.65),
    (2.04, 0.03, 0.85, 0.61),
    (2.27, 0.05, 0.79, 0.57),
    (2.48, 0.07, 0.74, 0.53),
    (2.66, 0.08, 0.65, 0.47),
]
body = loft_z("Body_Clean", body_sections, 48, MAT_FUR, 2)'''
text = text[:start] + body + text[end:]

# Lower the head and retain its rounded-rectangular capybara skull.
start = text.index('head_sections = [', start)
end_marker = 'head = loft_y("Head_Clean", head_sections, 56, MAT_FUR, 2)'
end = text.index(end_marker, start) + len(end_marker)
head = '''head_sections = [
    (0.72, 3.26, 0.28, 0.27),
    (0.58, 3.30, 0.70, 0.50),
    (0.34, 3.32, 0.98, 0.63),
    (0.08, 3.32, 1.08, 0.69),
    (-0.18, 3.29, 1.08, 0.68),
    (-0.42, 3.23, 1.00, 0.60),
    (-0.62, 3.15, 0.91, 0.51),
    (-0.79, 3.07, 0.80, 0.42),
    (-0.94, 3.01, 0.67, 0.33),
    (-1.07, 3.00, 0.49, 0.23),
    (-1.14, 3.02, 0.25, 0.13),
]
head = loft_y("Head_Clean", head_sections, 56, MAT_FUR, 2)
uv("Neck_Bridge", (0, 0.03, 2.66), (0.72, 0.55, 0.34), MAT_FUR, 52, 32)'''
text = text[:start] + head + text[end:]

# Facial components follow the lower skull.
replacements = {
    '(0, -1.125, 3.135), (0.55, 0.012, 0.190)': '(0, -1.125, 3.015), (0.55, 0.010, 0.185)',
    '(0.80 * sx, 0.04, 3.93)': '(0.80 * sx, 0.04, 3.81)',
    '(0.805 * sx, -0.043, 3.93)': '(0.805 * sx, -0.043, 3.81)',
    '(x, -0.790, 3.53), (0.145, 0.082, 0.175)': '(x, -0.790, 3.41), (0.158, 0.088, 0.188)',
    '(x - 0.036 * sx, -0.874, 3.590), (0.034, 0.008, 0.041)': '(x - 0.039 * sx, -0.880, 3.475), (0.037, 0.008, 0.044)',
    '(x + 0.038 * sx, -0.877, 3.485), (0.013, 0.005, 0.016)': '(x + 0.040 * sx, -0.882, 3.365), (0.014, 0.005, 0.017)',
    '(0, -1.205, 3.205), (0.325, 0.073, 0.135)': '(0, -1.205, 3.085), (0.325, 0.073, 0.135)',
    '(0.118 * sx, -1.277, 3.216)': '(0.118 * sx, -1.277, 3.096)',
    '(0, -1.172, 3.005), (0.205, 0.016, 0.098)': '(0, -1.172, 2.885), (0.220, 0.018, 0.108)',
    '(0, -1.190, 2.980), (0.105, 0.009, 0.037)': '(0, -1.190, 2.855), (0.112, 0.010, 0.041)',
    '(0.060 * sx, -1.192, 3.060), (0.043, 0.014, 0.060)': '(0.060 * sx, -1.192, 2.940), (0.046, 0.015, 0.065)',
}
for old, new in replacements.items():
    if old not in text:
        raise RuntimeError(f'face target not found: {old}')
    text = text.replace(old, new, 1)

# Compact pose and accessories.
pose_replacements = {
    '[(-0.65, -0.02, 2.18), (-0.82, -0.13, 2.40), (-0.94, -0.22, 2.68)]': '[(-0.65, -0.02, 2.02), (-0.82, -0.13, 2.26), (-0.94, -0.22, 2.54)]',
    '(-0.98, -0.25, 2.85)': '(-0.98, -0.25, 2.72)',
    '(x, -0.28, 3.06)': '(x, -0.28, 2.93)',
    '[(0.67, -0.01, 2.14), (0.78, -0.10, 1.82), (0.72, -0.23, 1.55)]': '[(0.67, -0.01, 2.02), (0.78, -0.10, 1.70), (0.72, -0.23, 1.40)]',
    '(0.71, -0.25, 1.45)': '(0.71, -0.25, 1.31)',
    '(0, 0.00, 4.10)': '(0, 0.00, 3.98)',
    '(4.12, 0.02, 0.70, 0.54)': '(4.00, 0.02, 0.70, 0.54)',
    '(4.26, 0.04, 0.68, 0.52)': '(4.14, 0.04, 0.68, 0.52)',
    '(4.44, 0.06, 0.58, 0.44)': '(4.32, 0.06, 0.58, 0.44)',
    '(4.53, 0.07, 0.43, 0.34)': '(4.41, 0.07, 0.43, 0.34)',
    '(0, 0.01, 4.20)': '(0, 0.01, 4.08)',
    '(0, 0.64, 1.72)': '(0, 0.64, 1.48)',
    '(0, 0.84, 1.57)': '(0, 0.84, 1.34)',
    '(0.43 * sx, -0.01, 2.05)': '(0.43 * sx, -0.01, 1.83)',
    '(0, -0.73, 1.72)': '(0, -0.73, 1.48)',
    '(0, -0.89, 1.72)': '(0, -0.89, 1.48)',
    '(0, -0.985, 1.72)': '(0, -0.985, 1.48)',
    '(0, -0.04, 2.24)': '(0, -0.04, 2.00)',
}
for old, new in pose_replacements.items():
    if old not in text:
        raise RuntimeError(f'pose target not found: {old}')
    text = text.replace(old, new, 1)

path.write_text(text, encoding='utf-8')
print('CAPIBARA_V4_2_TARGET_PROPORTIONS_FUR_OK', path)
