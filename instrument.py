import pyaudio
import numpy as np
import pickle
import asyncio
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from neuron_to_note import note_to_freq


INSTRUMENT_TARGET_ADDRESS = "/instrument_input"
INSTRUMENT_INIT_ADDRESS = "/instrument_init"
INSTRUMENT_PORT = 5020
ip = "127.0.0.1"

p = pyaudio.PyAudio()


class OscInstrument:
    FORMAT = pyaudio.paInt16
    RATE = 44100
    CHANNELS = 2
    CHUNK = 1024

    server = None
    tone_duration = 2000
    __frequencies = []
    __notes = []
    __volumes = []
    __n_freqs = 0
    __signal = None  # a (num-frequencies, num-samples)-matrix, where the kth row is the sine wave for the kth neuron

    def __init__(self, notes=None):
        if notes:
            self.init_sound(notes)
        self.__create_stream()

    def init_sound(self, notes):
        self.__notes = notes
        self.__n_freqs = len(notes)
        self.__frequencies = np.mat(note_to_freq(notes))
        self.__volumes = np.ones_like(self.__frequencies)
        self.__create_sound()

    def __create_stream(self):
        self.__stream = p.open(format=self.FORMAT,
                               channels=self.CHANNELS,
                               rate=self.RATE,
                               input=True,
                               output=True,
                               frames_per_buffer=self.CHUNK)

    def __create_sound(self):
        num_samples = int(self.RATE * self.tone_duration / 1000.)
        volume_scale = .85 * 32767
        twopi = 2 * np.pi

        #  every x-value needs to be duplicated for stereo sound
        x_data = np.resize(np.arange(num_samples), (2, num_samples)).T.flatten()
        signal = np.sin(self.__frequencies.T * x_data * twopi / self.RATE) * volume_scale

        # damp_duration = 100
        # end_silence = 100
        # # add an- u- abschwellen
        # if damp_duration < tone_duration / 2.:
        #     num_damp_samp = 2 * int(self.RATE * damp_duration)  # the 2 is the stereo
        # else:
        #     print
        #     'WARNING! dampDuration>toneDuration/2!!! Using toneDuration/2'
        #     num_damp_samp = 2 * int(self.RATE * tone_duration / 2.)  # the 2 is the stereo
        # dampVec = np.linspace(0, 1, num_damp_samp)
        # signal[0:num_damp_samp] *= dampVec
        # signal[len(signal) - num_damp_samp::] *= dampVec[::-1]
        # signal = np.append(signal, np.zeros(2 * int(self.RATE * end_silence)))

        self.__signal = signal

    def message_handler(self, address, content):
        if address == INSTRUMENT_INIT_ADDRESS:
            notes = pickle.loads(content)
            self.init_sound(notes)
        elif address == INSTRUMENT_TARGET_ADDRESS:
            self._update_volume(content)

    def play(self):
        scaling = (np.sin(np.arange(100) * 2 * np.pi / 50) + 1)/2.
        vol_idx = 1
        idx = 0
        data = self.__signal[idx:idx + 2 * self.CHUNK]

        while len(data):
            vol = scaling[vol_idx]
            print(vol)
            self.__stream.write((vol*data).astype(np.int16).tostring())
            idx += 2 * self.CHUNK
            data = self.__signal[idx:idx + 2 * self.CHUNK]
            vol_idx += 1

    def _update_volume(self, note):
        idx = self.__notes.index(note)
        self.__volumes[:, idx] = np.remainder(self.__volumes[:, idx] + 1, 2)

    async def loop(self):
        idx = 0
        while True:
            if len(self.__frequencies):
                end_idx = idx + 2 * self.CHUNK
                if end_idx < self.__signal.shape[1]:
                    curr_signal = self.__signal[:, idx:end_idx]
                    idx = end_idx
                else:
                    curr_signal = self.__signal[:, idx::]
                    idx = 0
                # multiply with volumes and average signal
                data = np.array(self.__volumes * curr_signal).flatten()/self.__n_freqs
                self.__stream.write(data.astype(np.int16).tostring())
            await asyncio.sleep(1000/(2*self.RATE))

    async def init_main(self):
        dispatcher = Dispatcher()
        dispatcher.map(INSTRUMENT_TARGET_ADDRESS, self.message_handler)
        dispatcher.map(INSTRUMENT_INIT_ADDRESS, self.message_handler)

        self.server = AsyncIOOSCUDPServer((ip, INSTRUMENT_PORT), dispatcher, asyncio.get_event_loop())
        transport, protocol = await self.server.create_serve_endpoint()  # Create datagram endpoint and start serving
        print('transport {} protocol {}'.format(transport, protocol))
        await self.loop()  # Enter main loop of program

        transport.close()  # Clean up serve endpoint


if __name__ == '__main__':
    song_server = OscInstrument()

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(song_server.init_main())
