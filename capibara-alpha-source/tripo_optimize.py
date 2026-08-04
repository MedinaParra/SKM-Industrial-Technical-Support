import bpy
import math
import os
import sys
from mathutils import Vector

ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
if len(ARGS) < 3:
    raise SystemExit('Usage: blender -b --python tripo_optimize.py -- input.glb output.glb output_dir')
INPUT_GLB, OUTPUT_GLB, OUTPUT_DIR = map(os.path.abspath, ARGS[:3])
os.makedirs(OUTPUT_DIR, exist_ok=True)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

bpy.ops.import_scene.gltf(filepath=INPUT_GLB, import_pack_images=True)
mesh_objects = [o for o in bpy.context.scene.objects if o.type == 'MESH']
if not mesh_objects:
    raise RuntimeError('The GLB did not import any mesh objects')

bpy.ops.object.select_all(action='DESELECT')
for obj in mesh_objects:
    obj.select_set(True)
bpy.context.view_layer.objects.active = mesh_objects[0]
bpy.ops.object.join()
character = bpy.context.object
character.name = 'CapibaraTripo'
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

def mesh_world_vertices(obj):
    mw = obj.matrix_world
    return [mw @ v.co for v in obj.data.vertices]

verts = mesh_world_vertices(character)
min_z = min(v.z for v in verts)
max_z = max(v.z for v in verts)
height = max_z - min_z
all_y = sum(v.y for v in verts) / len(verts)
head_verts = [v for v in verts if v.z > min_z + height * 0.58]
head_y = sum(v.y for v in head_verts) / max(1, len(head_verts))
if head_y > all_y:
    character.rotation_euler.z += math.pi
    bpy.context.view_layer.objects.active = character
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

verts = mesh_world_vertices(character)
min_x, max_x = min(v.x for v in verts), max(v.x for v in verts)
min_y, max_y = min(v.y for v in verts), max(v.y for v in verts)
min_z, max_z = min(v.z for v in verts), max(v.z for v in verts)
scale = 2.85 / max(1e-6, max_z - min_z)
character.scale = (scale, scale, scale)
bpy.context.view_layer.objects.active = character
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
verts = mesh_world_vertices(character)
min_x, max_x = min(v.x for v in verts), max(v.x for v in verts)
min_y, max_y = min(v.y for v in verts), max(v.y for v in verts)
min_z, max_z = min(v.z for v in verts), max(v.z for v in verts)
character.location += Vector((-(min_x + max_x) * 0.5, -(min_y + max_y) * 0.5, -min_z))
bpy.context.view_layer.update()

triangles_before = sum(len(p.vertices) - 2 for p in character.data.polygons)
target_triangles = 145_000
ratio = min(1.0, target_triangles / max(1, triangles_before))
if ratio < 0.98:
    dec = character.modifiers.new('Mobile_Decimate', 'DECIMATE')
    dec.decimate_type = 'COLLAPSE'
    dec.ratio = ratio
    dec.use_collapse_triangulate = True
    bpy.context.view_layer.objects.active = character
    bpy.ops.object.modifier_apply(modifier=dec.name)

for image in bpy.data.images:
    if image.source == 'FILE' or image.packed_file is not None:
        try:
            if max(image.size[:]) > 2048:
                image.scale(2048, 2048)
            image.pack()
        except Exception as exc:
            print('Texture warning:', image.name, exc)

verts = mesh_world_vertices(character)
min_x, max_x = min(v.x for v in verts), max(v.x for v in verts)
min_y, max_y = min(v.y for v in verts), max(v.y for v in verts)
min_z, max_z = min(v.z for v in verts), max(v.z for v in verts)
height = max_z - min_z
head = [v for v in verts if v.z > min_z + height * 0.58]
front_y = min(v.y for v in head)
head_min_x, head_max_x = min(v.x for v in head), max(v.x for v in head)
head_width = head_max_x - head_min_x
face_z = min_z + height * 0.77
face_height = height * 0.34
face_width = head_width * 0.82
face_center_x = (head_min_x + head_max_x) * 0.5

