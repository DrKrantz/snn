#!/usr/bin/env python

""" DOCSTRING """

__author__ = "Benjamin Staude"
__email__ = "benjamin.staude@gmail.com"
__date__ = 140801

from numpy import array, union1d
import pickle

import mido


class InputDevice:
    def __init__(self, midiport=None):
        self.__messages = []
        self.__inport = mido.open_input(midiport, False, self.__store_incoming)

    def __store_incoming(self, msg: mido.Message):
        if msg.type == 'note_on':
            self.__messages.append(msg.note)

    def update(self):
        content = self.__messages
        self.__messages = []
        return content


class KeyboardInput:
    def __init__(self, *args):
        self.triggered = array([], int)

    def update(self):
        fired = self.triggered
        self.triggered = array([], int)
        return fired

    def triggerSpike(self, key):
        self.triggered = union1d(self.triggered, array([key], int))


class GuiAdapter:
    NAME = 'Gui'

    def __init__(self, pars, *args):
        self.triggered = []
        self.pars = pars

    def on_par_receive(self, address, name, value):
        self.pars.update({name: float(value)})

    def on_spike_receive(self, address, neuron_id):
        self.triggered.append(int(neuron_id))

    def on_reset(self, _, pars_pkl):
        self.pars = pickle.loads(pars_pkl)

    def update(self, pars):
        fired = self.triggered
        self.triggered = []
        return {'pars': self.pars, 'fired': fired}


"""
class SensoryObject(InputDevice):
    NAME = 'USB MIDI Device'

    def __init__(self, midiport, pars):
        super(SensoryObject, self).__init__(self.midiport)
        self.pars = pars

    def update(self, pars):
        self.pars = pars
        MIDI_data = self.getData()
        fired = []
        if MIDI_data is not None:
            [fired.append(dd[1]) for dd in MIDI_data]
            print('object:', fired)
        return {'pars': self.pars, 'fired': array(fired, int)}
"""
