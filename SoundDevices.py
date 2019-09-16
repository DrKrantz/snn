import pygame.midi as pm


pm.init()


class SoundDevice(pm.Output):
    def __init__(self, velocity=80, note_range=range(1, 96), midi_port='SimpleSynth virtual input'):
        self.__velocity = velocity

        device_id = self.__get_device_id(midi_port)
        if device_id == -1:
            print("SETUP Warning: output: " + midi_port + " not available!!!")
        else:
            super(SoundDevice, self).__init__(device_id)
            print("SETUP output: " + midi_port + " connected")

    @staticmethod
    def __get_device_id(midi_port):
        n_device = pm.get_count()
        found_id = -1
        for devid in range(n_device):
            if int(pm.get_device_info(devid)[1] == midi_port.encode()) & \
                    int(pm.get_device_info(devid)[3] == 1):
                found_id = devid
        return found_id

    def update(self, address, *args):
        print("SoundDevice: notes played", args)
        for note in args:
            super(SoundDevice, self).note_on(note, self.__velocity)
