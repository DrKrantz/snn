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
    __frequencies = []
    __notes = []
    __volumes = []
    __n_freqs = 0

    def __init__(self, notes=None):
        if notes:
            self.__init_sound(notes)
        self.__create_stream()

    def __init_sound(self, notes):
        self.__notes = notes
        self.__n_freqs = len(notes)
        self.__frequencies = np.mat(note_to_freq(notes))
        self.__volumes = np.ones_like(self.__frequencies)

    def __create_stream(self):
        self.__stream = p.open(format=self.FORMAT,
                               channels=self.CHANNELS,
                               rate=self.RATE,
                               input=True,
                               output=True,
                               frames_per_buffer=self.CHUNK)

    def _update_volume(self, note):
        idx = self.__notes.index(note)
        self.__volumes[:, idx] = 0.25 if self.__volumes[:, idx] == 0.75 else 0.75

    def message_handler(self, address, content):
        if address == INSTRUMENT_INIT_ADDRESS:
            notes = pickle.loads(content)
            self.__init_sound(notes)
        elif address == INSTRUMENT_TARGET_ADDRESS:
            self._update_volume(content)

    async def loop(self):
        volume_scale = .85 * 32767
        twopi = 2 * np.pi
        #  every x-value needs to be duplicated for stereo sound
        x_data = np.resize(np.arange(2 * self.CHUNK), (2, 2 * self.CHUNK)).T.flatten()
        while True:
            if len(self.__frequencies):
                # TODO: reset signal to start from 0 at some point to avoid too large numbers
                x_data += 2 * self.CHUNK

                # a (num-frequencies, num-samples)-matrix, where the kth row is the sine wave for the kth neuron
                curr_signal = np.sin(self.__frequencies.T * x_data * twopi / self.RATE) * volume_scale
                # multiply with volumes and average over frequencies
                data = np.array(self.__volumes * curr_signal).flatten()/self.__n_freqs
                self.__stream.write(data.astype(np.int16).tostring())
            await asyncio.sleep(1000/(2*self.RATE))

    async def init_main(self):
        dispatcher = Dispatcher()
        dispatcher.map(INSTRUMENT_TARGET_ADDRESS, self.message_handler)
        dispatcher.map(INSTRUMENT_INIT_ADDRESS, self.message_handler)

        self.server = AsyncIOOSCUDPServer((ip, INSTRUMENT_PORT), dispatcher, asyncio.get_event_loop())
        transport, protocol = await self.server.create_serve_endpoint()  # Create datagram endpoint and start serving
        print('server running: transport {} protocol {}'.format(transport, protocol))
        await self.loop()  # Enter main loop of program

        transport.close()  # Clean up serve endpoint


if __name__ == '__main__':
    song_server = OscInstrument()

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(song_server.init_main())
