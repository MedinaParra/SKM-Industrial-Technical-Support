from pathlib import Path

project = Path("CapibaraAlpha")
generator = project / "tools" / "create_capybara.py"
if not generator.is_file():
    raise RuntimeError("Capibara generator was not found")

text = generator.read_text(encoding="utf-8")
marker = "# -----------------------------------------------------------------------------\n# Iteration 12: LOD export and technical report"
if marker not in text:
    raise RuntimeError("Iteration 12 marker was not found in generator")
head = text[:text.index(marker)]
tail = r'''# -----------------------------------------------------------------------------
# Iteration 12: technical report. GLB exports run in isolated Blender processes
# from the saved .blend to avoid exporter instability after long render sessions.
# -----------------------------------------------------------------------------

def metrics_for(col):
    meshes = [o for o in col.all_objects if o.type == "MESH"]
    triangles = 0
    for obj in meshes:
        obj.data.calc_loop_triangles()
        triangles += len(obj.data.loop_triangles)
    return {
        "objects": len(col.all_objects),
        "meshes": len(meshes),
        "vertices": sum(len(o.data.vertices) for o in meshes),
        "triangles": triangles,
        "materials": len({m.name for o in meshes for m in o.data.materials if m}),
    }

shape_count = 0
for obj in face_meshes:
    if getattr(obj.data, "shape_keys", None):
        shape_count += max(0, len(obj.data.shape_keys.key_blocks) - 1)
base_metrics = metrics_for(MODEL)
report = {
    "version": VERSION,
    "iterations_completed": ITERATIONS,
    "lod0": base_metrics,
    "lod1_target_ratio": 0.58,
    "lod2_target_ratio": 0.30,
    "bones": len(ARM.data.bones),
    "morph_targets": shape_count,
    "expressions": len(EXPRESSIONS),
    "presentation_animations": len(ACTIONS),
    "android_abis": ["armeabi-v7a", "arm64-v8a"],
    "renderer": "Godot GL Compatibility",
    "export_strategy": "isolated Blender processes",
}
with open(os.path.join(OUT_DIR, "capibara_beta_validation.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
with open(os.path.join(OUT_DIR, "ITERATIONS_COMPLETED.txt"), "w", encoding="utf-8") as f:
    for i, name in enumerate(ITERATIONS, start=1):
        f.write(f"{i:02d}. {name}: IMPLEMENTADA\n")

print("CAPIBARA_BETA_MODEL_AND_RENDERS_OK")
print("VERSION", VERSION)
print("BLEND", blend_path)
print("REPORT", json.dumps(report, ensure_ascii=False))
'''
generator.write_text(head + tail, encoding="utf-8")

exporter = project / "tools" / "export_capybara_glb.py"
exporter.write_text(r'''import bpy
import os
import sys
import json


def parse_args():
    args = sys.argv
    if "--" in args:
        args = args[args.index("--") + 1:]
    if len(args) < 2:
        raise RuntimeError("Usage: export_capybara_glb.py OUTPUT_GLB RATIO")
    return os.path.abspath(args[0]), float(args[1])


OUTPUT, RATIO = parse_args()
MODEL = bpy.data.collections.get("CAPIBARA_BETA")
if MODEL is None:
    raise RuntimeError("CAPIBARA_BETA collection was not found in saved blend")

# Remove studio-only objects and collections to reduce glTF exporter memory.
for col_name in ("STUDIO", "CAPIBARA_BETA_LOD1", "CAPIBARA_BETA_LOD2"):
    col = bpy.data.collections.get(col_name)
    if col and col != MODEL:
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(col)

# Lower LODs decimate only rigid meshes. Skinned and facial meshes remain intact
# so the silhouette, expressions and armature deformation are not damaged.
if RATIO < 0.999:
    for obj in list(MODEL.all_objects):
        if obj.type != "MESH" or len(obj.data.polygons) < 180:
            continue
        if getattr(obj.data, "shape_keys", None):
            continue
        if any(mod.type == "ARMATURE" for mod in obj.modifiers):
            continue
        bpy.context.view_layer.objects.active = obj
        obj.hide_set(False)
        obj.select_set(True)
        mod = obj.modifiers.new("LOD_Decimate", "DECIMATE")
        mod.ratio = RATIO
        mod.use_collapse_triangulate = True
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except RuntimeError:
            if mod.name in obj.modifiers:
                obj.modifiers.remove(mod)
        obj.select_set(False)

bpy.ops.object.select_all(action="DESELECT")
selected = []
for obj in MODEL.all_objects:
    if obj.type in {"MESH", "ARMATURE", "EMPTY"}:
        obj.hide_set(False)
        obj.hide_viewport = False
        obj.hide_render = False
        obj.select_set(True)
        selected.append(obj)
if not selected:
    raise RuntimeError("No exportable objects were selected")
arm = next((o for o in selected if o.type == "ARMATURE"), selected[0])
bpy.context.view_layer.objects.active = arm

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
kwargs = dict(
    filepath=OUTPUT,
    export_format="GLB",
    use_selection=True,
    export_yup=True,
    export_apply=False,
    export_materials="EXPORT",
    export_image_format="AUTO",
    export_texcoords=True,
    export_normals=True,
    export_tangents=False,
    export_attributes=True,
    export_cameras=False,
    export_lights=False,
    export_extras=True,
    export_animations=False,
    export_morph=True,
    export_morph_normal=False,
    export_morph_tangent=False,
    export_skins=True,
)
try:
    bpy.ops.export_scene.gltf(**kwargs)
except TypeError:
    for key in ("export_morph_normal", "export_morph_tangent", "export_skins"):
        kwargs.pop(key, None)
    bpy.ops.export_scene.gltf(**kwargs)

if not os.path.isfile(OUTPUT) or os.path.getsize(OUTPUT) < 1024:
    raise RuntimeError(f"Invalid GLB output: {OUTPUT}")
print("CAPIBARA_GLB_EXPORT_OK", json.dumps({"path": OUTPUT, "ratio": RATIO, "bytes": os.path.getsize(OUTPUT)}))
''', encoding="utf-8")

print("CAPIBARA_BETA_EXPORT_FIX_OK")
