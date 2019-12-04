import pyaudio
import numpy as np
import asyncio
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher


INSTRUMENT_TARGET_ADDRESS = "/instrument_input"
INSTRUMENT_PORT = 5020
ip = "127.0.0.1"

p = pyaudio.PyAudio()


class OscInstrument:
    FORMAT = pyaudio.paInt16
    RATE = 44100
    CHANNELS = 2
    CHUNK = 1024

    server = None

    def __init__(self, tone_duration=2000, frequency=440):
        self.__volume = 1
        self.__create_sound(tone_duration, frequency)
        self.__create_stream()

    def __create_stream(self):
        self.__stream = p.open(format=self.FORMAT,
                               channels=self.CHANNELS,
                               rate=self.RATE,
                               input=True,
                               output=True,
                               frames_per_buffer=self.CHUNK)

    def __create_sound(self, tone_duration, frequency):
        num_samples = int(self.RATE * tone_duration / 1000.)
        volume_scale = .85 * 32767
        twopi = 2 * np.pi
        sine = np.sin(np.arange(num_samples) * twopi * frequency / self.RATE) * volume_scale
        signal = np.array((sine, sine)).transpose().flatten()

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
        print('address: {} map: {}'.format(address, content))
        # osc_map = pickle.loads(content)

        self._update_volumes(content)

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

    def _update_volumes(self, volume):
        self.__volume = volume

    async def loop(self):
        refresh_rate = 50
        idx = 0

        while True:
            end_idx = idx + 2 * self.CHUNK
            if end_idx < len(self.__signal):
                data = self.__signal[idx:end_idx]
                idx = end_idx
            else:
                data = self.__signal[idx::]
                idx = 0

            self.__stream.write((self.__volume * data).astype(np.int16).tostring())

            await asyncio.sleep(1./refresh_rate)

    async def init_main(self):
        dispatcher = Dispatcher()
        dispatcher.map(INSTRUMENT_TARGET_ADDRESS, self.message_handler)

        self.server = AsyncIOOSCUDPServer((ip, INSTRUMENT_PORT), dispatcher, asyncio.get_event_loop())
        transport, protocol = await self.server.create_serve_endpoint()  # Create datagram endpoint and start serving
        print('transport {} protocol {}'.format(transport, protocol))
        await self.loop()  # Enter main loop of program

        transport.close()  # Clean up serve endpoint


if __name__ == '__main__':
    song_server = OscInstrument()

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(song_server.init_main())
