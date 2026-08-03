from pathlib import Path
import shutil

source = Path("capibara-alpha-source/production_overlay")
project = Path("CapibaraAlpha")
if not source.exists() or not project.exists():
    raise RuntimeError("Overlay or restored CapibaraAlpha project was not found")

for item in source.rglob("*"):
    if not item.is_file():
        continue
    rel = item.relative_to(source)
    dest = project / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(item, dest)

# Project metadata.
project_file = project / "project.godot"
text = project_file.read_text(encoding="utf-8")
text = text.replace("Capibara Alpha 0.1", "Capibara Beta 1.0")
text = text.replace('config/name="Capibara Alpha"', 'config/name="Capibara 3D Beta"')
text = text.replace('environment/defaults/default_clear_color=Color(0.018, 0.038, 0.033, 1)',
                    'environment/defaults/default_clear_color=Color(0.016, 0.032, 0.026, 1)')
if 'textures/vram_compression/import_etc2_astc=true' not in text:
    text = text.replace('renderer/rendering_method.mobile="gl_compatibility"\n',
                        'renderer/rendering_method.mobile="gl_compatibility"\ntextures/vram_compression/import_etc2_astc=true\n')
project_file.write_text(text, encoding="utf-8")

preset = project / "export_presets.cfg"
text = preset.read_text(encoding="utf-8")
text = text.replace('export_path="output/Capibara-Alpha-0.1.apk"',
                    'export_path="output/Capibara-Beta-1.0.apk"')
text = text.replace('architectures/armeabi-v7a=false', 'architectures/armeabi-v7a=true')
text = text.replace('package/unique_name="com.medinaparra.capibaraalpha"',
                    'package/unique_name="com.medinaparra.capibara.beta"')
text = text.replace('package/name="Capibara Alpha"', 'package/name="Capibara 3D Beta"')
for old in ('version/code=1', 'version/code=2', 'version/code=3'):
    text = text.replace(old, 'version/code=12')
for old in ('version/name="0.1.0-alpha"', 'version/name="0.1.1-alpha"', 'version/name="0.2.0-alpha"'):
    text = text.replace(old, 'version/name="1.0.0-beta"')
preset.write_text(text, encoding="utf-8")

print("CAPIBARA_12_ITERATIONS_OVERLAY_OK")
