#!/usr/bin/env python

""" DOCSTRING """

__author__ = "Benjamin Staude"
__email__ = "benjamin.staude@gmail.com"
__date__ = 140621

import pygame
import pygame.midi as pm
import time
from Dunkel_functions import neuron2note


class DeviceStruct(dict):
    def __init__(self, name='SimpleSynth virtual input', maxNumSignals=None,
                 updateInterval=1, instrument=1, velocity=64):
        self['name'] = name
        self['maxNumSignals'] = maxNumSignals
        self['updateInterval'] = updateInterval
        self['instrument'] = instrument
        self['velocity'] = velocity


class DeviceFactory(object):
    NEURON_NOTES = 'SimpleSynth'
    OBJECT = 'MIDISPORT 2x2 Anniv Port BB'
    SYNTH = 'MIDISPORT 2x2 Anniv Port B'
    PIANO = 'MIDISPORT 2x2 Anniv Port A'
    VISUALS = 'Ploytec MIDI Cable'

    def __init__(self):
        self.__name2DeviceStruct = {
            self.NEURON_NOTES: DeviceStruct(),
#                'BCF2000':'Virtual BCF2000',
            self.OBJECT: DeviceStruct(name = self.OBJECT,
                                  maxNumSignals = 3,
                                  updateInterval = 45,
                                  velocity = 30),
            self.PIANO: DeviceStruct(name = self.PIANO,
                                  maxNumSignals = 2,
                                  updateInterval = 60),
            self.SYNTH: DeviceStruct(name = self.SYNTH,
                                  maxNumSignals = 4,
                                  updateInterval = 5),
            self.VISUALS: DeviceStruct(name = self.VISUALS,
                                      maxNumSignals = 5,
                                      updateInterval = 30)
            }

    def create(self, name):
        return OutputDevice(self.__name2DeviceStruct[name])


class OutputDevice(pm.Output):
    def __init__(self, deviceStruct, neuron2NoteConversion=4):
        id = self.__getDeviceId(deviceStruct['name'])
        if id == -1:
            print "SETUP Warning: output: " + deviceStruct['name'] + " not available!!!"
        else:
            super(OutputDevice,self).__init__(id)
            self.__neuron2NoteConversion = neuron2NoteConversion;
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

    def note_on(self, neuron_id, velocity):
        note = neuron2note(neuron_id, self.__neuron2NoteConversion)
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
