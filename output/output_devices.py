import pygame.midi as pm
import numpy as np
import time
import pygame
import pickle
from pythonosc import udp_client

from . import instrument

pm.init()


def get_device_id(midi_port):
        for did in range(pm.get_count()):
            if int(pm.get_device_info(did)[1] == midi_port.encode()) & \
                    int(pm.get_device_info(did)[3] == 1):
                return did
        return -1


class MidiDevice(pm.Output):
    def __init__(self,
                 converter,
                 velocity=80,
                 midi_port='IAC Driver Bus 1',
                 max_num_signals=np.infty,
                 update_interval=0.1):
        self.converter = converter
        self.__velocity = velocity
        self.__max_num_signals = max_num_signals
        # notes that have been turned on longer than signal_duration are removed from the list
        self.__signal_duration = update_interval
        self.__on_notes = set()
        self.__active_notes = {}  # a dict of active notes {note1: on_duration1, note2: on_duration2, ...}
        self.__now = time.time()

        device_id = get_device_id(midi_port)
        if device_id == -1:
            print("SETUP Warning: output: " + midi_port + " not available!!!")
        else:
            super(MidiDevice, self).__init__(device_id)
            print("SETUP output: " + midi_port + " connected")

    def update(self, _, *args):
        print("SoundDevice: neurons received", args)
        notes = self.converter.convert(args)
        self.__update_active_notes()
        [self.note_on(note, self.__velocity) for note in notes]

    def turn_all_off(self, _,  *__):
        [self.note_off(note, 100) for note in self.__on_notes]
        self.__on_notes = set()

    def note_on(self, note, *args):
        """
        turn the midi-note on
        If __max_num_signals has been set, the note is only turned on if less than
        maxNumSignals are on. Additionally, notes that started longer than updateInterval
        ago are removed from the active_notes list.
        """
        #  turn on note if possible
        if len(self.__active_notes) < self.__max_num_signals:
            super(MidiDevice, self).note_on(note, *args)
            self.__on_notes.add(note)
            if self.__max_num_signals is not np.infty:
                self.__active_notes[note] = 0

    def __update_active_notes(self):
        # update active times of active notes and remove notes from list
        if self.__max_num_signals is not np.infty:
            now = time.time()
            to_remove = []
            for on_note, on_duration in self.__active_notes.items():
                self.__active_notes[on_note] += now - self.__now
                if self.__active_notes[on_note] > self.__signal_duration:
                    to_remove.append(on_note)

            [self.__active_notes.pop(on_note) for on_note in to_remove]

            self.__now = now


class AnalogDevice(object):
    def __init__(self, converter, velocity=80):
        self.converter = converter
        self.__velocity = velocity
        self.__player = OscDevice()
        self.__player.init_instrument(converter.midi_notes)

    def update(self, *args):
        notes = self.converter.convert(args)
        [self.__player.note_on(note) for note in notes]


class OscDevice(udp_client.SimpleUDPClient):
    def __init__(self, converter):
        self.converter = converter
        super(OscDevice, self).__init__(instrument.IP, instrument.PORT)

    def update(self, _, *args):
        notes = self.converter.convert(args)

        # print('forwarding {}'.format( notes ))
        self.send_message(instrument.UPDATE_ADDRESS, notes)

    def turn_all_off(self):
        pass

    def init_instrument(self, midi_notes):
        notes_pickle = pickle.dumps(midi_notes)
        self.send_message(instrument.INIT_ADDRESS, notes_pickle)


class SoundPlayer:
    RATE = 44100
    CHANNELS = 2

    def __init__(self):
        pygame.init()
        self.__sound = pygame.mixer.Sound(np.array([]))
        self.__create_sound()
        self.__channel = self.__sound.play()

    def __create_sound(self):
        num_samples = int(self.RATE * 1 / 1000.)
        bits = 16
        twopi = 2 * np.pi

        pygame.mixer.pre_init(44100, -bits, self.CHANNELS)
        pygame.init()

        max_sample = 2 ** (bits - 1) - 1
        sine = max_sample * np.sin(np.arange(num_samples) * twopi * 220 / self.RATE)

        num_damp_samp = int(self.RATE * 0.1)

        damp_vec = np.linspace(0, 1, num_damp_samp)
        sine[0:num_damp_samp] *= damp_vec
        sine[len(sine) - num_damp_samp::] *= damp_vec[::-1]

        #  add ending silence
        sine = np.concatenate([sine, np.zeros(int(self.RATE * 0.1))])

        #  generate signal for channels
        signal = np.array((sine, sine))  # default to LR

        signal = np.ascontiguousarray(signal.T.astype(np.int16))
        self.__sound = pygame.sndarray.make_sound(signal)

    def play(self):
        self.__channel = self.__sound.play()

    def get_busy(self):
        return self.__channel.get_busy()


if __name__ == '__main__':
    # note_converter = neuron_to_note.Neuron2NoteConverter(np.arange(1, 96), neuron_to_note.SCALE_MAJOR)
    # device = MidiDevice(note_converter, max_num_signals=2)
    # device = AnalogDevice(note_converter)
    # device.run()
    # device.play()

    from config import frequencies
    freqs = frequencies.get_octaves(n_oct=1, start_oct=4)
    notes = range(len(freqs))

    player = OscDevice()
    player.init_instrument(freqs)
    # time.sleep(2)
    #
    # k = 5
    # while True:
    #     played = random.sample(notes, k=1)
    #     player.note_on(played)
    #     # [player.note_on(note) for note in played]
    #     time.sleep(0.03)
