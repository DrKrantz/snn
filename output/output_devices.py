import pygame.midi as pm
import numpy as np
import time
import pickle
from pythonosc import udp_client

from config import routing

from . import neuron_to_note
from . import instrument


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

        pm.init()

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


class OscDevice(udp_client.SimpleUDPClient):
    def __init__(self, converter, instrument_address):
        self.converter = converter
        super(OscDevice, self).__init__(instrument_address[0], instrument_address[1])

    def update(self, _, *args):
        notes = self.converter.convert(args)

        # print('forwarding {}'.format( notes ))
        self.send_message(routing.FIRING_NEURONS, notes)

    def turn_all_off(self):
        pass  # TODO: force note off via osc

    def init_instrument(self, _, content):
        neuron_ids = pickle.loads(content)
        frequencies = neuron_to_note.get_frequencies_for_range(440, 1200, len(neuron_ids))
        message = {'ids': neuron_ids,
                   'frequencies': frequencies}

        self.send_message(routing.INIT_INSTRUMENT, pickle.dumps(message))
