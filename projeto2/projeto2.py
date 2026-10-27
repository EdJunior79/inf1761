import graphics_math as gm
import wgpu
from rendercanvas.glfw import RenderCanvas, loop

from camera3d import Camera3D
from spotlight import SpotLight
from shader import Shader
from pipeline import Pipeline
from phongmaterial import PhongMaterial
from transform import Transform
from node import Node
from scene import Scene
from renderer import Renderer
from cube import Cube
from sphere import Sphere
from texture import Texture
from sampler import Sampler
from textureset import TextureSet

fog_ligado = True
corte_ligado = True

def initialize(device, target_format):
    global camera, scene, shader

    # camera
    camera = Camera3D(3.2, 4.2, 4.8)
    camera.set_center(0.0, 1.5, 0.0)
    arcball = camera.create_arcball()
    arcball.attach(canvas)

    # luz de spot
    light = SpotLight(0.0, 6.0, 0.5, 0.0, -1.0, -0.12, cutoff_angle=35.0, exponent=8.0, space="world")

    mat_branco = PhongMaterial(1.0, 1.0, 1.0)
    mat_la = PhongMaterial(1.0, 1.0, 1.0)
    mat_la.set_specular(0.05, 0.05, 0.05) 

    # texturas
    sampler = Sampler(device, "decal_sampler")
    set_madeira = TextureSet([Texture(device, "decal_texture", "textura_madeira.jpg"), sampler])
    set_couro = TextureSet([Texture(device, "decal_texture", "textura_couro.jpg"), sampler])
    set_la = TextureSet([Texture(device, "decal_texture", "textura_la.jpg"), sampler])

    # geometria
    cube = Cube(device)
    sphere = Sphere(device)

    # shader
    shader = Shader(device, "mesa.wgsl", light=light, space="world")
    shader.set_vertex_buffers([
        {"array_stride": 3 * 4, "step_mode": "vertex",
         "attributes": [{"format": "float32x3", "offset": 0, "var_name": "coord"}]},
        {"array_stride": 3 * 4, "step_mode": "vertex",
         "attributes": [{"format": "float32x3", "offset": 0, "var_name": "normal"}]},
        {"array_stride": 3 * 4, "step_mode": "vertex",
         "attributes": []},
        {"array_stride": 2 * 4, "step_mode": "vertex",
         "attributes": [{"format": "float32x2", "offset": 0, "var_name": "texcoord"}]},
    ])
    # pipeline
    pipeline = Pipeline(shader, target_format, primitive={"cull_mode": "none"})

    shader.add_material(mat_branco)
    shader.add_material(mat_la)
    shader.add_texture_set(set_madeira)
    shader.add_texture_set(set_couro)
    shader.add_texture_set(set_la)

    # fog branco, da mesma cor do fundo
    shader.set_value("fog_color", gm.vec4(1.0, 1.0, 1.0, 1.0))
    shader.set_value("fog_density", 0.09)
    # plano de corte: mantem so o que esta abaixo de y = 2.52 (meio do novelo)
    shader.set_value("clip_plane", gm.vec4(0.0, -1.0, 0.0, 2.52))
    shader.set_value("clip_plane_color", gm.vec4(0.85, 0.75, 0.3, 1.0))

    nodes = []

    # base da mesa
    trf_base = Transform()
    trf_base.translate(0.0, 2.0, 0.0)
    trf_base.scale(3.4, 0.2, 3.4)
    nodes.append(Node(None, trf_base, [mat_branco, set_madeira], [cube]))

    # pernas da mesa
    for px, pz in [(-1.59, 1.59), (1.59, 1.59), (-1.59, -1.59), (1.59, -1.59)]:
        trf_perna = Transform()
        trf_perna.translate(px, 0.0, pz)
        trf_perna.scale(0.22, 2.0, 0.22)
        nodes.append(Node(None, trf_perna, [mat_branco, set_madeira], [cube]))

    # livro de couro
    trf_livro = Transform()
    trf_livro.translate(-0.55, 2.2, 0.35)
    trf_livro.rotate(20.0, 0.0, 1.0, 0.0)
    trf_livro.scale(0.75, 0.14, 1.05)
    nodes.append(Node(None, trf_livro, [mat_branco, set_couro], [cube]))

    # novelo de la
    trf_la = Transform()
    trf_la.translate(0.65, 2.52, -0.35)
    trf_la.scale(0.32, 0.32, 0.32)
    nodes.append(Node(None, trf_la, [mat_la, set_la], [sphere]))

    root = Node(pipeline, nodes=nodes)
    scene = Scene(root)

def draw():
    target_texture = context.get_current_texture()
    renderer.render(target_texture, scene, camera)

def on_key(event):
    global fog_ligado, corte_ligado
    if event["key"] == "q":
        canvas.close()
    elif event["key"] == "f":   # liga/desliga o fog
        fog_ligado = not fog_ligado
        shader.set_value("fog_density", 0.09 if fog_ligado else 0.0)
    elif event["key"] == "c":   # liga/desliga o plano de corte
        corte_ligado = not corte_ligado
        if corte_ligado:
            shader.set_value("clip_plane", gm.vec4(0.0, -1.0, 0.0, 2.52))
        else:
            shader.set_value("clip_plane", gm.vec4(0.0, 0.0, 0.0, 1.0))  # nao corta nada

def main():
    global canvas, device, context, renderer

    canvas = RenderCanvas(size=(750, 750), title="INF1761 - Mesa com objetos", update_mode="continuous", max_fps=60)
    adapter = wgpu.gpu.request_adapter_sync()
    device = adapter.request_device_sync()
    context = canvas.get_context("wgpu")
    target_format = context.get_preferred_format(device.adapter)
    context.configure(device=device, format=target_format)

    renderer = Renderer(device, depth_test=True, clear_value=(1.0, 1.0, 1.0, 1.0))

    initialize(device, target_format)

    canvas.add_event_handler(on_key, "key_down")
    canvas.request_draw(draw)
    loop.run()

if __name__ == "__main__":
    main()