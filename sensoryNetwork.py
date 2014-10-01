#!/usr/bin/env python

"""
NEEDS: 
    - Dunkel_pars.py
    - Dunkel_functions.py
    
    # Created by B. Staude to simulate the Thalamic Network (Figs. 3 and 4) of Destexhe 2009, J Comp Neurosci.
# Taken From Dunkel_Master_Cam
# version 1.0: included deadtime, 04.08.2011
"""

from numpy import *
from numpy import ones,zeros,nonzero,sum,shape
import time
import os
import pygame
import pygame.locals
import sys

from Dunkel_pars import parameters
from outputHandler import OutputHandler
from outputDevices import DeviceFactory
from inputHandler import InputHandler
import inputDevices
from connectivityMatrix import ConnectivityMatrix
import settingsReader

class SensoryNetwork(object):
    def __init__(self, inputHandler, outputHandler, pars, connectivityMatrix):
        super(SensoryNetwork, self).__init__()
        self.inputHandler = inputHandler
        self.pars = pars
        self.outputHandler = outputHandler
	self.outputHandler.update(array([1]))

        # value = raw_input('setup ok? [y]/n \n')
        # if value == 'n':
        #     return

        self.__A = connectivityMatrix

        
        N = self.pars['N']
        #vectors with parameters of adaptation and synapses
        self.__a = ones(N)
        self.__a[self.pars['Exc_ids']] = self.pars['a_e']
        self.__a[self.pars['Inh_ids']] = self.pars['a_i']
        self.__b = ones(N)
        self.__b[self.pars['Exc_ids']] = self.pars['b_e']
        self.__b[self.pars['Inh_ids']] = self.pars['b_i']
        self.__ge = self.pars['s_e']*ones((N))  # conductances of excitatory synapses
        self.__gi = self.pars['s_i']*ones((N))  # conductances of inhibitory synapses
        
        self.__v = self.pars['EL']*ones((N))  # Initial values of the mmbrane potential v
        self.__w = self.__b  # Initial values of adaptation variable w
        self.__neurons = array([])   # neuron IDs
        self.__hasPrinted = False
        self.deaddur = array([])  # duration (secs) the dead neurons have been dead
        self.deadIDs = array([],int)
        
    def update(self): # spike times ):

        # t += 1
        # if t == 20:
        #     output = open('networkPars.pkl', 'wb')
        #     pickle.dump(self.pars, output)
        #     print 'parameters saved'
        #     output.close()

        time.sleep(self.pars['pause'])

        ##### GET WEBCAM IMAGE, UPDATE VIEWER & INPUTS ###########
        self.inputHandler.update()
        self.pars.update(self.inputHandler.getPars())
        external = self.pars['midi_external']
        self.outputHandler.turnOff()

        ########## UPDATE DEADIMES AND GET FIRED IDs  ###########
        # update deadtimes
        self.deaddur += self.pars['h']    # increment the time of the dead
        aliveID = nonzero(self.deaddur > self.pars['dead'])[0]
        if len(aliveID) > self.pars['N_concious']:
            self.deaddur = self.deaddur[aliveID[-1]+1::]
            self.deadIDs = self.deadIDs[aliveID[-1]+1::]

        fired = nonzero(self.__v >= self.pars['threshold'])[0]
        self.deadIDs = concatenate((self.deadIDs, fired))  # put fired neuron to death
        self.deaddur = concatenate((self.deaddur, zeros(shape(fired))))
        #spiketimes=concatenate((spiketimes,t*pars['h']*1000+0*fired))
        #neurons = concatenate((neurons,fired+1))
        extFired = self.inputHandler.getFired()
        # if len(extFired)>0:
        #     print 'fired', extFired

        fired = array(union1d(fired, extFired), int)


        # print 'fired: vor', fired, type(fired), 'nach', postfired, type(fired)
        self.__v[fired] = self.pars['EL']  # set spiked neurons to reset potential
        self.__w[fired] += self.__b[fired]  # increment adaptation variable of
                                            # fired neurons

#            allfired.extend(fired)
#            alltimes.extend(ones(shape(fired))*t*pars['h'])

        #### SEND TO HANDLER ###
        self.outputHandler.update(fired)
        # self.outputHandler.updateObject(extFired)

        # update conductances of excitatory synapses
        fired_e = intersect1d(fired, self.pars['Exc_ids'])  # spiking e-neurons
        nPreSp_e = sum(self.__A[:, fired_e], axis=1)  # number of presynaptic e-spikes
        self.__ge += -self.pars['h'] * self.__ge/self.pars['tau_e'] + \
                    nPreSp_e * self.pars['s_e']

        # update conductances of inh. synapses
        fired_i = intersect1d(fired, self.pars['Inh_ids'])  # spiking i-neurons
        nPreSp_i = sum(self.__A[:, fired_i], axis=1)  # number of presynaptic i-spikes
        self.__gi += -self.pars['h'] * self.__gi/self.pars['tau_i'] + \
                    nPreSp_i * self.pars['s_i']

        #update membrane and adaptation variable
        self.__v += self.pars['h']*(-self.pars['gL']*(self.__v-self.pars['EL']) + \
              self.pars['gL']*self.pars['Delta']*exp((self.__v-self.pars['threshold'])/self.pars['Delta']) \
              -self.__w/self.pars['S'] - self.__ge*(self.__v-self.pars['Ee'])/self.pars['S'] \
              -self.__gi*(self.__v-self.pars['Ei'])/self.pars['S'] )/self.pars['Cm'] \
              + self.pars['h']*external/self.pars['Cm']
        self.__v[self.deadIDs] = self.pars['EL']  # clamp dead neurons to resting potential
        self.__w += self.pars['h'] * (self.__a * (self.__v - self.pars['EL']) -
                                      self.__w)/self.pars['tau_w']
        # print 'g_e', self.__ge
        # print 'g_i', self.__gi
        # raw_input('ok?')

