#!/usr/bin/env python

""" DOCSTRING """

__author__ = "Benjamin Staude"
__email__ = "benjamin.staude@gmail.com"
__date__ = 140621

import pygame
import pygame.midi as pm
import time
import numpy as np
from Dunkel_functions import chordConversion, linear2grid

class Neuron2NoteConverter(object):
    def __init__(self, conversion=4, noteRange=range(1, 127)):
        self.__conversion = conversion
        self.__noteRange = noteRange

        alldur, allmoll = chordConversion()
        self.__durlist = np.intersect1d(self.__noteRange, alldur, True)
        self.__mollist = np.intersect1d(self.__noteRange, allmoll, True)

    def convert(self, neuron_id):
        # conversion_type: 1 - linear tonal arrangement
        #		2 - neurons are arranged on a grid, the row determines the note
        #		3 - all excitatory have one note, all inhibitory have another
        #		4 - linear tonal arrangement in C-dur
        #		5 - linear tonal arrangement in C-moll
        #print conversion_type

        # if self.__neuron2NoteConversion == 1:
        #     note = int(mod(neuron_id, 127)+1)
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
            note = self.__molllist[int(np.mod(neuron_id, len(self.__molllist)))]

        print note
        return note




class DeviceStruct(dict):
    def __init__(self, name='SimpleSynth virtual input', maxNumSignals=None,
                 updateInterval=1, instrument=1, velocity=64, noteRange=range(1,127)):
        self['name'] = name
        self['maxNumSignals'] = maxNumSignals
        self['updateInterval'] = updateInterval
        self['instrument'] = instrument
        self['velocity'] = velocity
        self['noteRange'] = noteRange


class DeviceFactory(object):
    NEURON_NOTES = 'SimpleSynth'
    OBJECT = 'MIDISPORT 2x2 Anniv Port BB'
    SYNTH = 'MIDISPORT 2x2 Anniv Port B'
    PIANO = 'MIDISPORT 2x2 Anniv Port A'
    VISUALS = 'Ploytec MIDI Cable'

    def __init__(self):
        self.__name2DeviceStruct = {
            self.NEURON_NOTES: DeviceStruct(noteRange = range(80,127)),

            self.OBJECT: DeviceStruct(name = self.OBJECT,
                                      maxNumSignals = 3,
                                      updateInterval = 45,
                                      velocity = 30),

            self.PIANO: DeviceStruct(name = self.PIANO,
                                     maxNumSignals = 2,
                                     updateInterval = 60,
                                     velocity = 80,
                                     noteRange = range(35,96)),

            self.SYNTH: DeviceStruct(name = self.SYNTH,
                                  maxNumSignals = 4,
                                  updateInterval = 5,
                                  velocity = 80),

            self.VISUALS: DeviceStruct(name = self.VISUALS,
                                      maxNumSignals = 5,
                                      updateInterval = 30),
            }

    def create(self, name):
        return OutputDevice(self.__name2DeviceStruct[name],
                            Neuron2NoteConverter(
                                noteRange=self.__name2DeviceStruct[name]['noteRange']
                            ))


class OutputDevice(pm.Output):
    def __init__(self, deviceStruct, neuron2NoteConverter):
        id = self.__getDeviceId(deviceStruct['name'])
        if id == -1:
            print "SETUP Warning: output: " + deviceStruct['name'] + " not available!!!"
        else:
            super(OutputDevice,self).__init__(id)
            self.__neuron2NoteConverter = neuron2NoteConverter;
            self.__name = deviceStruct['name']
            self.__velocity = deviceStruct['velocity']
            self.set_instrument(deviceStruct['instrument'])
            self.__maxNumSignals = deviceStruct['maxNumSignals']
            self.__updateInterval = deviceStruct['updateInterval']
            self.__onNotes = set()
            if self.__maxNumSignals is not None:
                self.__activeNotes = []
                self.__activeTimes = []
                self.__now = time.time()
            print "SETUP output: " + deviceStruct['name'] + " connected"

    def __getDeviceId(self, name):
        n_device = pm.get_count()
        foundId = -1
        for id in range(n_device):
            if int(pm.get_device_info(id)[1] == name) & \
                    int(pm.get_device_info(id)[3] == 1):
                foundId = id
        return foundId

    def setNeuron2NoteConversion(self, conversion):
        self.__neuron2NoteConversion = conversion



    def note_on(self, neuron_id):
        note = self.__neuron2NoteConverter.convert(neuron_id)
        """
        turn the midi-note on
        If maxNumSignals has been set, the note is only turned on if less than
        maxNumSignals are on. Additionally, notes that started more than updateInterval
        ago are removed from the activeNotes list.
        """
        self.__onNotes.add(note)
        if self.__maxNumSignals is None:
            super(OutputDevice, self).note_on(note, self.__velocity)
        else:
            now = time.time()
            # update active times of active notes and remove notes from list
            if len(self.__activeTimes) > 0:
                done = False
                idx = 0
                while not done:
                    if idx < len(self.__activeTimes):
                        self.__activeTimes[idx] += now-self.__now
                        if self.__activeTimes[idx] > self.__updateInterval:
                            self.__activeTimes.pop(idx)
                            self.__activeNotes.pop(idx)
                        else:
                            idx += 1
                    else:
                        done = True
            self.__now = now
            if len(self.__activeTimes) < self.__maxNumSignals:
#                print self.__name, note
                super(OutputDevice, self).note_on(note, self.__velocity)
#                if self.__name == OutputHandler.OBJECT:
                print 'note sent', self.__name, self.__now
                if self.__activeNotes.__contains__(note):
                    idx = self.__activeNotes.index(note)
                    self.__activeNotes.remove(note)
                    self.__activeTimes.pop(idx)
                self.__activeNotes.append(note)
                self.__activeTimes.append(0)

    def turnAllOff(self):
        for note in self.__onNotes:
            self.note_off(note, 100)
        self.__onNotes = set()

