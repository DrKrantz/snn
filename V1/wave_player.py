import pyaudio
import numpy as np

p = pyaudio.PyAudio()


class WavePlayer:
    FORMAT = pyaudio.paInt16
    RATE = 44100
    CHANNELS = 1
    CHUNK = 1024
    DECAY_FACTOR = 0.95

    server = None
    __frequencies = []
    __notes = []
    __volumes = []
    __n_freqs = 0

    def __init__(self, data):
        self.__prepare_data(data)
        self.__create_stream()

    def __create_stream(self):
        self.__stream = p.open(format=self.FORMAT,
                               channels=self.CHANNELS,
                               rate=self.RATE,
                               input=True,
                               output=True,
                               frames_per_buffer=self.CHUNK)

    def play(self):
        for chunk in self.data:
            self.__stream.write(chunk.astype(np.int16).tostring())

    def __prepare_data(self, data):
        n_samples = len(data)
        rem = np.remainder(n_samples, self.CHUNK)
        padded = np.append(data, np.zeros(self.CHUNK-rem))
        self.data = padded.reshape(int(padded.size/self.CHUNK), self.CHUNK)


if __name__ == '__main__':
    import pickle
    file_name = 'test.pkl'
    raw_data = pickle.load(open(file_name, 'rb'))
    player = WavePlayer(raw_data)
    player.play()
