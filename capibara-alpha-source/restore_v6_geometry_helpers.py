from pathlib import Path
import sys

if len(sys.argv) < 3:
    raise SystemExit("usage: restore_v6_geometry_helpers.py <v6_target.py> <v5_source.py>")

target_path = Path(sys.argv[1])
source_path = Path(sys.argv[2])
target = target_path.read_text(encoding="utf-8")
source = source_path.read_text(encoding="utf-8")

helper_start = source.index('def finish_mesh(')
helper_end = source.index('# -----------------------------------------------------------------------------\n# Clean continuous body and head', helper_start)
helpers = source[helper_start:helper_end]
helpers = helpers.replace('px = math.copysign(abs(c) ** 0.78, c)',
                          'px = math.copysign(abs(c) ** 0.88, c)', 1)
helpers = helpers.replace('pz = math.copysign(abs(s) ** 0.84, s)',
                          'pz = math.copysign(abs(s) ** 0.90, s)', 1)

anchor = '# -----------------------------------------------------------------------------\n# Clean continuous body and head'
if anchor not in target:
    raise RuntimeError('V6 body anchor not found')
if 'def loft_z(' in target:
    raise RuntimeError('V6 helper block was not removed; repair no longer required')

target = target.replace(anchor, helpers + anchor, 1)
target_path.write_text(target, encoding="utf-8")
print('CAPIBARA_V6_GEOMETRY_HELPERS_RESTORED', target_path)
