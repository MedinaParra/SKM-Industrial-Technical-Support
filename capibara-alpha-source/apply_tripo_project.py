from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'CapibaraAlpha')
(root / 'assets').mkdir(parents=True, exist_ok=True)
(root / 'output').mkdir(parents=True, exist_ok=True)

main_gd = r'''extends Node3D

const MODEL_SCENE: PackedScene = preload("res://assets/capibara_tripo_mobile.glb")
const EXPRESSIONS: Array[String] = ["neutral", "feliz", "sorpresa", "sueno", "enojado", "guino"]

var character_pivot: Node3D
var character_holder: Node3D
var model_root: Node3D
var face_sprite: Sprite3D
var camera: Camera3D
var status_label: Label
var current_expression: String = "neutral"
var elapsed: float = 0.0
var blink_clock: float = 2.4
var blink_remaining: float = 0.0
var dragging: bool = false
var drag_last: Vector2 = Vector2.ZERO

func _ready() -> void:
    _build_world()
    _spawn_character()
    _build_ui()
    _set_expression("neutral")

func _build_world() -> void:
    var environment_node: WorldEnvironment = WorldEnvironment.new()
    var environment: Environment = Environment.new()
    environment.background_mode = Environment.BG_COLOR
    environment.background_color = Color("102920")
    environment.background_energy_multiplier = 0.8
    environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    environment.ambient_light_color = Color("d6dfc8")
    environment.ambient_light_energy = 0.62
    environment.tonemap_mode = Environment.TONE_MAPPER_FILMIC
    environment.glow_enabled = true
    environment.glow_intensity = 0.42
    environment_node.environment = environment
    add_child(environment_node)

    var sun: DirectionalLight3D = DirectionalLight3D.new()
    sun.rotation_degrees = Vector3(-42.0, -28.0, 0.0)
    sun.light_color = Color("ffd5a3")
    sun.light_energy = 1.55
    sun.shadow_enabled = true
    add_child(sun)

    var fill: OmniLight3D = OmniLight3D.new()
    fill.position = Vector3(-2.5, 3.2, 3.2)
    fill.light_color = Color("8abaff")
    fill.light_energy = 3.8
    fill.omni_range = 8.0
    add_child(fill)

    var rim: OmniLight3D = OmniLight3D.new()
    rim.position = Vector3(2.5, 3.6, -2.2)
    rim.light_color = Color("91ffb2")
    rim.light_energy = 3.6
    rim.omni_range = 8.0
    add_child(rim)

    var ground: MeshInstance3D = MeshInstance3D.new()
    var cylinder: CylinderMesh = CylinderMesh.new()
    cylinder.top_radius = 2.55
    cylinder.bottom_radius = 2.70
    cylinder.height = 0.22
    cylinder.radial_segments = 72
    ground.mesh = cylinder
    ground.position.y = -0.13
    var ground_material: StandardMaterial3D = StandardMaterial3D.new()
    ground_material.albedo_color = Color("4e7540")
    ground_material.roughness = 0.95
    ground.material_override = ground_material
    add_child(ground)

    for index in range(8):
        var stone: MeshInstance3D = MeshInstance3D.new()
        var sphere: SphereMesh = SphereMesh.new()
        sphere.radius = 0.12 + float(index % 3) * 0.025
        sphere.height = sphere.radius * 1.15
        sphere.radial_segments = 14
        sphere.rings = 8
        stone.mesh = sphere
        var angle: float = TAU * float(index) / 8.0
        stone.position = Vector3(cos(angle) * 2.05, 0.03, sin(angle) * 2.05)
        stone.scale = Vector3(1.35, 0.65, 1.0)
        var stone_material: StandardMaterial3D = StandardMaterial3D.new()
        stone_material.albedo_color = Color("756b59")
        stone_material.roughness = 1.0
        stone.material_override = stone_material
        add_child(stone)

    camera = Camera3D.new()
    camera.position = Vector3(0.0, 1.62, 5.05)
    camera.fov = 39.0
    camera.near = 0.05
    camera.far = 50.0
    add_child(camera)
    camera.look_at(Vector3(0.0, 1.42, 0.0), Vector3.UP)

func _spawn_character() -> void:
    character_pivot = Node3D.new()
    character_pivot.name = "CharacterPivot"
    add_child(character_pivot)

    character_holder = Node3D.new()
    character_holder.name = "CharacterHolder"
    character_pivot.add_child(character_holder)

    model_root = MODEL_SCENE.instantiate() as Node3D
    model_root.name = "CapibaraTripoModel"
    character_holder.add_child(model_root)

    var face_anchor: Node3D = model_root.find_child("FaceAnchor", true, false) as Node3D
    var face_left: Node3D = model_root.find_child("FaceLeft", true, false) as Node3D
    var face_right: Node3D = model_root.find_child("FaceRight", true, false) as Node3D
    var face_top: Node3D = model_root.find_child("FaceTop", true, false) as Node3D
    var face_bottom: Node3D = model_root.find_child("FaceBottom", true, false) as Node3D

    if face_anchor == null:
        face_anchor = Node3D.new()
        face_anchor.name = "FaceAnchorFallback"
        face_anchor.position = Vector3(0.0, 2.15, 0.58)
        model_root.add_child(face_anchor)

    var face_width: float = 0.90
    var face_height: float = 0.82
    if face_left != null and face_right != null:
        face_width = face_left.global_position.distance_to(face_right.global_position)
    if face_top != null and face_bottom != null:
        face_height = face_top.global_position.distance_to(face_bottom.global_position)

    face_sprite = Sprite3D.new()
    face_sprite.name = "ExpressionOverlay"
    face_sprite.centered = true
    face_sprite.pixel_size = max(0.0008, face_width / 512.0)
    face_sprite.scale = Vector3(1.0, face_height / max(0.01, face_width), 1.0)
    face_sprite.billboard = BaseMaterial3D.BILLBOARD_ENABLED
    face_sprite.no_depth_test = false
    face_sprite.render_priority = 2
    face_anchor.add_child(face_sprite)

func _build_ui() -> void:
    var layer: CanvasLayer = CanvasLayer.new()
    add_child(layer)

    var safe: MarginContainer = MarginContainer.new()
    safe.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    safe.add_theme_constant_override("margin_left", 26)
    safe.add_theme_constant_override("margin_right", 26)
    safe.add_theme_constant_override("margin_top", 42)
    safe.add_theme_constant_override("margin_bottom", 34)
    layer.add_child(safe)

    var layout: VBoxContainer = VBoxContainer.new()
    layout.add_theme_constant_override("separation", 10)
    safe.add_child(layout)

    var title: Label = Label.new()
    title.text = "CAPIBARA"
    title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    title.add_theme_font_size_override("font_size", 54)
    title.add_theme_color_override("font_color", Color("ffc55a"))
    title.add_theme_color_override("font_outline_color", Color("351b0d"))
    title.add_theme_constant_override("outline_size", 10)
    layout.add_child(title)

    var subtitle: Label = Label.new()
    subtitle.text = "ALPHA 0.2  -  EXPRESIONES FACIALES"
    subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    subtitle.add_theme_font_size_override("font_size", 19)
    subtitle.add_theme_color_override("font_color", Color("e6f0dc"))
    subtitle.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.7))
    subtitle.add_theme_constant_override("outline_size", 5)
    layout.add_child(subtitle)

    var spacer: Control = Control.new()
    spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
    layout.add_child(spacer)

    status_label = Label.new()
    status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    status_label.add_theme_font_size_override("font_size", 24)
    status_label.add_theme_color_override("font_color", Color.WHITE)
    status_label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.8))
    status_label.add_theme_constant_override("outline_size", 6)
    layout.add_child(status_label)

    var panel: PanelContainer = PanelContainer.new()
    var panel_style: StyleBoxFlat = StyleBoxFlat.new()
    panel_style.bg_color = Color(0.08, 0.16, 0.12, 0.90)
    panel_style.corner_radius_top_left = 24
    panel_style.corner_radius_top_right = 24
    panel_style.corner_radius_bottom_left = 24
    panel_style.corner_radius_bottom_right = 24
    panel_style.border_width_left = 2
    panel_style.border_width_right = 2
    panel_style.border_width_top = 2
    panel_style.border_width_bottom = 2
    panel_style.border_color = Color(0.55, 0.72, 0.38, 0.65)
    panel.add_theme_stylebox_override("panel", panel_style)
    layout.add_child(panel)

    var grid: GridContainer = GridContainer.new()
    grid.columns = 3
    grid.add_theme_constant_override("h_separation", 10)
    grid.add_theme_constant_override("v_separation", 10)
    panel.add_child(grid)

    var labels: Dictionary = {
        "neutral": "NEUTRAL",
        "feliz": "FELIZ",
        "sorpresa": "SORPRESA",
        "sueno": "SUENO",
        "enojado": "ENOJADO",
        "guino": "GUINO"
    }
    for expression_name in EXPRESSIONS:
        var button: Button = Button.new()
        button.text = labels[expression_name]
        button.custom_minimum_size = Vector2(0, 68)
        button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
        button.add_theme_font_size_override("font_size", 18)
        var style: StyleBoxFlat = StyleBoxFlat.new()
        style.bg_color = Color("8a5a2f")
        style.corner_radius_top_left = 18
        style.corner_radius_top_right = 18
        style.corner_radius_bottom_left = 18
        style.corner_radius_bottom_right = 18
        style.border_width_left = 2
        style.border_width_right = 2
        style.border_width_top = 2
        style.border_width_bottom = 2
        style.border_color = Color("d9a95c")
        button.add_theme_stylebox_override("normal", style)
        var pressed: StyleBoxFlat = style.duplicate() as StyleBoxFlat
        pressed.bg_color = Color("4f8e3b")
        button.add_theme_stylebox_override("pressed", pressed)
        button.pressed.connect(_set_expression.bind(expression_name))
        grid.add_child(button)

    var hint: Label = Label.new()
    hint.text = "Arrastra suavemente para girar el modelo"
    hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    hint.add_theme_font_size_override("font_size", 16)
    hint.add_theme_color_override("font_color", Color("c9d8bf"))
    layout.add_child(hint)

func _set_expression(expression_name: String) -> void:
    current_expression = expression_name
    if face_sprite != null:
        face_sprite.texture = _expression_texture(expression_name)
    var readable: Dictionary = {
        "neutral": "Expresion neutral",
        "feliz": "Muy feliz",
        "sorpresa": "Sorpresa",
        "sueno": "Con sueno",
        "enojado": "Enojado de mentira",
        "guino": "Guino amistoso",
        "blink": "Parpadeo"
    }
    status_label.text = str(readable.get(expression_name, expression_name))
    blink_clock = 2.2 + randf() * 2.6

func _expression_texture(expression_name: String) -> Texture2D:
    var svg: String = _expression_svg(expression_name)
    var image: Image = Image.new()
    var error: Error = image.load_svg_from_string(svg, 1.0)
    if error != OK:
        push_error("No se pudo crear la expresion SVG: " + str(error))
        return GradientTexture2D.new()
    return ImageTexture.create_from_image(image)

func _expression_svg(expression_name: String) -> String:
    var common_start: String = "<svg xmlns='http://www.w3.org/2000/svg' width='512' height='512' viewBox='0 0 512 512'><defs><filter id='soft'><feGaussianBlur stdDeviation='3'/></filter></defs>"
    var patch: String = "<ellipse cx='256' cy='282' rx='205' ry='178' fill='#9a5429' fill-opacity='0.10' filter='url(#soft)'/>"
    var common_end: String = "</svg>"
    if expression_name == "feliz":
        return common_start + patch + "<path d='M105 205 Q155 255 205 205' fill='none' stroke='#23150f' stroke-width='22' stroke-linecap='round'/><path d='M307 205 Q357 255 407 205' fill='none' stroke='#23150f' stroke-width='22' stroke-linecap='round'/><ellipse cx='112' cy='302' rx='58' ry='31' fill='#df765f' fill-opacity='.52'/><ellipse cx='400' cy='302' rx='58' ry='31' fill='#df765f' fill-opacity='.52'/><path d='M172 312 Q256 405 340 312 Q256 460 172 312' fill='#351715' stroke='#24100e' stroke-width='12'/><path d='M220 329 L252 329 L252 370 Q234 381 218 365 Z' fill='#f5ead4'/><path d='M260 329 L292 329 L294 365 Q278 381 260 370 Z' fill='#f5ead4'/><ellipse cx='256' cy='401' rx='50' ry='23' fill='#d56f78'/>" + common_end
    if expression_name == "sorpresa":
        return common_start + patch + "<ellipse cx='155' cy='218' rx='48' ry='67' fill='#17110e'/><ellipse cx='357' cy='218' rx='48' ry='67' fill='#17110e'/><circle cx='138' cy='193' r='14' fill='white'/><circle cx='340' cy='193' r='14' fill='white'/><path d='M106 119 Q155 88 203 120' fill='none' stroke='#321a10' stroke-width='18' stroke-linecap='round'/><path d='M309 120 Q357 88 406 119' fill='none' stroke='#321a10' stroke-width='18' stroke-linecap='round'/><ellipse cx='256' cy='359' rx='67' ry='78' fill='#321313' stroke='#1b0d0b' stroke-width='12'/><ellipse cx='256' cy='392' rx='40' ry='24' fill='#d36b74'/>" + common_end
    if expression_name == "sueno" or expression_name == "blink":
        return common_start + patch + "<path d='M102 230 Q155 265 208 230' fill='none' stroke='#24150f' stroke-width='21' stroke-linecap='round'/><path d='M304 230 Q357 265 410 230' fill='none' stroke='#24150f' stroke-width='21' stroke-linecap='round'/><path d='M223 349 Q256 370 289 349' fill='none' stroke='#281511' stroke-width='16' stroke-linecap='round'/>" + ("<text x='365' y='125' font-family='sans-serif' font-size='52' font-weight='bold' fill='#d8ecff'>Z</text><text x='405' y='78' font-family='sans-serif' font-size='38' font-weight='bold' fill='#d8ecff'>Z</text>" if expression_name == "sueno" else "") + common_end
    if expression_name == "enojado":
        return common_start + patch + "<ellipse cx='155' cy='231' rx='42' ry='52' fill='#18110e'/><ellipse cx='357' cy='231' rx='42' ry='52' fill='#18110e'/><path d='M94 137 L205 183' fill='none' stroke='#30160f' stroke-width='24' stroke-linecap='round'/><path d='M418 137 L307 183' fill='none' stroke='#30160f' stroke-width='24' stroke-linecap='round'/><path d='M190 378 Q256 318 322 378' fill='none' stroke='#2e1511' stroke-width='20' stroke-linecap='round'/>" + common_end
    if expression_name == "guino":
        return common_start + patch + "<path d='M100 227 Q155 265 210 227' fill='none' stroke='#24150f' stroke-width='22' stroke-linecap='round'/><ellipse cx='357' cy='220' rx='46' ry='61' fill='#17110e'/><circle cx='340' cy='196' r='13' fill='white'/><path d='M177 333 Q256 403 335 333' fill='none' stroke='#2d1511' stroke-width='22' stroke-linecap='round'/><ellipse cx='110' cy='308' rx='50' ry='27' fill='#df765f' fill-opacity='.48'/>" + common_end
    return common_start + patch + "<ellipse cx='155' cy='222' rx='43' ry='58' fill='#17110e'/><ellipse cx='357' cy='222' rx='43' ry='58' fill='#17110e'/><circle cx='140' cy='199' r='13' fill='white'/><circle cx='342' cy='199' r='13' fill='white'/><path d='M191 341 Q256 385 321 341' fill='none' stroke='#2d1511' stroke-width='18' stroke-linecap='round'/>" + common_end

func _process(delta: float) -> void:
    elapsed += delta
    character_holder.position.y = 0.025 + sin(elapsed * 1.7) * 0.025
    character_holder.rotation.z = sin(elapsed * 1.1) * 0.008

    if blink_remaining > 0.0:
        blink_remaining -= delta
        if blink_remaining <= 0.0:
            _set_expression(current_expression)
    elif current_expression not in ["sueno", "enojado"]:
        blink_clock -= delta
        if blink_clock <= 0.0:
            var restore_expression: String = current_expression
            face_sprite.texture = _expression_texture("blink")
            blink_remaining = 0.13
            current_expression = restore_expression
            blink_clock = 2.2 + randf() * 2.6

func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventScreenTouch:
        var touch: InputEventScreenTouch = event as InputEventScreenTouch
        dragging = touch.pressed
        drag_last = touch.position
    elif event is InputEventScreenDrag:
        var drag: InputEventScreenDrag = event as InputEventScreenDrag
        var delta_x: float = drag.position.x - drag_last.x
        character_pivot.rotation.y = clamp(character_pivot.rotation.y - delta_x * 0.004, -0.38, 0.38)
        drag_last = drag.position
    elif event is InputEventMouseButton:
        var mouse_button: InputEventMouseButton = event as InputEventMouseButton
        if mouse_button.button_index == MOUSE_BUTTON_LEFT:
            dragging = mouse_button.pressed
            drag_last = mouse_button.position
    elif event is InputEventMouseMotion and dragging:
        var motion: InputEventMouseMotion = event as InputEventMouseMotion
        character_pivot.rotation.y = clamp(character_pivot.rotation.y - motion.relative.x * 0.004, -0.38, 0.38)
'''

