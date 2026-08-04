from pathlib import Path

path = Path("CapibaraAlpha/main.gd")
text = path.read_text(encoding="utf-8")

text = text.replace(
    'const MODEL_SCENE := preload("res://assets/capibara_alpha.glb")',
    'const MODEL_PATH: String = "res://assets/capibara_alpha.glb"'
)

text = text.replace(
    '''    var instance := MODEL_SCENE.instantiate()
    instance.name = "CapibaraModel"
    character_holder.add_child(instance)
    model_root = instance
    animation_player = instance.find_child("AnimationPlayer", true, false) as AnimationPlayer''',
    '''    var model_scene: PackedScene = load(MODEL_PATH) as PackedScene
    if model_scene == null:
        push_error("No se pudo cargar el modelo del capibara: " + MODEL_PATH)
        return
    var instance: Node = model_scene.instantiate()
    instance.name = "CapibaraModel"
    character_holder.add_child(instance)
    model_root = instance
    animation_player = instance.find_child("AnimationPlayer", true, false) as AnimationPlayer'''
)

text = text.replace(
    '    var idx := node.mesh.find_blend_shape_by_name(blend_name)',
    '    var idx: int = node.mesh.find_blend_shape_by_name(StringName(blend_name))'
)

text = text.replace(
    '''    elif event is InputEventScreenDrag:
        var d := event.position - drag_last
        drag_last = event.position
        _rotate_character(d)''',
    '''    elif event is InputEventScreenDrag:
        var drag_event := event as InputEventScreenDrag
        var d: Vector2 = drag_event.position - drag_last
        drag_last = drag_event.position
        _rotate_character(d)'''
)

required = [
    'const MODEL_PATH: String',
    'var model_scene: PackedScene',
    'var instance: Node',
    'var idx: int',
    'var drag_event := event as InputEventScreenDrag',
]
missing = [item for item in required if item not in text]
if missing:
    raise RuntimeError(f"Godot patch incomplete: {missing}")

path.write_text(text, encoding="utf-8")
print("CAPIBARA_GODOT_STATIC_TYPES_OK")
