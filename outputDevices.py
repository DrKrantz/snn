#!/usr/bin/env python

""" DOCSTRING """

__author__ = "Benjamin Staude"
__email__ = "benjamin.staude@gmail.com"
__date__ = 140621

import mido
import time
import json
from pythonosc.udp_client import SimpleUDPClient

import numpy as np
import sensoryNetwork
from Dunkel_functions import chordConversion, chromaticConversion


class Neuron2NoteConverter(object):
    def __init__(self, conversion=1, min_note=1, max_note=127):
        self.__conversion = conversion
        self.__noteRange = list(range(min_note, max_note))

        alldur, allmoll = chordConversion()
        self.__durlist = np.intersect1d(self.__noteRange, alldur)
        self.__mollist = np.intersect1d(self.__noteRange, allmoll)
        chromatic1, chromatic2 = chromaticConversion()
        self.__cromatic1 = np.intersect1d(self.__noteRange, chromatic1)
        self.__cromatic2 = np.intersect1d(self.__noteRange, chromatic2)

    def convert(self, neuron_id):
        """ convert neuronId to note value
            :param neuron_id:
            :return:
        conversion_type:
            1 - linear tonal arrangement
            2 - neurons are arranged on a grid, the row determines the note
            3 - all excitatory have one note, all inhibitory have another
            4 - linear tonal arrangement in C-dur
            5 - linear tonal arrangement in C-moll
        """
        note = int(np.mod(neuron_id, 127) + 1)
        if self.__conversion == 1:
            note = int(np.mod(neuron_id, 127)+1)
        # if self.__neuron2NoteConversion == 2:
        #     coord = linear2grid(neuron_id, pars['N_col'])
        #     note = coord[1]
        # if self.__neuron2NoteConversion == 3:
        #     if any((self.pars['Exc_ids'] - neuron_id) == 0):
        #         note = 120
        #     else:
        #         note = 20
        if self.__conversion == 4:
            note = self.__durlist[int(np.mod(neuron_id, len(self.__durlist)))]
        if self.__conversion == 5:
            note = self.__mollist[int(np.mod(neuron_id, len(self.__mollist)))]
        if self.__conversion == 6:
            note = self.__cromatic1[int(np.mod(neuron_id, len(self.__cromatic1)))]
        if self.__conversion == 7:
            note = self.__cromatic2[int(np.mod(neuron_id, len(self.__cromatic2)))]

        return note


class OutputDevice:
    def __init__(self, midiport='IAC Driver Bus 1', max_num_signals=None,
                 update_interval=1, instrument=1, velocity=64, min_note=1, max_note=127,
                 conversion=1):
        self.__port = mido.open_output(midiport)
        self.__converter = Neuron2NoteConverter(conversion, min_note, max_note)
        self.__velocity = velocity
        # self.set_instrument(deviceStruct['instrument'])  # TODO set instrument in mido (via channels?)

        self.__max_num_signals = max_num_signals
        self.__update_interval = update_interval
        self.__on_notes = set()
        if self.__max_num_signals is not None:
            self.__active_notes = []
            self.__active_times = []
            self.__now = time.time()

    def setNeuron2NoteConversion(self, conversion):
        self.__neuron2NoteConversion = conversion

    def note_on(self, neuron_id):
        note = self.__converter.convert(neuron_id)
        """
        turn the midi-note on
        If max_num_signals has been set, the note is only turned on if less than
        max_num_signals are on. Additionally, notes that started more than updateInterval
        ago are removed from the activeNotes list.
        """
        self.__on_notes.add(note)
        if self.__max_num_signals is None:
            self.__send_note(note)
        else:
            now = time.time()
            # update active times of active notes and remove notes from list
            if len(self.__active_times) > 0:
                done = False
                idx = 0
                while not done:
                    if idx < len(self.__active_times):
                        self.__active_times[idx] += now - self.__now
                        if self.__active_times[idx] > self.__update_interval:
                            self.__active_times.pop(idx)
                            self.__active_notes.pop(idx)
                        else:
                            idx += 1
                    else:
                        done = True
            self.__now = now
            if len(self.__active_times) < self.__max_num_signals:
                self.__send_note(note)
                if self.__active_notes.__contains__(note):
                    idx = self.__active_notes.index(note)
                    self.__active_notes.remove(note)
                    self.__active_times.pop(idx)
                self.__active_notes.append(note)
                self.__active_times.append(0)

    def __send_note(self, note, note_type='note_on'):
        self.__port.send(
            mido.Message(note_type, note=note, velocity=self.__velocity)
        )

    def turn_all_off(self):
        for note in self.__on_notes:
            if note != 1:
                    self.__send_note(note, 'note_off')
        self.__on_notes = set()


class DisplayAdapter:
    def __init__(self):
        self.client = SimpleUDPClient(sensoryNetwork.IP, sensoryNetwork.SPIKE_DISPLAY_PORT)

    def update(self, fired):
        self.client.send_message(sensoryNetwork.SPIKE_DISPLAY_ADDRESS, json.dumps(fired.tolist()))