project_godot = r'''; Capibara Tripo Alpha 0.2 - Godot 4.7
config_version=5

[application]
config/name="Capibara Expresiones Alpha"
run/main_scene="res://main.tscn"
config/features=PackedStringArray("4.7", "GL Compatibility")
config/icon="res://icon.png"

[display/window]
size/viewport_width=1080
size/viewport_height=1920
size/window_width_override=540
size/window_height_override=960
stretch/mode="canvas_items"
handheld/orientation=1

[rendering]
renderer/rendering_method="gl_compatibility"
renderer/rendering_method.mobile="gl_compatibility"
textures/vram_compression/import_etc2_astc=true
textures/default_filters/use_nearest_mipmap_filter=false
environment/defaults/default_clear_color=Color(0.018, 0.038, 0.033, 1)
'''

main_tscn = r'''[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://main.gd" id="1_script"]

[node name="CapibaraTripoAlpha" type="Node3D"]
script = ExtResource("1_script")
'''

export_presets = r'''[preset.0]
name="Android"
platform="Android"
runnable=true
advanced_options=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter="output/*,tools/*"
export_path="output/Capibara-Tripo-Expresiones-Alpha.apk"
script_export_mode=2

[preset.0.options]
custom_template/debug=""
custom_template/release=""
gradle_build/use_gradle_build=false
gradle_build/export_format=0
architectures/armeabi-v7a=true
architectures/arm64-v8a=true
architectures/x86=false
architectures/x86_64=false
package/unique_name="com.medinaparra.capibaraexpresiones"
package/name="Capibara Expresiones"
package/signed=true
package/app_category=0
version/code=2
version/name="0.2.0-alpha"
screen/immersive_mode=true
screen/edge_to_edge=true
screen/support_small=true
screen/support_normal=true
screen/support_large=true
screen/support_xlarge=true
user_data_backup/allow=false
command_line/extra_args=""
apk_expansion/enable=false
permissions/custom_permissions=PackedStringArray()
'''

(root / 'main.gd').write_text(main_gd, encoding='utf-8')
(root / 'main.tscn').write_text(main_tscn, encoding='utf-8')
(root / 'project.godot').write_text(project_godot, encoding='utf-8')
(root / 'export_presets.cfg').write_text(export_presets, encoding='utf-8')
(root / 'TRIPO_ALPHA.txt').write_text(
    'Modelo: GLB suministrado por el usuario\n'
    'Sistema facial: overlay 3D runtime con 6 expresiones y parpadeo\n'
    'Objetivo: alpha Android compatible con ARMv7 y ARM64\n',
    encoding='utf-8'
)
print('TRIPO_GODOT_PROJECT_OK', root)
