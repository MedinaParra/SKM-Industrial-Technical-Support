from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "capibara-alpha-source/create_capybara_v13_character_rebuild.py")
text = path.read_text(encoding="utf-8")
text = text.replace('VERSION = "16.0.0-head-assembly-correction"', 'VERSION = "17.0.0-hero-assembly"', 1)

# Fine, low-contrast coat instead of procedural camouflage.
text = text.replace('noise.inputs["Scale"].default_value = 34.0', 'noise.inputs["Scale"].default_value = 58.0', 1)
text = text.replace('noise.inputs["Detail"].default_value = 2.7', 'noise.inputs["Detail"].default_value = 2.0', 1)
text = text.replace('noise.inputs["Roughness"].default_value = 0.58', 'noise.inputs["Roughness"].default_value = 0.50', 1)
text = text.replace('(0.135, 0.050, 0.015, 1), (0.30, 0.125, 0.040, 1)',
                    '(0.145, 0.055, 0.018, 1), (0.255, 0.105, 0.036, 1)', 1)
text = text.replace('(0.18, 0.065, 0.020, 1), (0.34, 0.150, 0.055, 1)',
                    '(0.175, 0.065, 0.022, 1), (0.285, 0.125, 0.046, 1)', 1)

studio_anchor = '# -----------------------------------------------------------------------------\n# Studio\n# -----------------------------------------------------------------------------\n'
if studio_anchor not in text:
    raise RuntimeError('V17 studio anchor not found')

assembly = r'''
# -----------------------------------------------------------------------------
# V17 hero assembly: transform every head-related element together so facial
# features, ears and the hat remain attached while correcting overall ratio.
# -----------------------------------------------------------------------------
def apply_object_scale(obj, factors):
    obj.scale.x *= factors[0]
    obj.scale.y *= factors[1]
    obj.scale.z *= factors[2]
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Remove the anime vertical eye shape before scaling the complete head.
for eye_name in ("Eye_L", "Eye_R"):
    eye_obj = bpy.data.objects.get(eye_name)
    if eye_obj:
        apply_object_scale(eye_obj, (0.92, 0.94, 0.72))

# Catchlights should read as moist reflections, not cartoon bubbles.
for highlight_name in (
    "Eye_Highlight_L", "Eye_Highlight_R",
    "Eye_Highlight_Small_L", "Eye_Highlight_Small_R",
):
    highlight_obj = bpy.data.objects.get(highlight_name)
    if highlight_obj:
        apply_object_scale(highlight_obj, (0.72, 0.72, 0.72))

nose_obj = bpy.data.objects.get("Nose")
if nose_obj:
    apply_object_scale(nose_obj, (0.78, 0.82, 0.78))

mouth_obj = bpy.data.objects.get("Mouth_Interior")
if mouth_obj:
    apply_object_scale(mouth_obj, (1.14, 0.92, 0.88))
    mouth_obj.location.z -= 0.018

for tooth_name in ("Incisor_L", "Incisor_R"):
    tooth_obj = bpy.data.objects.get(tooth_name)
    if tooth_obj:
        apply_object_scale(tooth_obj, (1.18, 1.15, 1.32))
        tooth_obj.location.y -= 0.030
        tooth_obj.location.z += 0.008

head_root = bpy.data.objects.new("Head_Hero_Assembly", None)
model.objects.link(head_root)
head_root.location = (0.0, 0.0, 3.02)

head_exact = {
    "Head_Fused_Sculpt", "Nose", "Mouth_Interior", "Tongue",
    "Hat_Brim", "Hat_Crown", "Hat_Band",
}
head_prefixes = (
    "Eye_", "Nostril_", "Incisor_", "Ear_",
)
for obj in list(model.objects):
    if obj is head_root:
        continue
    if obj.name in head_exact or obj.name.startswith(head_prefixes):
        matrix_world = obj.matrix_world.copy()
        obj.parent = head_root
        obj.matrix_world = matrix_world

# Reference ratio: head is important but smaller than the V16 cartoon skull.
head_root.scale = (0.82, 0.90, 0.82)
head_root.location.z -= 0.105
head_root.location.y += 0.015

# Slightly broaden and shorten the pear body without touching the head group.
body_obj = bpy.data.objects.get("Body_Pear")
if body_obj:
    apply_object_scale(body_obj, (1.07, 1.02, 0.95))

# Hands remain warm fur; only nail pads/toes stay dark.
wave_palm = bpy.data.objects.get("Wave_Palm")
if wave_palm:
    apply_object_scale(wave_palm, (1.06, 1.05, 1.06))

'''
text = text.replace(studio_anchor, assembly + studio_anchor, 1)

# Reframe the compact assembly.
text = text.replace('(0, -7.55, 2.95), (0, -0.14, 2.08), 67',
                    '(0, -7.15, 2.72), (0, -0.13, 1.93), 68', 1)
text = text.replace('(7.45, -0.10, 2.95), (0, 0.00, 2.08), 67',
                    '(7.10, -0.10, 2.72), (0, 0.00, 1.93), 68', 1)
text = text.replace('(4.65, -6.35, 3.00), (0, -0.18, 2.08), 68',
                    '(4.45, -6.05, 2.78), (0, -0.18, 1.95), 69', 1)

path.write_text(text, encoding='utf-8')
print('CAPIBARA_V17_HERO_ASSEMBLY_OK', path)
