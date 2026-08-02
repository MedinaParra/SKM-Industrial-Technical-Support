from pathlib import Path

root = Path("CapibaraAlpha")

main = root / "main.gd"
text = main.read_text(encoding="utf-8")
old = """    elif event is InputEventMouseMotion and dragging:\n        var d := event.position - drag_last\n        drag_last = event.position\n        _rotate_character(d)\n"""
new = """    elif event is InputEventMouseMotion and dragging:\n        var motion := event as InputEventMouseMotion\n        var d: Vector2 = motion.position - drag_last\n        drag_last = motion.position\n        _rotate_character(d)\n"""
if old not in text and new not in text:
    raise RuntimeError("Expected mouse-motion block was not found in main.gd")
main.write_text(text.replace(old, new), encoding="utf-8")

preset = root / "export_presets.cfg"
text = preset.read_text(encoding="utf-8")
text = text.replace('gradle_build/min_sdk="24"\n', "")
text = text.replace('gradle_build/target_sdk="35"\n', "")
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

print("CAPIBARA_SOURCE_FIXES_OK")
