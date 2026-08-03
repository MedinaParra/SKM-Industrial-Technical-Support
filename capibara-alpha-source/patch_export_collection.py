from pathlib import Path

path = Path("CapibaraAlpha/tools/export_capybara_glb.py")
text = path.read_text(encoding="utf-8")
old = '''MODEL = bpy.data.collections.get("CAPIBARA_BETA")
if MODEL is None:
    raise RuntimeError("CAPIBARA_BETA collection was not found in saved blend")'''
new = '''MODEL = (
    bpy.data.collections.get("CAPIBARA_BETA_LOD0")
    or bpy.data.collections.get("CAPIBARA_BETA")
)
if MODEL is None:
    excluded = {"Collection", "STUDIO", "CAPIBARA_BETA_LOD1", "CAPIBARA_BETA_LOD2"}
    candidates = [c for c in bpy.data.collections if c.name not in excluded and len(c.all_objects) > 0]
    if candidates:
        MODEL = max(candidates, key=lambda c: len(c.all_objects))
if MODEL is None:
    available = [c.name for c in bpy.data.collections]
    raise RuntimeError(f"Capibara model collection was not found. Available: {available}")
print("CAPIBARA_EXPORT_COLLECTION", MODEL.name, len(MODEL.all_objects))'''
if old not in text:
    raise RuntimeError("Expected collection lookup block was not found")
path.write_text(text.replace(old, new), encoding="utf-8")
print("CAPIBARA_EXPORT_COLLECTION_PATCH_OK")
