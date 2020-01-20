import pyaudio
import numpy as np
import pickle
import asyncio
import threading
import time
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from neuron_to_note import note_to_freq


INSTRUMENT_TARGET_ADDRESS = "/instrument_input"
INSTRUMENT_INIT_ADDRESS = "/instrument_init"
INSTRUMENT_PORT = 5020
ip = "127.0.0.1"

p = pyaudio.PyAudio()

TYPE_NOTE = 0
TYPE_FREQUENCIES = 1


class SoundThread(threading.Thread):  # multiprocessing.Process
    FORMAT = pyaudio.paInt16
    RATE = 44100
    CHANNELS = 1
    CHUNK = 1024
    SMOOTHING_SAMPLES = 300

    def __init__(self, data):
        self.__data = data
        self.__create_stream()
        self._status_playing = False
        super(SoundThread, self).__init__(target=self.play)

    def __create_stream(self):
        self.__stream = p.open(format=self.FORMAT,
                               channels=self.CHANNELS,
                               rate=self.RATE,
                               input=True,
                               output=True,
                               frames_per_buffer=self.CHUNK)

    def set_data(self, data):
        self.__data = data

    def play(self):
        idx = 0
        while idx < len(self.__data):
            signal = self.__data[idx:idx+self.CHANNELS*self.CHUNK]
            self.__stream.write(signal.astype(np.int16).tostring())
            # x_data += 2*self.CHUNK
            time.sleep(1000 / (2*self.RATE))
            idx += self.CHANNELS*self.CHUNK

    def stop(self):
        self._status_playing = False


class OscInstrument:
    FORMAT = pyaudio.paInt16
    RATE = 44100
    CHANNELS = 2
    CHUNK = 1024
    DECAY_FACTOR = 0.95

    server = None
    __frequencies = []
    __notes = []
    __volumes = []
    __indices_to_update = []
    __n_freqs = 0
    __data_matrix = np.array([])
    __x_data = np.array([])
    __max_volume = .85 * 32767

    def __init__(self, notes=None):
        self.__create_stream()
        if notes:
            self.__init_sound(notes)

    def __create_stream(self):
        self.__stream = p.open(format=self.FORMAT,
                               channels=self.CHANNELS,
                               rate=self.RATE,
                               input=True,
                               output=True,
                               frames_per_buffer=self.CHUNK)

    def __init_sound(self, notes, note_type=TYPE_FREQUENCIES):
        if note_type == TYPE_NOTE:
            self.__notes = notes
            self.__frequencies = np.array(note_to_freq(notes))
        elif note_type == TYPE_FREQUENCIES:
            self.__frequencies = np.array(notes)
            self.__notes = range(len(notes))
        self.__n_freqs = len(notes)
        self.__volumes = np.ones_like(self.__frequencies)*self.__max_volume
        self.__data_matrix = np.ones((self.__n_freqs, self.CHANNELS * self.CHUNK))
        #  every x-value needs to be duplicated for stereo sound
        duplicated_xrange = np.resize(np.arange(self.CHUNK), (2, self.CHUNK)).T.flatten()
        self.__x_data = np.mat(self.__frequencies).T * duplicated_xrange * 2 * np.pi / self.RATE

    def _volume_decay(self):
        self.__volumes *= self.DECAY_FACTOR

    def _compute_current_signal(self):
        # a (num-frequencies, num-samples)-matrix, where the kth row is the sine wave for the kth neuron
        base_signal = np.sin(self.__x_data)
        for freq_idx, wave_form in enumerate(np.array(base_signal)):

            # detect the 'switch_idx' where the signal crosses zero
            first_sign = np.sign(wave_form[0])
            if first_sign == 0:
                switch_idx = 0
            else:
                switch_idx = np.nonzero(np.sign(wave_form) != first_sign)[0][0]
            wave_form[0:switch_idx] *= self.__volumes[freq_idx]

            # set volume to maximum or decay
            if freq_idx in self.__indices_to_update:
                self.__volumes[freq_idx] = self.__max_volume
            else:
                self.__volumes[freq_idx] *= self.DECAY_FACTOR

            # set volume of signal, wave_form has amplitude 1 by construction
            wave_form[switch_idx::] *= self.__volumes[freq_idx]

            self.__data_matrix[freq_idx, :] = wave_form

        return np.mean(self.__data_matrix, 0)

    def _shift_x_data(self):
        x_data = np.ones_like(self.__x_data)
        for freq_idx, x in enumerate(np.array(self.__x_data)):
            # first shift x
            x += self.CHUNK*2*np.pi*self.__frequencies[freq_idx]/self.RATE
            # compute the multiple of 2pi that can be subtracted
            factor = np.floor(x[0]/(2*np.pi))
            # shift x_data to the left
            x_data[freq_idx, :] = x-factor*2*np.pi
        self.__x_data = x_data

    def _update_volume(self, note):
        self.__indices_to_update.append(self.__notes.index(note))

    def message_handler(self, address, content):
        if address == INSTRUMENT_INIT_ADDRESS:
            notes = pickle.loads(content)
            self.__init_sound(notes)
        elif address == INSTRUMENT_TARGET_ADDRESS:
            self._update_volume(content)

    async def loop(self):
        all_data = np.array([])
        while True:
            if len(self.__frequencies):
                # self._volume_decay()
                data = self._compute_current_signal()
                self.__indices_to_update = []
                self.__stream.write(data.astype(np.int16).tostring())
                self._shift_x_data()

                # all_data = np.concatenate([all_data, data])
                # if len(all_data) >= 100*self.CHUNK:
                #     with open('test.pkl', 'wb') as f:
                #         pickle.dump(all_data, f)
                    # break

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