class DeviceManager:
    def __init__(self, devices, pars):
        self.devices = devices
        self.pars = pars
        self.inputs = {}
        # print self.devices
        self.__createInputDevices(pars)

    def __createInputDevices(self, pars):
        inputs = {}
        for devicename, midiport in self.devices['inputs'].iteritems():
            self.inputs[devicename] = getattr(inputDevices, devicename)(pars)

    def getInputDevices(self):
        return self.inputs.values()

class MainApp:
    def __init__(self, deviceManager, pars):
        self.__fullscreen = False
        pygame.init()
        pars=pars
        bcf = inputDevices.BCF(pars)
        # sensoryObject = inputDevices.SensoryObject(pars)
        inputHandler = InputHandler(
            inputDevices=deviceManager.getInputDevices(), #,, sensoryObjectInputHandler.OBJECT, , sensoryObject,
            pars=pars
        )
        simpleSynth = DeviceFactory().create(DeviceFactory.NEURON_NOTES)
        print 'created'
        outputDevices = {DeviceFactory.NEURON_NOTES: simpleSynth}
        # outputDeviceNames = [DeviceFactory.NEURON_NOTES]
        # ''', DeviceFactory.SYNTH,
        #                      DeviceFactory.VISUALS,
        #                      DeviceFactory.ATHMOS
        # '''
        #
        # [outputDevices.__setitem__(
        #     devname, DeviceFactory().create(devname)) for devname in outputDeviceNames
        # ]
        outputHandler = OutputHandler(outputDevices)

        print "wiring...."
        connectivityMatrix = ConnectivityMatrix().get()
        print 'wiring completed'

        self.network = SensoryNetwork(inputHandler, outputHandler, pars, connectivityMatrix)
        if self.network is not None:
            self.run()

    def input(self,events):
        for event in events:
            if event.type == pygame.locals.QUIT:
                sys.exit(0)
            elif event.type == pygame.locals.KEYDOWN:
                if event.dict['key'] == pygame.locals.K_ESCAPE:
                    sys.exit(0)
                elif event.dict['key'] == pygame.locals.K_f:
                    self.__fullscreen = not(self.__fullscreen)
                    if self.__fullscreen:
                        pygame.display.set_mode(
                            self.network.outputHandler.display.spikeScreenSize,
                            pygame.locals.FULLSCREEN
                        )
                    else:
                        pygame.display.set_mode(
                            self.network.outputHandler.display.spikeScreenSize
                        )
                elif event.dict['key'] == pygame.locals.K_1:
                    self.keyboardInput.triggerSpike(1)
                elif event.dict['key'] == pygame.locals.K_2:
                    self.keyboardInput.triggerSpike(100)
                elif event.dict['key'] == pygame.locals.K_3:
                    self.keyboardInput.triggerSpike(150)
                elif event.dict['key'] == pygame.locals.K_4:
                    self.keyboardInput.triggerSpike(200)
                elif event.dict['key'] == pygame.locals.K_5:
                    self.keyboardInput.triggerSpike(300)
                elif event.dict['key'] == pygame.locals.K_6:
                    self.keyboardInput.triggerSpike(140)
                elif event.dict['key'] == pygame.locals.K_7:
                    self.keyboardInput.triggerSpike(150)
                elif event.dict['key'] == pygame.locals.K_8:
                    self.keyboardInput.triggerSpike(60)
                elif event.dict['key'] == pygame.locals.K_9:
                    self.keyboardInput.triggerSpike(270)
                elif event.dict['key'] == pygame.locals.K_0:
                    self.keyboardInput.triggerSpike(180)

    def run(self):
        updInt = .05
        now = time.time()
        while True:
            self.input(pygame.event.get())
            # if time.time()-now<updInt:
            #     pass
            # else:
            self.network.update()
            now = time.time()


if __name__ == '__main__':
    pars = parameters()
    settingsReaderClass = settingsReader.SettingsReader(
        os.getenv("HOME") + "/" + "settings.csv")
    devices = settingsReaderClass.getDevices()
    settingsReaderClass = None
    dm = DeviceManager(devices, pars)

    app = MainApp(dm, pars)
    app.run()
