#!/usr/bin/env python

"""
NEEDS: 
    - Dunkel_pars.py
    - Dunkel_functions.py
    
    # Created by B. Staude to simulate the Thalamic Network (Figs. 3 and 4) of Destexhe 2009, J Comp Neurosci.
# Taken From Dunkel_Master_Cam
# version 1.0: included deadtime, 04.08.2011
"""

from numpy import ones, zeros, nonzero, sum, shape
import numpy as np
import time
import pygame
import pygame.locals
import sys

from Dunkel_pars import parameters
from outputHandler import OutputHandler
from inputHandler import InputHandler
import outputDevices
import inputDevices
from connectivityMatrix import ConnectivityMatrix
import settingsReader
from SimulationGui import Gui


class SensoryNetwork(object):
    def __init__(self, inputHandler, outputHandler, pars, connectivityMatrix):
        super(SensoryNetwork, self).__init__()
        self.inputHandler = inputHandler
        self.pars = pars
        self.outputHandler = outputHandler

        self.__A = connectivityMatrix
        
        n = self.pars['N']
        # vectors with parameters of adaptation and synapses
        self.__a =np. ones(n)
        self.__a[self.pars['Exc_ids']] = self.pars['a_e']
        self.__a[self.pars['Inh_ids']] = self.pars['a_i']
        self.__b = np.ones(n)
        self.__b[self.pars['Exc_ids']] = self.pars['b_e']
        self.__b[self.pars['Inh_ids']] = self.pars['b_i']
        self.__ge = self.pars['s_e']*np.ones(n)  # conductances of excitatory synapses
        self.__gi = self.pars['s_i']*np.ones(n)  # conductances of inhibitory synapses
        
        self.__v = self.pars['EL']*ones(n)  # Initial values of the mmbrane potential v
        self.__w = self.__b  # Initial values of adaptation variable w
        self.__neurons = np.array([])   # neuron IDs
        self.__hasPrinted = False
        self.deaddur = np.array([])  # duration (secs) the dead neurons have been dead
        self.deadIDs = np.array([], int)
        
    def update(self):
        # GET WEBCAM IMAGE, UPDATE VIEWER & INPUTS ###########
        self.inputHandler.update()
        self.pars.update(self.inputHandler.getPars())
        external = self.pars['midi_external']
        self.outputHandler.turnOff()

        # UPDATE DEADIMES AND GET FIRED IDs  ###########
        # update deadtimes
        self.deaddur += self.pars['h']    # increment the time of the dead
        aliveID = nonzero(self.deaddur > self.pars['dead'])[0]
        if len(aliveID) > self.pars['N_concious']:
            self.deaddur = self.deaddur[aliveID[-1]+1::]
            self.deadIDs = self.deadIDs[aliveID[-1]+1::]

        fired = nonzero(self.__v >= self.pars['threshold'])[0]
        self.deadIDs = np.concatenate((self.deadIDs, fired))  # put fired neuron to death
        self.deaddur = np.concatenate((self.deaddur, zeros(shape(fired))))
        extFired = self.inputHandler.getFired()

        fired = np.array(np.union1d(fired, extFired), int)

        self.__v[fired] = self.pars['EL']  # set spiked neurons to reset potential
        self.__w[fired] += self.__b[fired]  # increment adaptation variable of fired neurons

        # SEND TO HANDLER ###
        self.outputHandler.update(fired)

        # update conductances of excitatory synapses
        fired_e = np.intersect1d(fired, self.pars['Exc_ids'])  # spiking e-neurons
        nPreSp_e = sum(self.__A[:, fired_e], axis=1)  # number of presynaptic e-spikes
        self.__ge += -self.pars['h'] * self.__ge/self.pars['tau_e'] + \
                     nPreSp_e * self.pars['s_e']

        # update conductances of inh. synapses
        fired_i = np.intersect1d(fired, self.pars['Inh_ids'])  # spiking i-neurons
        nPreSp_i = sum(self.__A[:, fired_i], axis=1)  # number of presynaptic i-spikes
        self.__gi += -self.pars['h'] * self.__gi/self.pars['tau_i'] + \
                    nPreSp_i * self.pars['s_i']

        # update membrane and adaptation variable
        self.__v += self.pars['h']*(-self.pars['gL']*(self.__v-self.pars['EL']) +
              self.pars['gL']*self.pars['Delta']*np.exp((self.__v-self.pars['threshold'])/self.pars['Delta']) -
              self.__w/self.pars['S'] - self.__ge*(self.__v-self.pars['Ee'])/self.pars['S'] -
              self.__gi*(self.__v-self.pars['Ei'])/self.pars['S'])/self.pars['Cm'] + \
              self.pars['h']*external/self.pars['Cm']
        self.__v[self.deadIDs] = self.pars['EL']  # clamp dead neurons to resting potential
        self.__w += self.pars['h'] * (self.__a * (self.__v - self.pars['EL']) -
                                      self.__w)/self.pars['tau_w']


class DeviceManager:
    def __init__(self, devices, pars):
        self.deviceSettings = devices
        self.pars = pars
        self.inputs = {}
        self.outputs = {}
        self.__createInputDevices(pars)
        self.__createOutputDevices()

    def __createInputDevices(self, pars):
        for devicename, midiport in self.deviceSettings['inputs'].items():
            self.inputs[devicename] = getattr(inputDevices, devicename)(midiport, pars)

    def __createOutputDevices(self):
        for devicename, midiport in self.deviceSettings['outputs'].items():
            self.outputs[devicename] = getattr(outputDevices, devicename)(midiport)

    def getInputDevices(self):
        return list(self.inputs.values())


class MainApp:
    def __init__(self, deviceManager, gui, pars):
        self.__fullscreen = False

        self.pars = pars
        self.keyboardInput = deviceManager.inputs['KeyboardInput']

        inputHandler = InputHandler(
            inputDevices=deviceManager.getInputDevices(),
            pars=pars
        )
        outputHandler = OutputHandler(deviceManager.outputs, pars)

        print("wiring....")
        connectivityMatrix = ConnectivityMatrix().get()
        print('wiring completed')

        self.network = SensoryNetwork(inputHandler, outputHandler, pars, connectivityMatrix)
        if self.network is not None:
            self.run()

    def input(self, events):
        for event in events:
            if event.type == pygame.locals.QUIT:
                sys.exit(0)
            elif event.type == pygame.locals.KEYDOWN:
                if event.dict['key'] == pygame.locals.K_ESCAPE:
                    sys.exit(0)
                elif event.dict['key'] == pygame.locals.K_f:
                    self.__fullscreen = not self.__fullscreen
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
        lastUpdated = time.time()
        while True:
            self.input(pygame.event.get())
            if time.time()-lastUpdated < self.pars['pause']:
                pass
            else:
                self.network.update()
                lastUpdated = time.time()


if __name__ == '__main__':
    pygame.init()
    pars = parameters()
    settingsFile = 'settings.csv'
    for i, value in enumerate(sys.argv):
        if value == '-f':
            settingsFile = sys.argv[i+1]
        if value == '-w':
            pars['screen_size'][0] = int(sys.argv[i+1])
        if value == '-h':
            pars['screen_size'][1] = int(sys.argv[i+1])

    print('Using settings from', settingsFile)

    settingsReaderClass = settingsReader.SettingsReader(settingsFile)
    devices = settingsReaderClass.getDevices()
    gui = Gui(pars)
    dm = DeviceManager(devices, pars)
    app = MainApp(dm, gui, pars)
    # app.run()
