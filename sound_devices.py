import pygame.midi as pm
import numpy as np


pm.init()


class SoundDevice(pm.Output):
    def __init__(self, converter, velocity=80, midi_port='SimpleSynth virtual input'):
        self.converter = converter
        self.__velocity = velocity
        self._on_notes = np.array([])

        device_id = self.__get_device_id(midi_port)
        if device_id == -1:
            print("SETUP Warning: output: " + midi_port + " not available!!!")
        else:
            super(SoundDevice, self).__init__(device_id)
            print("SETUP output: " + midi_port + " connected")

    @staticmethod
    def __get_device_id(midi_port):
        found_id = -1
        for did in range(pm.get_count()):
            if int(pm.get_device_info(did)[1] == midi_port.encode()) & \
                    int(pm.get_device_info(did)[3] == 1):
                found_id = did
        return found_id

    def update(self, _, *args):
        print("SoundDevice: neurons received", args)
        notes = self.converter.convert(args)
        self._on_notes = np.union1d(self._on_notes, notes).astype('int')
        [self.note_on(note, self.__velocity) for note in notes]

    def turn_all_off(self, _,  *__):
        [self.note_off(note, 100) for note in self._on_notes]
        self._on_notes = np.array([])
