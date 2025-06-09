import pyglet
import moderngl
from audio.analyzer import AudioAnalyzer
from graphics.scene import Scene

window = pyglet.window.Window(1280, 720, 'Sonic Orbits - Phase 2', resizable=True)
ctx = moderngl.create_context()

audio = AudioAnalyzer()
scene = Scene(ctx)


@window.event
def on_draw():
    scene.render(window, audio)

@window.event
def on_resize(width, height):
    ctx.viewport = (0, 0, width, height)
    scene.resize(width, height)

def update(dt):
    bass = audio.get_energy('bass')
    scene.update(dt, bass)

pyglet.clock.schedule_interval(update, 1/60)
pyglet.app.run()
