#!/usr/bin/env python

""" inputHandler.py: control all incoming signals """

__author__ = "Benjamin Staude"
__email__ = "benjamin.staude@gmail.com"
__date__ = 140620

from pygame import midi as pm
from numpy import array, intersect1d, unique

from webcam import Webcam
from inputDevices import InputDevice

from Dunkel_functions import note2neuron


class InputHandler(object):
    PARAMETERS = 'Virtual BCF2000'
    OBJECT = 'USB MIDI Device'  # 'USB MIDI Device'
    WEBCAM = 'webcam'

    def __init__(self, inputDevices=[], pars={}):
        self.pars=pars
        self.webcam = Webcam()
        # self.__inputs = {'webcam': self.webcam}
        # self.__setupInputs(inputList)
        self.__fired = array([], int)
        self.__inputDevices = inputDevices
        # self.__updateFunctions = {'Virtual BCF2000': self.__updateBCF,
        #                           'USB MIDI Device': self.__updateObject,
        #                           'webcam': self.webcam.update}
        #
    @property    
    def webcamOpen(self):
        return self.webcam.window.has_exit

    def getFired(self):
        return self.__fired

    def getPars(self):
        return self.pars
    
    def update(self):
        self.__fired = array([], int)
        self.webcam.update()
        ########## CONVERT MIDI INPUT TO NETWORK INPUT AND PROPERTIES ###############
        for device in self.__inputDevices:
            inputDict = device.update(self.pars)
            self.__fired += inputDict['fired']
            self.__fired = unique(self.__fired)
            self.pars.update(inputDict['pars'])


if __name__ == '__main__':
    pm.init()
    device = InputDevice('USB MIDI Device')  # Virtual BCF2000
    device.map_keys()
