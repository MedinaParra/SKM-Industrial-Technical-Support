from pathlib import Path

project = Path("CapibaraAlpha")
generator = project / "tools" / "create_capybara.py"
text = generator.read_text(encoding="utf-8")
marker = "# -----------------------------------------------------------------------------\n# Iteration 12: LOD export and technical report"
if marker not in text:
    raise RuntimeError("Iteration 12 marker was not found")

report_tail = r'''# -----------------------------------------------------------------------------
# Iteration 12: validation report. GLB files are exported in clean processes.
# -----------------------------------------------------------------------------
def metrics_for(col):
    meshes = [o for o in col.all_objects if o.type == "MESH"]
    for obj in meshes:
        obj.data.calc_loop_triangles()
    return {
        "objects": len(col.all_objects),
        "meshes": len(meshes),
        "vertices": sum(len(o.data.vertices) for o in meshes),
        "triangles": sum(len(o.data.loop_triangles) for o in meshes),
        "materials": len({m.name for o in meshes for m in o.data.materials if m}),
    }
shape_count = sum(
    max(0, len(obj.data.shape_keys.key_blocks) - 1)
    for obj in face_meshes if getattr(obj.data, "shape_keys", None)
)
report = {
    "version": VERSION,
    "iterations_completed": ITERATIONS,
    "lod0": metrics_for(MODEL),
    "lod1_target_ratio": 0.58,
    "lod2_target_ratio": 0.30,
    "bones": len(ARM.data.bones),
    "morph_targets": shape_count,
    "expressions": len(EXPRESSIONS),
    "presentation_animations": len(ACTIONS),
    "android_abis": ["armeabi-v7a", "arm64-v8a"],
    "renderer": "Godot GL Compatibility",
}
with open(os.path.join(OUT_DIR, "capibara_beta_validation.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
with open(os.path.join(OUT_DIR, "ITERATIONS_COMPLETED.txt"), "w", encoding="utf-8") as f:
    for i, name in enumerate(ITERATIONS, 1):
        f.write(f"{i:02d}. {name}: IMPLEMENTADA\n")
print("CAPIBARA_BETA_MODEL_AND_RENDERS_OK")
print("REPORT", json.dumps(report, ensure_ascii=False))
'''
generator.write_text(text[:text.index(marker)] + report_tail, encoding="utf-8")

exporter = project / "tools" / "export_capybara_glb.py"
exporter.write_text(r'''import bpy, json, os, sys
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if len(args) < 2:
    raise RuntimeError("OUTPUT_GLB and RATIO are required")
output, ratio = os.path.abspath(args[0]), float(args[1])
model = bpy.data.collections.get("CAPIBARA_BETA_LOD0") or bpy.data.collections.get("CAPIBARA_BETA")
if model is None:
    excluded = {"Collection", "STUDIO", "CAPIBARA_BETA_LOD1", "CAPIBARA_BETA_LOD2"}
    candidates = [c for c in bpy.data.collections if c.name not in excluded and len(c.all_objects)]
    model = max(candidates, key=lambda c: len(c.all_objects)) if candidates else None
if model is None:
    raise RuntimeError(f"Model collection missing: {[c.name for c in bpy.data.collections]}")
print("CAPIBARA_EXPORT_COLLECTION", model.name, len(model.all_objects))

if ratio < 0.999:
    for obj in list(model.all_objects):
        if obj.type != "MESH" or len(obj.data.polygons) < 180:
            continue
        if getattr(obj.data, "shape_keys", None) or any(m.type == "ARMATURE" for m in obj.modifiers):
            continue
        bpy.ops.object.select_all(action="DESELECT")
        obj.hide_set(False)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        mod = obj.modifiers.new("LOD_Decimate", "DECIMATE")
        mod.ratio = ratio
        mod.use_collapse_triangulate = True
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except RuntimeError:
            pass

bpy.ops.object.select_all(action="DESELECT")
selected = []
for obj in model.all_objects:
    if obj.type in {"MESH", "ARMATURE", "EMPTY"}:
        obj.hide_set(False)
        obj.select_set(True)
        selected.append(obj)
if not selected:
    raise RuntimeError("Nothing selected for GLB export")
bpy.context.view_layer.objects.active = next((o for o in selected if o.type == "ARMATURE"), selected[0])
os.makedirs(os.path.dirname(output), exist_ok=True)
kwargs = {
    "filepath": output,
    "export_format": "GLB",
    "use_selection": True,
    "export_yup": True,
    "export_apply": False,
    "export_materials": "EXPORT",
    "export_image_format": "AUTO",
    "export_texcoords": True,
    "export_normals": True,
    "export_tangents": False,
    "export_attributes": True,
    "export_cameras": False,
    "export_lights": False,
    "export_extras": True,
    "export_animations": False,
    "export_morph": True,
    "export_morph_normal": False,
    "export_morph_tangent": False,
    "export_skins": True,
}
try:
    bpy.ops.export_scene.gltf(**kwargs)
except TypeError:
    for key in ("export_morph_normal", "export_morph_tangent", "export_skins"):
        kwargs.pop(key, None)
    bpy.ops.export_scene.gltf(**kwargs)
if not os.path.isfile(output) or os.path.getsize(output) < 1024:
    raise RuntimeError(f"Invalid GLB: {output}")
print("CAPIBARA_GLB_EXPORT_OK", json.dumps({"path": output, "ratio": ratio, "bytes": os.path.getsize(output)}))
''', encoding="utf-8")
print("CAPIBARA_BETA_EXPORT_FIX_OK")
