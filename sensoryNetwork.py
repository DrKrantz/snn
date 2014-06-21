#!/usr/bin/env python

"""
NEEDS: 
    - Dunkel_pars.py
    - Dunkel_functions.py
    
    # Created by B. Staude to simulate the Thalamic Network (Figs. 3 and 4) of Destexhe 2009, J Comp Neurosci.
# Taken From Dunkel_Master_Cam
# version 1.0: included deadtime, 04.08.2011
"""

from scipy import *
from numpy import *

from numpy import ones,zeros,nonzero,sum,shape
#import pylab as pll
import pygame
import pygame.midi as pm
import time
import sys
#import pylab
#import scipy.io as sio

from Dunkel_pars import parameters
from outputHandler import OutputHandler, DeviceFactory
from inputHandler import InputHandler
from connectivityMatrix import ConnectivityMatrix

import pickle


class SensoryNetwork(object):
    def __init__(self):
        super(SensoryNetwork, self).__init__()
        self.inputHandler = InputHandler(inputList=[InputHandler.PARAMETERS],
                                         pars=parameters())
        
        self.pars = self.inputHandler.pars
        outputDeviceNames = [DeviceFactory.NEURON_NOTES]
        outputDevices = {}
        [outputDevices.__setitem__(
            devname, DeviceFactory().create(devname)) for devname in outputDeviceNames]
        self.outputHandler = OutputHandler(outputDevices)

        print "wiring...."
        self.__A = ConnectivityMatrix().get()
        print 'wiring completed'
        
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
        
    def start(self):
        t = 0
        deaddur = array([])  # duration (secs) the dead neurons have been dead
        deadIDs = array([],int)
        fired = array([])
        spiketimes = array([])  # spike times
        print self.pars
        while not self.inputHandler.webcamOpen:  # t<int(self.pars['Ts']/self.pars['h'])
            t += 1
            if t == 20:
                output = open('networkPars.pkl', 'wb')
                pickle.dump(self.pars, output)
                print 'parameters saved'
                output.close()
                 
            time.sleep(self.pars['pause'])
            
            ##### GET WEBCAM IMAGE AND UPDATE VIEWER ###########
            self.inputHandler.update()
            cam_external = self.inputHandler.webcam.getExternal()
            external = self.pars['midi_external'] + cam_external  # self.pars['cam_ext']
            self.outputHandler.turnOff()

            ########## UPDATE DEADIMES AND GET FIRED IDs  ###########
            # update deadtimes
            deaddur += self.pars['h']    # increment the time of the dead
            aliveID = nonzero(deaddur > self.pars['dead'])[0]
            if len(aliveID) > 0:
                deaddur = deaddur[aliveID[-1]+1::]
                deadIDs = deadIDs[aliveID[-1]+1::]

            fired = nonzero(self.__v >= self.pars['threshold'])[0]
            deadIDs = concatenate((deadIDs, fired))  # put fired neuron to death
            deaddur = concatenate((deaddur, zeros(shape(fired))))
            #spiketimes=concatenate((spiketimes,t*pars['h']*1000+0*fired))
            #neurons = concatenate((neurons,fired+1))
            extFired = self.inputHandler.getFired()
            fired = array(union1d(fired, extFired), int)
            # print 'fired: vor', fired, type(fired), 'nach', postfired, type(fired)
            self.__v[fired] = self.pars['EL']  # set spiked neurons to reset potential
            self.__w[fired] += self.__b[fired]  # increment adaptation variable of
                                                # fired neurons
            
#            allfired.extend(fired)
#            alltimes.extend(ones(shape(fired))*t*pars['h'])
                
            #### SEND TO HANDLER ###
            self.outputHandler.update(fired)
            self.outputHandler.updateObject(extFired)
                        
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
            self.__v[deadIDs] = self.pars['EL']  # clamp dead neurons to resting potential
            self.__w += self.pars['h'] * (self.__a * (self.__v - self.pars['EL']) -
                                          self.__w)/self.pars['tau_w']
            print 'g_e', self.__ge
            print 'g_i', self.__gi
            # raw_input('ok?')
    
if __name__ == '__main__':
    SensoryNetwork().start()
