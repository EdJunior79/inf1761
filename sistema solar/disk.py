import math
from array import array
import wgpu
from shape import Shape

class Disk(Shape):
    def __init__(self, device, n_div=64):
        super().__init__()
        self.device = device
        
        coords = array("f")
        texcoords = array("f")
        indices = array("I")
        
        coords.extend([0.0, 0.0])
        texcoords.extend([0.5, 0.5])
        
        for i in range(n_div):
            ang = i * (2.0 * math.pi / n_div)
            c = math.cos(ang)
            s = math.sin(ang)
            
            coords.extend([c, s])
            texcoords.extend([0.5 + 0.5 * c, 0.5 - 0.5 * s])
            
        for i in range(1, n_div + 1):
            prox = 1 if i == n_div else i + 1
            indices.extend([0, i, prox])
            
        self.nind = len(indices)
        
        self.coord_vbo = device.create_buffer_with_data(data=coords, usage=wgpu.BufferUsage.VERTEX)
        self.texcoord_vbo = device.create_buffer_with_data(data=texcoords, usage=wgpu.BufferUsage.VERTEX)
        self.ibo = device.create_buffer_with_data(data=indices, usage=wgpu.BufferUsage.INDEX)

    def draw(self, st):
        instance = st.get_shader().commit_matrix(st)
        st.render_pass.set_vertex_buffer(0, self.coord_vbo)
        st.render_pass.set_vertex_buffer(1, self.texcoord_vbo)
        st.render_pass.set_index_buffer(self.ibo, wgpu.IndexFormat.uint32)
        st.render_pass.draw_indexed(self.nind, 1, 0, 0, instance)