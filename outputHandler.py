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
global pars

pars = parameters()

class DeviceStruct(dict):
    def __init__(self, name='SimpleSynth virtual input', maxNumSignals=None,
                 updateInterval=1, instrument=1, velocity=64):
        self['name'] = name
        self['maxNumSignals'] = maxNumSignals
        self['updateInterval'] = updateInterval
        self['instrument'] = instrument
        self['velocity'] = velocity

class OutputDevice(pm.Output):
    def __init__(self, deviceStruct):
        id = self.__getDeviceId(deviceStruct['name'])
        if id == -1:
            print "SETUP Warning: output: " + deviceStruct['name'] + " not available!!!"
        else:
            super(OutputDevice,self).__init__(id)
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
        
    def note_on(self, note, velocity):
        """
        turn the midi-note on
        If maxNumSignals has been set, the note is only turned on if less than
        maxNumSignals are on. Additionally, notes that started more than updateInterval 
        ago are removed from the activeNotes list.
        """
        self.__onNotes.add(note)
        if self.__maxNumSignals is None:
            super(OutputDevice,self).note_on(note, self.__velocity)
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
                super(OutputDevice,self).note_on(note,self.__velocity)
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

class OutputHandler(object):
    NEURON_NOTES = 'SimpleSynth'
    OBJECT = 'MIDISPORT 2x2 Anniv Port A'
    PIANO = 'MIDISPORT 2x2 Anniv Port B'
    VISUALS = 'Ploytec MIDI Cable'
    def __init__(self, outputList=[], neuron2NoteConversion=4):
        super(OutputHandler, self).__init__()
        self.__display = Display(pars['N_col'], pars['N_row'],\
                ['Ne', 'Ni', 's_e', 's_i', 'tau_e', 'tau_i', 'midi_ext_e', 'midi_ext_i',
                 'cam_ext', 'cam_external_max'], 'lines')
        self.__name2DeviceStruct = {
                self.NEURON_NOTES: DeviceStruct(),
#                'BCF2000':'Virtual BCF2000',
                self.OBJECT: DeviceStruct(name = self.OBJECT,
                                      maxNumSignals = 3,
                                      updateInterval = 45,
                                      velocity = 30),
                self.PIANO: DeviceStruct(name = self.PIANO,
                                      maxNumSignals = 10,
                                      updateInterval = 15),
                self.VISUALS: DeviceStruct(name = self.VISUALS,
                                          maxNumSignals = 5,
                                          updateInterval = 30)
                }
        pm.init()

        self.__setupOutputs(outputList)
        if self.VISUALS in self.__output:
            self.__output[self.VISUALS].note_on(1,100)
#        self.__membraneViewer = Test()
        
        self.__now = time.time()
        self.__activeNotes = set()
        self.__neuron2NoteConversion = neuron2NoteConversion
        
        #Start with one note
#        self.__output['MIDI B'].note_on(1,100)
    
    def __getDevice(self, deviceStruct, instrument=1, maxNumSignals=None):
        return OutputDevice(deviceStruct)
                
#        print "SETUP Warning: output: "+deviceStruct['name']+ " not available!!!"

    def __setupInputs(self, inputList):
        self.__input = {}
        for name in inputList:
            self.__input[name] = \
                self.__getDevice(self.__name2Identifier[name], type = 'input')
            
    def __setupOutputs(self, outputList):
        self.__output = {}
        for name in outputList:
            self.__output[name] = self.__getDevice(self.__name2DeviceStruct[name])
            
    def updateObject(self, fired):
        neuron_ids = intersect1d(fired, pars['note_ids'])
        for neuron_id in neuron_ids:
            self.__output[self.OBJECT].note_on(neuron_id, pars['velocity'])

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
                    if name != self.OBJECT:
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
            if outputName == OutputHandler.NEURON_NOTES:
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




