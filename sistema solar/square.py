from array import array
import wgpu
from shape import Shape

class Square(Shape):
    def __init__(self, device):
        super().__init__()
        self.device = device
        
        coords = array("f", [
            -1.0, -1.0,
             1.0, -1.0,
             1.0,  1.0,
            -1.0,  1.0
        ])
        
        texcoords = array("f", [
            0.0, 1.0,
            1.0, 1.0,
            1.0, 0.0,
            0.0, 0.0
        ])
        
        indices = array("I", [0, 1, 2,  0, 2, 3])
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