import wgpu
from rendercanvas.glfw import RenderCanvas, loop
from camera2d import Camera2D
from shader import Shader
from pipeline import Pipeline
from scene import Scene
from node import Node
from transform import Transform
from texture import Texture
from sampler import Sampler
from textureset import TextureSet
from engine import Engine
from state import State
from disk import Disk
from square import Square

# janela e webgpu
canvas = RenderCanvas(size=(750, 750), title="Mini-Sistema Solar 2D - Grafo de Cena")
context = canvas.get_context("wgpu")
adapter = wgpu.gpu.request_adapter_sync(power_preference="high-performance", canvas=context)
device = adapter.request_device_sync()
texture_format = context.get_preferred_format(adapter)
context.configure(device=device, format=texture_format)

#camera e shader
camera = Camera2D(-6.0, 6.0, -6.0, 6.0)
shader = Shader(device, "shader.wgsl")

shader.set_vertex_buffers([
    {
        "array_stride": 8,
        "step_mode": "vertex",
        "attributes": [{"format": "float32x2", "offset": 0, "var_name": "pos"}],
    },
    {
        "array_stride": 8,
        "step_mode": "vertex",
        "attributes": [{"format": "float32x2", "offset": 0, "var_name": "uv"}],
    },
])

def carregar_textura(nome_imagem):
    tex = Texture(device, "face_texture", nome_imagem)
    smp = Sampler(device, "face_sampler")
    ts = TextureSet([tex, smp])
    shader.add_texture_set(ts)
    return ts

app_espaco   = carregar_textura("espaco.jpg")
app_sol      = carregar_textura("sol.jpg")
app_mercurio = carregar_textura("mercurio.jpg")
app_terra    = carregar_textura("terra.jpg")
app_lua      = carregar_textura("lua.jpg")

# geometrias
geo_disco    = Disk(device)
geo_quadrado = Square(device)

# grafo de cena
pipe = Pipeline(shader, texture_format, depth_stencil=None)
root = Node(pipeline=pipe, trf=Transform())

# fundo espaco
trf_fundo = Transform()
trf_fundo.scale(6.0, 6.0, 1.0)
node_fundo = Node(trf=trf_fundo, apps=[app_espaco], shps=[geo_quadrado])
root.add_node(node_fundo)

# sol
trf_sol = Transform()
trf_sol.scale(1.15, 1.15, 1.0)
node_sol = Node(trf=trf_sol, apps=[app_sol], shps=[geo_disco])
root.add_node(node_sol)

# mercurio
trf_orb_merc = Transform()
node_orb_merc = Node(trf=trf_orb_merc)
root.add_node(node_orb_merc)

trf_pos_merc = Transform()
trf_pos_merc.translate(1.9, 0.0, 0.0)
trf_pos_merc.scale(0.24, 0.24, 1.0)
node_merc = Node(trf=trf_pos_merc, apps=[app_mercurio], shps=[geo_disco])
node_orb_merc.add_node(node_merc)

# terra e lua
trf_orb_terra = Transform()
node_orb_terra = Node(trf=trf_orb_terra)
root.add_node(node_orb_terra)
trf_pos_terra = Transform()
trf_pos_terra.translate(4.1, 0.0, 0.0)
node_pos_terra = Node(trf=trf_pos_terra)
node_orb_terra.add_node(node_pos_terra)

# rotacao da terra no proprio eixo
trf_eixo_terra = Transform()
node_eixo_terra = Node(trf=trf_eixo_terra)
node_pos_terra.add_node(node_eixo_terra)

trf_tam_terra = Transform()
trf_tam_terra.scale(0.48, 0.48, 1.0)
node_corpo_terra = Node(trf=trf_tam_terra, apps=[app_terra], shps=[geo_disco])
node_eixo_terra.add_node(node_corpo_terra)

# lua
trf_orb_lua = Transform()
node_orb_lua = Node(trf=trf_orb_lua)
node_pos_terra.add_node(node_orb_lua)

trf_pos_lua = Transform()
trf_pos_lua.translate(0.9, 0.0, 0.0)
trf_pos_lua.scale(0.16, 0.16, 1.0)
node_corpo_lua = Node(trf=trf_pos_lua, apps=[app_lua], shps=[geo_disco])
node_orb_lua.add_node(node_corpo_lua)

class SolarEngine(Engine):
    def __init__(self, t_merc, t_orb_terra, t_eixo_terra, t_orb_lua):
        super().__init__()
        self.t_merc = t_merc
        self.t_orb_terra = t_orb_terra
        self.t_eixo_terra = t_eixo_terra
        self.t_orb_lua = t_orb_lua

    def update(self, dt: float):
        self.t_merc.rotate(82.0 * dt, 0, 0, 1)
        self.t_orb_terra.rotate(22.0 * dt, 0, 0, 1)
        self.t_eixo_terra.rotate(440.0 * dt, 0, 0, 1)
        self.t_orb_lua.rotate(240.0 * dt, 0, 0, 1)

engine = SolarEngine(trf_orb_merc, trf_orb_terra, trf_eixo_terra, trf_orb_lua)
scene = Scene(root)
scene.add_engine(engine)

def draw_frame():
    scene.update(1.0 / 60.0)

    current_texture = context.get_current_texture()
    encoder = device.create_command_encoder()
    render_pass = encoder.begin_render_pass(
        color_attachments=[{
            "view": current_texture.create_view(),
            "resolve_target": None,
            "clear_value": (0.0, 0.0, 0.0, 1.0),
            "load_op": wgpu.LoadOp.clear,
            "store_op": wgpu.StoreOp.store,
        }]
    )

    st = State(camera, device, render_pass, canvas.get_physical_size())
    scene.render(st)
    render_pass.end()

    for shd in st.get_matrix_shaders():
        shd.flush_matrices()

    device.queue.submit([encoder.finish()])
    canvas.request_draw()

canvas.request_draw(draw_frame)
loop.run()