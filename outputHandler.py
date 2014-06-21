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

        if DeviceFactory.VISUALS in self.__output:
            self.__output[DeviceFactory.VISUALS].note_on(1,100)
#        self.__membraneViewer = Test()
        
        self.__now = time.time()
        self.__activeNotes = set()
        self.__neuron2NoteConversion = neuron2NoteConversion
        
        #Start with one note
#        self.__output['MIDI B'].note_on(1,100)

    def __setupInputs(self, inputList):
        self.__input = {}
        for name in inputList:
            self.__input[name] = \
                self.__getDevice(self.__name2Identifier[name], type = 'input')

    def updateObject(self, fired):
        neuron_ids = intersect1d(fired, pars['note_ids'])
        for neuron_id in neuron_ids:
            self.__output[DeviceFactory.OBJECT].note_on(neuron_id, pars['velocity'])

    def update(self,fired):
#        print 'es feuern', fired
        '''
        if len(self.__midi_timeactive>0):
            self.__midi_timeactive-=time.time()-now
            self.__midi_timeactive = midi_timeactive[midi_timeactive>=0]
        now = time.time()
        '''
        neuron_ids = intersect1d(fired, pars['note_ids'])
        ##################################################
                
        # turn new notes and concious states on and update the allfired-list
        n_fired = neuron_ids.__len__()
        if neuron_ids.__contains__(1):
            self.__neuron2NoteConversion = (4 if self.__neuron2NoteConversion==5 else 5)
            print '----------------------------------------key change'
        if n_fired > 0:
            for neuron_id in neuron_ids:
                for name, output in self.__output.iteritems():
                    if name != DeviceFactory.OBJECT:
                        output.note_on(
                            neuron2note(neuron_id,self.__neuron2NoteConversion),
                                        pars['velocity'])
                #if neuron_id>(pars['N']-80):
                #    midi.ausgang_concious.note_on(neuron2note(neuron_id,neuron2note_conversion),pars['velocity'])
                
#                if neuron_id<20:
#                     if midi_timeactive is None:
#                        midi.ausgang_soundextern.note_on(neuron2note(neuron_id,neuron2note_conversion),pars['velocity'])
#                        midi_timeactive = array([1])
#                    elif len(midi_timeactive)<=pars['midi_per_sec']:
#                        midi.ausgang_soundextern.note_on(neuron2note(neuron_id,neuron2note_conversion),pars['velocity'])
#                        midi_timeactive = array(midi_timeactive.tolist().append(1))
#            #if N_fired>=pars['N_concious']:
                #midi_id = mod(N_fired,127)
                #midi_id_extern = mod(N_fired,50)+70
                #print midi_id, N_fired
                
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
        '''
                # turn old notes off    
        neuron_ids = intersect1d(fired,pars['note_ids'])
        for neuron_id in neuron_ids:
            midi.ausgang.note_off(neuron2note(neuron_id,neuron2note_conversion),100)
            #midi.ausgang_concious.note_off(neuron2note(neuron_id,neuron2note_conversion),100)
#            midi.ausgang_soundextern.note_off(neuron2note(neuron_id,neuron2note_conversion),100)
            #if neuron_id>(pars['N']-80):
            #    midi.ausgang_concious.note_off(neuron2note(neuron_id,neuron2note_conversion),100)
            #if neuron_id<20:
            #    midi.ausgang_soundextern.note_off(neuron2note(neuron_id,neuron2note_conversion),100)
        #if N_fired>=pars['N_concious']:
        #    midi.ausgang_concious.note_off(midi_id,100)
        #    midi.ausgang_soundextern.note_off(midi_id_extern,100)
        for note_id in range(len(fired)):
            midi.ausgang.note_off(neuron2note(fired[note_id],neuron2note_conversion),100)
        '''




