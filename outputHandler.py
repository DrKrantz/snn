import time

import pygame
import pygame.midi as pm

# packages needed for the parameter-display
from pygame.locals import *
import pygame.font

from numpy import intersect1d, array

from Dunkel_pars import parameters
from Dunkel_functions import small2string, neuron2note, linear2grid
from display import Display
from outputDevices import DeviceFactory
global pars

pars = parameters()


class OutputHandler(object):

    def __init__(self, outputs, neuron2NoteConversion=4):
        super(OutputHandler, self).__init__()
        self.__display = Display(pars['N_col'], pars['N_row'],\
                ['Ne', 'Ni', 's_e', 's_i', 'tau_e', 'tau_i', 'midi_ext_e', 'midi_ext_i',
                 'cam_ext', 'cam_external_max'], 'lines')
        pm.init()
        self.__output = outputs

        # if DeviceFactory.VISUALS in self.__output:
        #     self.__output[DeviceFactory.VISUALS].note_on(1,100)
#        self.__membraneViewer = Test()
        
        self.__now = time.time()
        self.__activeNotes = set()
        self.__neuron2NoteConversion = neuron2NoteConversion
        

    def __setupInputs(self, inputList):
        self.__input = {}
        for name in inputList:
            self.__input[name] = \
                self.__getDevice(self.__name2Identifier[name], type = 'input')

    def updateObject(self, fired):
        # print 'ans Objekt gehen', fired
        neuron_ids = intersect1d(fired, pars['note_ids'])
        for neuron_id in neuron_ids:
            self.__output[DeviceFactory.OBJECT].note_on(neuron_id, pars['velocity'])

    def update(self,fired):
        # print 'es feuern', fired

        neuron_ids = intersect1d(fired, pars['note_ids'])
        self.__checkKeyChange(neuron_ids)

        n_fired = neuron_ids.__len__()
        if n_fired > 0:
            for neuron_id in neuron_ids:
                for name, output in self.__output.iteritems():
                    if name != DeviceFactory.OBJECT:
                        output.note_on(neuron_id)
                
#        self.__membraneViewer.move()        
        # display spikes and update display
        self.__display.update_fired(fired)
        self.__display.update_pars(
            ['cam_ext', 'midi_ext_e', 'midi_ext_i', 's_e', 's_i',
             'tau_e', 'tau_i', 'cam_external_max'])
        pygame.display.update()
        
        
    def turnOff(self):
        for outputName in self.__output.iterkeys():
            if outputName == DeviceFactory.NEURON_NOTES:
                self.__output[outputName].turnAllOff()


    def __checkKeyChange(self, neuron_ids):
        if len(neuron_ids)>17:
            self.__neuron2NoteConversion = (1 if self.__neuron2NoteConversion==7 else 7)
            self.__output[DeviceFactory.NEURON_NOTES].setNeuron2NoteConversion(
                self.__neuron2NoteConversion
            )
            # [output.setNeuron2NoteConversion(self.__neuron2NoteConversion) for
            #             name, output in self.__output.iteritems()]

            print '----------------------------------------key change'
