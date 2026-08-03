from pathlib import Path

root = Path("CapibaraAlpha")

# ---------------------------------------------------------------------------
# Fixes required by Godot 4.7.1 and 32/64-bit Android export.
# ---------------------------------------------------------------------------
main = root / "main.gd"
text = main.read_text(encoding="utf-8")
old = """    elif event is InputEventMouseMotion and dragging:\n        var d := event.position - drag_last\n        drag_last = event.position\n        _rotate_character(d)\n"""
new = """    elif event is InputEventMouseMotion and dragging:\n        var motion := event as InputEventMouseMotion\n        var d: Vector2 = motion.position - drag_last\n        drag_last = motion.position\n        _rotate_character(d)\n"""
if old in text:
    text = text.replace(old, new)
text = text.replace("ALPHA 0.1  •  MODELO 3D ORIGINAL", "ALPHA 0.2  •  ITERACIÓN 1: SILUETA Y ROSTRO")
main.write_text(text, encoding="utf-8")

preset = root / "export_presets.cfg"
text = preset.read_text(encoding="utf-8")
text = text.replace('gradle_build/min_sdk="24"\n', "")
text = text.replace('gradle_build/target_sdk="35"\n', "")
text = text.replace('architectures/armeabi-v7a=false', 'architectures/armeabi-v7a=true')
text = text.replace('version/code=1', 'version/code=3')
text = text.replace('version/code=2', 'version/code=3')
text = text.replace('version/name="0.1.0-alpha"', 'version/name="0.2.0-alpha"')
text = text.replace('version/name="0.1.1-alpha"', 'version/name="0.2.0-alpha"')
preset.write_text(text, encoding="utf-8")

project = root / "project.godot"
text = project.read_text(encoding="utf-8")
setting = "textures/vram_compression/import_etc2_astc=true"
if setting not in text:
    anchor = 'renderer/rendering_method.mobile="gl_compatibility"\n'
    if anchor not in text:
        raise RuntimeError("Rendering anchor was not found in project.godot")
    text = text.replace(anchor, anchor + setting + "\n")
project.write_text(text, encoding="utf-8")

# ---------------------------------------------------------------------------
# Iteration 1: mascot silhouette, capybara facial proportions and verification
# renders. This patch modifies the reproducible Blender generator, not a binary.
# ---------------------------------------------------------------------------
model = root / "tools" / "create_capybara.py"
s = model.read_text(encoding="utf-8")
s = s.replace("Capibara Alpha 0.1 — modelo procedural original", "Capibara Alpha 0.2 — Iteración 1: silueta y rostro")

s = s.replace(
    "MAT_EYE = mat_principled('Eyes', srgb('#120B08'), 0.17, specular=0.65)\n"
    "MAT_EYE_BROWN = mat_principled('Iris_Warm', srgb('#5A2D12'), 0.25, specular=0.62)",
    "MAT_SCLERA = mat_principled('Sclera_Warm', srgb('#E8D7B8'), 0.24, specular=0.58)\n"
    "MAT_EYE = mat_principled('Pupil_Black', srgb('#0A0705'), 0.12, specular=0.72)\n"
    "MAT_EYE_BROWN = mat_principled('Iris_Warm', srgb('#6E3515'), 0.20, specular=0.68)"
)
s = s.replace(
    "MAT_FLOWER = mat_principled('Flower', srgb('#F4B94B'), 0.65)",
    "MAT_FLOWER = mat_principled('Flower', srgb('#F4B94B'), 0.65)\n"
    "MAT_HAT = mat_principled('Explorer_Hat', srgb('#7C7A3A'), 0.82)\n"
    "MAT_HAT_BAND = mat_principled('Hat_Band', srgb('#4C321E'), 0.70)\n"
    "MAT_TONGUE = mat_principled('Tongue', srgb('#B85D62'), 0.55)"
)

# Body and head proportions.
s = s.replace("head_pivot.location=(0,0,2.55)", "head_pivot.location=(0,0,2.48)")
s = s.replace("body = add_uv('Body', (0,0,1.55), (1.03,0.72,1.32)", "body = add_uv('Body', (0,0,1.50), (1.00,0.73,1.25)")
s = s.replace("belly = add_uv('Belly', (0,-0.31,1.42), (0.78,0.47,0.98)", "belly = add_uv('Belly', (0,-0.34,1.39), (0.76,0.45,0.93)")
s = s.replace("chest = add_uv('Chest', (0,-0.08,2.28), (0.82,0.61,0.72)", "chest = add_uv('Chest', (0,-0.10,2.22), (0.84,0.62,0.70)")
s = s.replace("head = add_uv('Head', (0,0,3.04), (1.07,0.78,0.91)", "head = add_uv('Head', (0,-0.01,3.02), (1.10,0.81,0.91)")
s = s.replace("head.parent=head_pivot; head.location.z -= 2.55", "head.parent=head_pivot; head.location.z -= 2.48")
s = s.replace("forehead = add_uv('Forehead', (0,0.04,3.48), (0.88,0.67,0.56)", "forehead = add_uv('Forehead', (0,0.05,3.45), (0.91,0.68,0.53)")
s = s.replace("forehead.parent=head_pivot; forehead.location.z -= 2.55", "forehead.parent=head_pivot; forehead.location.z -= 2.48")

