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
            super(SoundDevice, self).__init__(device_id)
            print("SETUP output: " + midi_port + " connected")

    def update(self, _, *args):
        print("SoundDevice: neurons received", args)
        notes = self.converter.convert(args)
        [self.__on_notes.add(int(note)) for note in notes]
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
        self.__on_notes.add(note)
        if self.__max_num_signals is None:
            super(SoundDevice, self).note_on(note, args)
        else:  # TODO: move this block to a separate function, called only once in update, not in every note_on
            now = time.time()
            # update active times of active notes and remove notes from list
            to_remove = []
            for on_note, on_duration in self.__active_notes.items():
                self.__active_notes[on_note] += now-self.__now
                if self.__active_notes[on_note] > self.__signal_duration:
                    to_remove.append(on_note)
            [self.__active_notes.pop(on_note) for on_note in to_remove]

            self.__now = now

            #  turn on note if possible
            if len(self.__active_notes) < self.__max_num_signals:
                super(SoundDevice, self).note_on(note, self.__velocity)
                self.__active_notes[note] = 0


if __name__ == '__main__':
    import neuron_to_note

    note_converter = neuron_to_note.Neuron2NoteConverter(np.arange(1, 96), neuron_to_note.SCALE_MAJOR)
    device = SoundDevice(note_converter, max_num_signals=2)
    device.update('uwe', 1, 2, 3, 4)
