#!/usr/bin/env python

""" inputHandler.py: control all incoming signals """

__author__ = "Benjamin Staude"
__email__ = "benjamin.staude@gmail.com"
__date__ = 140620

from pygame import midi as pm
from numpy import array, unique, union1d
from V1.inputDevices import InputDevice


class InputHandler(object):
    PARAMETERS = 'Virtual BCF2000'
    OBJECT = 'USB MIDI Device'  # 'USB MIDI Device'
    WEBCAM = 'webcam'

    def __init__(self, inputDevices=[], pars={}):
        self.pars = pars
        self.__fired = array([], int)
        self.inputDevices = inputDevices

    def getFired(self):
        return self.__fired

    def getPars(self):
        return self.pars

    def update(self):
        self.__fired = array([], int)
        # CONVERT MIDI INPUT TO NETWORK INPUT AND PROPERTIES ###############
        for device in self.inputDevices:
            inputDict = device.update(self.pars)
            if len(self.__fired) == 0:  # avoid shape mismatch error when adding [1,2] to []
                self.__fired = inputDict['fired']
            else:
                self.__fired = union1d(inputDict['fired'], self.__fired)
            self.__fired = unique(self.__fired)
            self.pars.update(inputDict['pars'])


if __name__ == '__main__':
    pm.init()
    device = InputDevice('USB MIDI Device')  # Virtual BCF2000
    device.map_keys()
