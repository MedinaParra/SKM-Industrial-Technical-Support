from pathlib import Path
import base64
import io
import runpy
import tarfile

project = Path("CapibaraAlpha")
archive_dir = Path("capibara-alpha-source/production_overlay_archive")
if not project.exists() or not archive_dir.exists():
    raise RuntimeError("Restored project or production overlay archive was not found")

parts = sorted(archive_dir.glob("part_*.b64"))
if not parts:
    raise RuntimeError("No production overlay archive parts were found")

encoded = "".join(part.read_text(encoding="ascii").strip() for part in parts)
archive_bytes = base64.b64decode(encoded, validate=True)
with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
    root = project.resolve()
    for member in archive.getmembers():
        target = (root / member.name).resolve()
        if root not in target.parents and target != root:
            raise RuntimeError(f"Unsafe archive path: {member.name}")
    archive.extractall(project, filter="data")

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

# Apply the Godot static-typing/runtime loading correction as part of the main
# overlay process. This keeps the full build and the fast diagnostic identical.
godot_patch = Path("capibara-alpha-source/patch_godot_beta.py")
if godot_patch.is_file():
    runpy.run_path(str(godot_patch), run_name="__main__")
else:
    raise RuntimeError("Godot beta patch was not found")

required = [
    project / "tools/create_capybara.py",
    project / "main.gd",
    project / "shaders/fur_mobile.gdshader",
    project / "README_BETA_1_0.md",
]
missing = [str(path) for path in required if not path.is_file()]
if missing:
    raise RuntimeError(f"Incomplete production overlay: {missing}")

print("CAPIBARA_12_ITERATIONS_OVERLAY_OK")
