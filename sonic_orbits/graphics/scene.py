import os
import moderngl
import numpy as np
from pyrr import Matrix44, Vector3

class Scene:
    def __init__(self, ctx, num_particles=1000):
        self.ctx = ctx
        self.angle = 0.0
        self.num_particles = num_particles

        # Load shaders using a path relative to this file
        here = os.path.dirname(os.path.abspath(__file__))
        shader_path = os.path.join(here, 'shaders.glsl')
        with open(shader_path) as f:
            shader_src = f.read()

        vert_src = self.extract_shader(shader_src, 'vertex')
        frag_src = self.extract_shader(shader_src, 'fragment')

        self.prog = self.ctx.program(vertex_shader=vert_src, fragment_shader=frag_src)

        # Initialize random positions in a sphere around origin
        positions = np.random.uniform(-1.0, 1.0, (num_particles, 3)).astype('f4')
        # Normalize to inside unit sphere (optional)
        norms = np.linalg.norm(positions, axis=1)
        positions = (positions.T / norms).T * np.random.uniform(0.1, 1.0, num_particles)[:, None]

        self.positions = positions
        self.velocities = np.random.uniform(-0.01, 0.01, (num_particles, 3)).astype('f4')

        self.vbo = self.ctx.buffer(positions.tobytes())
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_position')

        # Camera setup
        self.camera_pos = Vector3([0.0, 0.0, -5.0])
        self.proj = Matrix44.perspective_projection(45.0, 16 / 9, 0.1, 100.0)

    def extract_shader(self, source, shader_type):
        start_token = f'#{shader_type}'
        lines = source.splitlines()
        collecting = False
        shader_lines = []
        for line in lines:
            if line.strip().startswith(start_token):
                collecting = True
                continue
            if shader_type == 'vertex' and line.strip().startswith('#fragment'):
                break
            if collecting:
                shader_lines.append(line)
        return '\n'.join(shader_lines)

    def resize(self, width, height):
        self.proj = Matrix44.perspective_projection(45.0, width / height, 0.1, 100.0)

    def update(self, dt, bass_energy):
        # Update particle positions based on velocity, modulated by bass_energy
        speed = 0.5 + bass_energy * 5.0  # speed factor

        self.positions += self.velocities * speed * dt

        # Bounce particles back if outside radius 1.5 sphere
        dist = np.linalg.norm(self.positions, axis=1)
        outside = dist > 1.5
        self.velocities[outside] = -self.velocities[outside]

        # Update buffer with new positions
        self.vbo.write(self.positions.tobytes())

        # Slowly rotate whole system for nice effect
        self.angle += 0.2 * bass_energy

    def render(self, window, audio):
        self.ctx.clear(0.0, 0.0, 0.0)
        self.ctx.enable(moderngl.DEPTH_TEST)

        model = Matrix44.from_y_rotation(self.angle)
        view = Matrix44.look_at(self.camera_pos, Vector3([0.0, 0.0, 0.0]), Vector3([0.0, 1.0, 0.0]))

        self.prog['model'].write(model.astype('f4').tobytes())
        self.prog['view'].write(view.astype('f4').tobytes())
        self.prog['proj'].write(self.proj.astype('f4').tobytes())

        # Draw particles as points
        self.vao.render(moderngl.POINTS)