start_marker = "# cheeks and muzzle are slightly forward (negative Y toward camera)"
end_marker = "# Eyebrows for expression"
if start_marker not in s or end_marker not in s:
    raise RuntimeError("Iteration 1 face markers were not found")
start = s.index(start_marker)
end = s.index(end_marker)
face = '''# Refined cheeks and broad capybara muzzle — Iteración 1
cheek_l = add_uv('Cheek_L', (-0.36,-0.62,2.93), (0.53,0.40,0.43), MAT_MUZZLE, segments=56, rings=34)
cheek_l.parent=head_pivot; cheek_l.location.z -= 2.48
cheek_r = add_uv('Cheek_R', (0.36,-0.62,2.93), (0.53,0.40,0.43), MAT_MUZZLE, segments=56, rings=34)
cheek_r.parent=head_pivot; cheek_r.location.z -= 2.48
snout = add_uv('Snout', (0,-0.79,3.05), (0.62,0.29,0.37), MAT_MUZZLE, segments=56, rings=34)
snout.parent=head_pivot; snout.location.z -= 2.48
nose = add_uv('Nose', (0,-1.03,3.18), (0.36,0.16,0.22), MAT_NOSE, segments=52, rings=32)
nose.parent=head_pivot; nose.location.z -= 2.48
for side, x in [('L',-0.13),('R',0.13)]:
    nostril = add_uv(f'Nostril_{side}', (x,-1.177,3.20), (0.055,0.022,0.038), MAT_EYE, segments=28, rings=18)
    nostril.parent=head_pivot; nostril.location.z -= 2.48

# Small rounded ears preserve the capybara identity.
for side, x in [('L',-0.76),('R',0.76)]:
    pivot = bpy.data.objects.new(f'Ear_{side}_Pivot', None); model_col.objects.link(pivot); pivot.parent=head_pivot; pivot.location=(x,0.04,0.91)
    ear = add_uv(f'Ear_{side}', (x,0.03,3.53), (0.27,0.20,0.31), MAT_FUR_DARK, segments=44, rings=28, rot=(math.radians(8),0,math.radians(10 if side=='L' else -10)))
    ear.parent=pivot; ear.location=(0,0,0.10)
    inner = add_uv(f'EarInner_{side}', (x,-0.14,3.54), (0.17,0.045,0.20), MAT_INNER_EAR, segments=36, rings=24)
    inner.parent=pivot; inner.location=(0,-0.15,0.11)

# Large glossy eyes with a warm rim, iris, pupil and two catchlights.
for side, x in [('L',-0.45),('R',0.45)]:
    eye = add_uv(f'Eye_{side}', (x,-0.70,3.34), (0.255,0.125,0.305), MAT_SCLERA, segments=56, rings=36)
    eye.parent=head_pivot; eye.location.z -= 2.48
    iris = add_uv(f'Iris_{side}', (x,-0.807,3.34), (0.175,0.042,0.220), MAT_EYE_BROWN, segments=48, rings=30)
    iris.parent=head_pivot; iris.location.z -= 2.48
    pupil = add_uv(f'Pupil_{side}', (x,-0.845,3.34), (0.112,0.028,0.155), MAT_EYE, segments=44, rings=28)
    pupil.parent=head_pivot; pupil.location.z -= 2.48
    glint = add_uv(f'EyeGlint_{side}', (x-0.055,-0.875,3.435), (0.062,0.020,0.078), MAT_WHITE, segments=28, rings=20)
    glint.parent=head_pivot; glint.location.z -= 2.48
    glint2 = add_uv(f'EyeGlintSmall_{side}', (x+0.052,-0.876,3.285), (0.026,0.012,0.035), MAT_WHITE, segments=24, rings=16)
    glint2.parent=head_pivot; glint2.location.z -= 2.48
    lid = add_uv(f'Eyelid_{side}', (x,-0.825,3.515), (0.265,0.050,0.105), MAT_FUR, segments=44, rings=26)
    lid.parent=head_pivot; lid.location.z -= 2.48

'''
s = s[:start] + face + s[end:]

