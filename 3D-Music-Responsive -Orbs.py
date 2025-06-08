import numpy as np
import sounddevice as sd
from vpython import sphere, vector, rate, scene, color

# Create 3D particles
scene.title = "Sonic Orbits"
scene.background = color.black
particles = [sphere(pos=vector(np.sin(a)*5, np.cos(a)*5, 0),
                    radius=0.2, color=color.hsv_to_rgb(vector(a/6.28, 1, 1)))
             for a in np.linspace(0, 2*np.pi, 100)]

# Sound stream
duration = 0.05
samplerate = 44100

def audio_callback(indata, frames, time, status):
    global fft_energy
    samples = indata[:, 0]
    spectrum = np.abs(np.fft.rfft(samples))[:50]
    fft_energy = np.mean(spectrum)

stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=samplerate, blocksize=int(duration * samplerate))
stream.start()

# Animation loop
fft_energy = 0
angle = 0
while True:
    rate(60)
    angle += 0.01
    scale = min(fft_energy / 100, 3)
    for i, p in enumerate(particles):
        theta = angle + i * 0.1
        p.pos = vector(np.sin(theta)*scale*5, np.cos(theta)*scale*5, np.sin(theta * 0.5)*scale*2)
        p.radius = 0.2 + 0.1 * np.sin(theta * 5)
