import pyaudio
import numpy as np
import pickle
import asyncio
import threading
import time
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from config import routing

p = pyaudio.PyAudio()


class SoundThread(threading.Thread):  # multiprocessing.Process
    FORMAT = pyaudio.paInt16
    RATE = 44100
    CHANNELS = 2
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


def update_volume_additive(current_volume):
    volume_increase = 1000
    return min(current_volume + volume_increase, OscInstrument.MAX_VOLUME)


def update_volume_to_max(current_volume):
    return OscInstrument.MAX_VOLUME


def decay_volume_exp(current_volume):
    return current_volume*OscInstrument.DECAY_FACTOR


class OscInstrument:
    FORMAT = pyaudio.paInt16
    RATE = 44100  # Hz
    CHANNELS = 2
    CHUNK = 1024
    DECAY_FACTOR = 0.98
    MAX_VOLUME = .85 * 32767

    server = None
    __frequencies = []
    __neuron_ids = []
    __volumes = []
    __indices_to_update = []
    __n_freqs = 0
    __data_matrix = np.array([])
    __x_data = np.array([])
    __LR_mask = np.array([])

    def __init__(self, volume_update_cb=None, volume_decay_cb=None, target_file=None):
        self.__create_stream()
        self.__volume_update_cb = update_volume_to_max if volume_update_cb is None else volume_update_cb
        self.__volume_decay_cb = decay_volume_exp if volume_decay_cb is None else volume_decay_cb
        self.__target_file = target_file
        self.all_data = []

    def __create_stream(self):
        self.__stream = p.open(format=self.FORMAT,
                               channels=self.CHANNELS,
                               rate=self.RATE,
                               input=False,
                               output=True,
                               frames_per_buffer=self.CHUNK)

    def __init_sound(self, ids, frequencies):
        self.__neuron_ids = ids
        self.__frequencies = frequencies
        self.__n_freqs = len(ids)
        self.__volumes = np.ones_like(self.__neuron_ids) * self.MAX_VOLUME / 10
        self.__data_matrix = np.ones((self.__n_freqs, self.CHANNELS * self.CHUNK))
        self.__LR_mask = []
        [self.__LR_mask.append(np.tile([L, 1-L], self.CHUNK)) for L in np.random.random(self.__n_freqs)]
        #  every x-value needs to be duplicated for stereo sound
        multiplied_range = np.resize(np.arange(self.CHUNK), (self.CHANNELS, self.CHUNK)).T.flatten()
        self.__x_data = np.mat(self.__frequencies).T * multiplied_range * 2 * np.pi / self.RATE
        # self.__x_data += 2 * np.pi * np.resize(np.random.rand(self.__n_freqs), (self.CHANNELS * self.CHUNK, self.__n_freqs)).T / self.RATE  # phase shift
        print('Instrument initialized with {} frequencies'.format(self.__n_freqs))

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
                self.__volumes[freq_idx] = self.__volume_update_cb(self.__volumes[freq_idx])
            else:
                self.__volumes[freq_idx] = self.__volume_decay_cb(self.__volumes[freq_idx])

            # set volume of signal, wave_form has amplitude 1 by construction
            wave_form[switch_idx::] *= self.__volumes[freq_idx]

            self.__data_matrix[freq_idx, :] = wave_form  # * self.__LR_mask[freq_idx]

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

    def __store_fired_ids(self, ids):
        for n_id in ids:
            if n_id in self.__neuron_ids:
                self.__indices_to_update.append(self.__neuron_ids.index(n_id))
            else:
                print('Note {} not in initialized notes. Ignoring'.format(n_id))

    def __store_and_write(self, data):
        self.all_data.extend(data)
        if len(self.all_data) >= 100 * self.CHUNK:
            with open(self.__target_file, 'wb') as f:
                pickle.dump(self.all_data, f)
            self.__target_file = None
            self.all_data = []

    def iterate(self, to_stream=True):
        data = self._compute_current_signal()
        if to_stream:
            self.__stream.write(data.astype(np.int16).tostring())

        self._shift_x_data()
        self.__indices_to_update = []
        return data

    def update_spiked(self, _, *content):
        # print('receiving {}'.format(content))
        self.__store_fired_ids(content)

    def init_notes(self, _, content):
        message = pickle.loads(content)
        self.__init_sound(message['ids'], message['frequencies'])

    async def loop(self):
        while True:
            if len(self.__frequencies):
                if self.__stream.get_write_available() > 0:  # Only compute chunk if stream can consume
                    data = self.iterate()
                    if self.__target_file is not None:
                        self.__store_and_write(data)

            await asyncio.sleep(self.CHUNK/self.RATE - 0.01)  # 0.01 is a extra buffer - time_passed

    async def init_main(self, instrument_address):
        dispatcher = Dispatcher()
        dispatcher.map(routing.INIT_INSTRUMENT, self.init_notes)
        dispatcher.map(routing.FIRING_NEURONS, self.update_spiked)

        self.server = AsyncIOOSCUDPServer(instrument_address, dispatcher, asyncio.get_event_loop())
        transport, protocol = await self.server.create_serve_endpoint()  # Create datagram endpoint and start serving
        print('Instrument server running, waiting for initialization')
        await self.loop()  # Enter main loop of program

        transport.close()  # Clean up serve endpoint