s = s.replace("add_curve('Brow_L', [(-0.65,-0.805,3.62),(-0.43,-0.86,3.68),(-0.20,-0.80,3.62)], 0.035", "add_curve('Brow_L', [(-0.66,-0.804,3.61),(-0.44,-0.855,3.67),(-0.22,-0.815,3.62)], 0.026")
s = s.replace("add_curve('Brow_R', [(0.20,-0.80,3.62),(0.43,-0.86,3.68),(0.65,-0.805,3.62)], 0.035", "add_curve('Brow_R', [(0.22,-0.815,3.62),(0.44,-0.855,3.67),(0.66,-0.804,3.61)], 0.026")
s = s.replace("o.location.z -= 2.55", "o.location.z -= 2.48")
s = s.replace("mouth = add_uv('Mouth', (0,-0.93,2.77), (0.40,0.095,0.25)", "mouth = add_uv('Mouth', (0,-0.94,2.77), (0.38,0.090,0.235)")
s = s.replace("mouth.parent=head_pivot; mouth.location.z -= 2.55", "mouth.parent=head_pivot; mouth.location.z -= 2.48")
s = s.replace("smile_l.location.z -= 2.55", "smile_l.location.z -= 2.48")
s = s.replace("smile_r.location.z -= 2.55", "smile_r.location.z -= 2.48")
s = s.replace("(0.135,0.065,0.22)", "(0.115,0.055,0.185)")
s = s.replace("tooth.location.z -= 2.55", "tooth.location.z -= 2.48")
s = s.replace("blush.location.z-=2.55", "blush.location.z-=2.48")

arms_marker = "    tooth.parent=head_pivot; tooth.location.z -= 2.48\n\n# Arms and paws"
if arms_marker not in s:
    raise RuntimeError("Mouth/accessory insertion marker was not found")
accessories = """    tooth.parent=head_pivot; tooth.location.z -= 2.48

tongue = add_uv('Tongue', (0,-1.015,2.68), (0.20,0.040,0.075), MAT_TONGUE, segments=36, rings=22)
tongue.parent=head_pivot; tongue.location.z -= 2.48

# Explorer hat placeholder fixes the intended silhouette. Fine details come later.
bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, location=(0,0.02,3.98))
hat_crown=bpy.context.object; hat_crown.name='Hat_Crown'; hat_crown.scale=(0.88,0.73,0.30); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); smooth(hat_crown); hat_crown.data.materials.append(MAT_HAT); move_to_collection(hat_crown,model_col); hat_crown.parent=head_pivot; hat_crown.location.z-=2.48
bpy.ops.mesh.primitive_torus_add(major_radius=0.82, minor_radius=0.105, major_segments=72, minor_segments=20, location=(0,-0.01,3.83))
hat_brim=bpy.context.object; hat_brim.name='Hat_Brim'; hat_brim.scale=(1.14,0.96,0.70); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); smooth(hat_brim); hat_brim.data.materials.append(MAT_HAT); move_to_collection(hat_brim,model_col); hat_brim.parent=head_pivot; hat_brim.location.z-=2.48
bpy.ops.mesh.primitive_torus_add(major_radius=0.69, minor_radius=0.045, major_segments=72, minor_segments=16, location=(0,-0.01,3.88))
hat_band=bpy.context.object; hat_band.name='Hat_Band'; hat_band.scale=(1.08,0.91,0.85); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); smooth(hat_band); hat_band.data.materials.append(MAT_HAT_BAND); move_to_collection(hat_band,model_col); hat_band.parent=head_pivot; hat_band.location.z-=2.48

# Arms and paws"""
s = s.replace(arms_marker, accessories)
s = s.replace("obj['alpha_version'] = '0.1.0'", "obj['alpha_version'] = '0.2.0-iter1'")

# Preserve legacy file names required by the build workflow while adding four
# explicit verification captures.
render_start = s.index("# Render preview")
render_end = s.index("# Export only model collection")
render_block = '''# Render verification captures: front, profile, three-quarter and face close-up
def render_view(filename, location, target=(0,0,2.15), lens=58):
    cam.location=location
    cam.data.lens=lens
    look_at(cam,target)
    scene.render.resolution_x=1024
    scene.render.resolution_y=1024
    scene.render.filepath=os.path.join(OUT_DIR,filename)
    bpy.ops.render.render(write_still=True)

render_view('capibara_iter1_front.png',(0,-9.2,3.05),(0,0,2.10),62)
render_view('capibara_iter1_profile.png',(8.7,-0.2,3.05),(0,0,2.10),62)
render_view('capibara_alpha_preview.png',(5.8,-8.6,3.55),(0,0,2.15),58)
render_view('capibara_iter1_closeup.png',(3.3,-6.5,3.75),(0,-0.05,2.95),72)

scene.render.resolution_x=512
scene.render.resolution_y=512
scene.render.filepath=os.path.join(PROJECT_DIR,'icon.png')
bpy.ops.render.render(write_still=True)

'''
s = s[:render_start] + render_block + s[render_end:]
s = s.replace("print('PREVIEW', scene.render.filepath)", "print('PREVIEWS', os.path.join(OUT_DIR,'capibara_iter1_front.png'), os.path.join(OUT_DIR,'capibara_iter1_profile.png'), os.path.join(OUT_DIR,'capibara_alpha_preview.png'), os.path.join(OUT_DIR,'capibara_iter1_closeup.png'))")
model.write_text(s, encoding="utf-8")

print("CAPIBARA_ITERATION_1_PATCH_OK")
