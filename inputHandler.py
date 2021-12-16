#!/usr/bin/env python

""" inputHandler.py: control all incoming signals """

__author__ = "Benjamin Staude"
__email__ = "benjamin.staude@gmail.com"
__date__ = 140620

from numpy import array, unique, union1d


class InputHandler(object):

    def __init__(self, spike_inputs, parameter_inputs, exc_ids, pars={}):
        self.pars = pars
        self.__exc_ids = exc_ids
        self.__fired = array([], int)  # these are not the neuronIDs, but the midi-channels!
        self.spike_devices = spike_inputs
        self.parameter_adapter = parameter_inputs

    def getFired(self):
        return self.__get_fired_exc_ids()

    def getPars(self):
        return self.pars

    def update(self):
        self.__fired = array([], int)
        # CONVERT MIDI INPUT TO NETWORK INPUT AND PROPERTIES ###############
        for device in self.spike_devices:
            fired = device.update()
            if len(self.__fired) == 0:  # avoid shape mismatch error when adding [1,2] to []
                self.__fired = fired
            else:
                self.__fired = union1d(fired, self.__fired)

        for device in self.parameter_adapter:
            inputDict = device.update(self.pars)
            if len(self.__fired) == 0:  # avoid shape mismatch error when adding [1,2] to []
                self.__fired = inputDict['fired']
            else:
                self.__fired = union1d(inputDict['fired'], self.__fired)
            self.pars.update(inputDict['pars'])

        self.__fired = array(unique(self.__fired), dtype=int)

    def __get_fired_exc_ids(self):
        return self.__exc_ids[self.__fired%len(self.__exc_ids)]

# if __name__ == '__main__':
# from inputDevices import InputDevice
#     pm.init()
#     device = InputDevice('USB MIDI Device')  # Virtual BCF2000
#     device.map_keys()
