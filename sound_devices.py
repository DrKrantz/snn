import pygame.midi as pm
import numpy as np
import time


pm.init()


def get_device_id(midi_port):
        for did in range(pm.get_count()):
            if int(pm.get_device_info(did)[1] == midi_port.encode()) & \
                    int(pm.get_device_info(did)[3] == 1):
                return did
        return -1


class SoundDevice(pm.Output):
    def __init__(self,
                 converter,
                 velocity=80,
                 midi_port='IAC Driver Bus 1',
                 max_num_signals=None,
                 update_interval=0.1):
        self.converter = converter
        self.__velocity = velocity
        self.__max_num_signals = max_num_signals
        self.__update_interval = update_interval
        self.__on_notes = set()
        self.__active_times = []
        self.__active_notes = []
        self.__now = time.time()

        device_id = get_device_id(midi_port)
        if device_id == -1:
            print("SETUP Warning: output: " + midi_port + " not available!!!")
        else:
            super(SoundDevice, self).__init__(device_id)
            print("SETUP output: " + midi_port + " connected")

    def update(self, _, *args):
        print("SoundDevice: neurons received", args)
        notes = self.converter.convert(args)
        self.__on_notes = np.union1d(self.__on_notes, notes).astype('int')
        [self.note_on(note, self.__velocity) for note in notes]

    def turn_all_off(self, _,  *__):
        [self.note_off(note, 100) for note in self.__on_notes]
        self.__on_notes = np.array([])
        self.__active_times = []
        self.__active_notes = []

    def note_on(self, neuron_id, *args):
        note = self.converter.convert(neuron_id)
        """
        turn the midi-note on
        If __max_num_signals has been set, the note is only turned on if less than
        maxNumSignals are on. Additionally, notes that started longer than updateInterval
        ago are removed from the active_notes list.
        """
        self.__on_notes.add(note)
        if self.__max_num_signals is None:
            super(SoundDevice, self).note_on(note, args)
        else:
            now = time.time()
            # update active times of active notes and remove notes from list
            if len(self.__active_times) > 0:
                done = False
                idx = 0
                while not done:
                    if idx < len(self.__active_times):
                        self.__active_times[idx] += now-self.__now
                        if self.__active_times[idx] > self.__update_interval:
                            self.__active_times.pop(idx)
                            self.__active_notes.pop(idx)
                        else:
                            idx += 1
                    else:
                        done = True
            self.__now = now
            if len(self.__active_times) < self.__max_num_signals:
                super(SoundDevice, self).note_on(note, self.__velocity)
                if self.__active_notes.__contains__(note):
                    idx = self.__active_notes.index(note)
                    self.__active_notes.remove(note)
                    self.__active_times.pop(idx)
                self.__active_notes.append(note)
                self.__active_times.append(0)
