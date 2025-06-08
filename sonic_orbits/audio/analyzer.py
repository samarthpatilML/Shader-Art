import numpy as np
import sounddevice as sd
import threading

class AudioAnalyzer:
    def __init__(self, samplerate=44100, blocksize=1024):
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.freq_data = np.zeros(blocksize // 2+1)
        self.lock = threading.Lock()

        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            channels=1,
            dtype='float32',
            callback=self._audio_callback
        )
        self.stream.start()

    def _audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        samples = indata[:, 0]
        spectrum = np.abs(np.fft.rfft(samples * np.hanning(len(samples))))
        with self.lock:
            self.freq_data = spectrum

    def get_energy(self, band='bass'):
        with self.lock:
            spectrum = self.freq_data.copy()

        freqs = np.fft.rfftfreq(self.blocksize, d=1.0 / self.samplerate)

        if band == 'bass':
            mask = (freqs >= 20) & (freqs < 250)
        elif band == 'mid':
            mask = (freqs >= 250) & (freqs < 2000)
        elif band == 'treble':
            mask = (freqs >= 2000) & (freqs < 8000)
        else:
            mask = np.ones_like(freqs, dtype=bool)

        energy = np.mean(spectrum[mask])
        return energy