anchors = {
    'FaceAnchor': (face_center_x, front_y - 0.025, face_z),
    'FaceLeft': (face_center_x - face_width * 0.5, front_y - 0.025, face_z),
    'FaceRight': (face_center_x + face_width * 0.5, front_y - 0.025, face_z),
    'FaceTop': (face_center_x, front_y - 0.025, face_z + face_height * 0.5),
    'FaceBottom': (face_center_x, front_y - 0.025, face_z - face_height * 0.5),
}
for name, loc in anchors.items():
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = 'PLAIN_AXES'
    empty.empty_display_size = 0.06
    empty.location = loc
    bpy.context.scene.collection.objects.link(empty)

character['source'] = 'User supplied Tripo GLB'
character['triangles_before'] = int(triangles_before)
character['target_triangles'] = int(target_triangles)
character['facial_system'] = 'Godot runtime overlay alpha'

def mat(name, color, roughness=0.8):
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*color, 1.0)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    return material

floor_mat = mat('Studio Floor', (0.08, 0.14, 0.10), 0.95)
bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=2.35, depth=0.18, location=(0, 0, -0.10))
floor = bpy.context.object
floor.name = 'PreviewFloor'
floor.data.materials.append(floor_mat)

world = bpy.context.scene.world or bpy.data.worlds.new('Capibara World')
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.018, 0.035, 0.027, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.42

def area(name, loc, energy, size, color):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = energy
    data.shape = 'DISK'
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    obj.location = loc
    bpy.context.scene.collection.objects.link(obj)
    direction = Vector((0, 0, 1.4)) - obj.location
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

area('Key', (-3.4, -4.5, 5.2), 950, 4.0, (1.0, 0.73, 0.48))
area('Fill', (3.2, -2.0, 3.5), 620, 3.4, (0.55, 0.72, 1.0))
area('Rim', (1.2, 4.0, 4.6), 850, 3.2, (0.48, 1.0, 0.68))

cam_data = bpy.data.cameras.new('Camera')
cam = bpy.data.objects.new('Camera', cam_data)
bpy.context.scene.collection.objects.link(cam)
bpy.context.scene.camera = cam
cam_data.lens = 58

def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = 768
scene.render.resolution_y = 768
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.render.image_settings.color_mode = 'RGBA'
scene.view_settings.look = 'AgX - Medium High Contrast'

views = {
    'front': (0.0, -5.2, 2.15),
    'three_quarter': (3.35, -4.0, 2.15),
    'profile': (5.1, 0.0, 2.15),
    'rear': (0.0, 5.2, 2.15),
}
for name, pos in views.items():
    cam.location = pos
    look_at(cam, (0, 0, 1.38))
    scene.render.filepath = os.path.join(OUTPUT_DIR, f'capibara_tripo_{name}.png')
    bpy.ops.render.render(write_still=True)

bpy.data.objects.remove(floor, do_unlink=True)
for obj in list(bpy.context.scene.objects):
    if obj.type in {'LIGHT', 'CAMERA'}:
        bpy.data.objects.remove(obj, do_unlink=True)

blend_path = os.path.join(OUTPUT_DIR, 'capibara_tripo_mobile.blend')
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
bpy.ops.export_scene.gltf(
    filepath=OUTPUT_GLB,
    export_format='GLB',
    export_apply=True,
    export_animations=False,
    export_materials='EXPORT',
    export_image_format='AUTO',
    export_extras=True,
)

triangles_after = sum(len(p.vertices) - 2 for p in character.data.polygons)
with open(os.path.join(OUTPUT_DIR, 'model_report.txt'), 'w', encoding='utf-8') as report:
    report.write(f'Triangles before: {triangles_before}\n')
    report.write(f'Triangles after: {triangles_after}\n')
    report.write(f'Face width: {face_width:.4f}\n')
    report.write(f'Face height: {face_height:.4f}\n')
    report.write('Expressions: neutral, feliz, sorpresa, sueno, enojado, guino\n')
print('TRIPO_CAPIBARA_MOBILE_OK', OUTPUT_GLB, triangles_before, triangles_after)
