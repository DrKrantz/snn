#!/usr/bin/env python

"""
NEEDS: 
    - Dunkel_pars.py
    - Dunkel_functions.py
    
    # Created by B. Staude to simulate the Thalamic Network (Figs. 3 and 4) of Destexhe 2009, J Comp Neurosci.
# Taken From Dunkel_Master_Cam
# version 1.0: included deadtime, 04.08.2011
"""
import json

import numpy as np
import time
import sys

from Dunkel_pars import parameters
from outputHandler import OutputHandler
from inputHandler import InputHandler
import outputDevices
import inputDevices
from connectivityMatrix import ConnectivityMatrix
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import asyncio
import pickle


IP = "localhost"
GUI_PORT = 1337
SPIKE_DISPLAY_PORT = 1338
SPIKE_DISPLAY_ADDRESS = '/display_spikes'
GUI_PAR_ADDRESS = '/gui_pars'
GUI_SPIKE_ADDRESS = '/gui_spikes'


class Recorder:
    def __init__(self, n):
        self.done = False
        self.__k = 0
        self.__nIter = 400
        self.__vRec = np.zeros((n, self.__nIter))

    def record(self, v):
        self.__vRec[:, self.__k] = v
        self.__k += 1

        if self.__k >= self.__nIter:
            self.done = True
            self.__write()

    def __write(self):
        print('--------- WRITING WRITING --------------')
        with open('./data/v_rec.pkl', 'wb') as f:
            pickle.dump(self.__vRec, f)


class SensoryNetwork(object):
    def __init__(self, inputHandler, outputHandler, pars, connectivityMatrix):
        super(SensoryNetwork, self).__init__()
        self.inputHandler = inputHandler
        self.pars = pars
        self.outputHandler = outputHandler

        self.__A = connectivityMatrix
        
        n = self.pars['N']
        # vectors with parameters of adaptation and synapses
        self.__a = np. ones(n)
        self.__a[self.pars['Exc_ids']] = self.pars['a_e']
        self.__a[self.pars['Inh_ids']] = self.pars['a_i']
        self.__b = np.ones(n)
        self.__b[self.pars['Exc_ids']] = self.pars['b_e']
        self.__b[self.pars['Inh_ids']] = self.pars['b_i']
        self.__ge = self.pars['s_e']*np.ones(n)  # conductances of excitatory synapses
        self.__gi = self.pars['s_i']*np.ones(n)  # conductances of inhibitory synapses
        
        self.__v = self.pars['EL']*np.ones(n)  # Initial values of the mmbrane potential v
        self.__w = self.__b  # Initial values of adaptation variable w
        self.__neurons = np.array([])   # neuron IDs
        self.__hasPrinted = False
        self.deaddur = np.array([])  # duration (secs) the dead neurons have been dead
        self.deadIDs = np.array([], int)
        self.__recorder = Recorder(n)
        
    def update(self):
        # GET WEBCAM IMAGE, UPDATE VIEWER & INPUTS ###########
        self.inputHandler.update()
        self.pars.update(self.inputHandler.getPars())

        self.outputHandler.turn_off()

        # UPDATE DEADIMES AND GET FIRED IDs  ###########
        # update deadtimes
        self.deaddur += self.pars['h']    # increment the time of the dead
        aliveID = np.nonzero(self.deaddur > self.pars['dead'])[0]
        if len(aliveID) > self.pars['N_concious']:
            self.deaddur = self.deaddur[aliveID[-1]+1::]
            self.deadIDs = self.deadIDs[aliveID[-1]+1::]

        fired = np.nonzero(self.__v >= self.pars['threshold'])[0]
        self.deadIDs = np.concatenate((self.deadIDs, fired))  # put fired neuron to death
        self.deaddur = np.concatenate((self.deaddur, np.zeros_like(fired)))
        extFired = self.inputHandler.getFired()
        self.outputHandler.update_external(extFired)

        fired = np.array(np.union1d(fired, extFired), int)

        self.__v[fired] = self.pars['EL']  # set spiked neurons to reset potential
        self.__w[fired] += self.__b[fired]  # increment adaptation variable of fired neurons

        # SEND TO HANDLER ###
        self.outputHandler.update(fired)

        # update conductances of excitatory synapses
        external_e = np.random.poisson(self.pars['lambda_e'] * self.pars['h'])
        fired_e = np.intersect1d(fired, self.pars['Exc_ids'])  # spiking e-neurons
        nPreSp_e = np.sum(self.__A[:, fired_e], axis=1) + external_e  # number of presynaptic e-spikes
        self.__ge += -self.pars['h'] * self.__ge/self.pars['tau_e'] + \
                     nPreSp_e * self.pars['s_e']

        # update conductances of inh. synapses
        external_i = np.random.poisson(self.pars['lambda_i'] * self.pars['h'])
        fired_i = np.intersect1d(fired, self.pars['Inh_ids'])  # spiking i-neurons
        nPreSp_i = np.sum(self.__A[:, fired_i], axis=1) + external_i  # number of presynaptic i-spikes
        self.__gi += -self.pars['h'] * self.__gi/self.pars['tau_i'] + \
                    nPreSp_i * self.pars['s_i']

        # update membrane and adaptation variable
        neuron_dynamics = -self.pars['gL']*(self.__v-self.pars['EL']) + \
              self.pars['gL']*self.pars['Delta']*np.exp((self.__v-self.pars['threshold'])/self.pars['Delta']) - \
              self.__w/self.pars['S']

        network_input = (-self.__ge*(self.__v-self.pars['Ee']) - self.__gi*(self.__v-self.pars['Ei']))/self.pars['S']

        self.__v += self.pars['h']*(neuron_dynamics + network_input)/self.pars['Cm'] + \
              self.pars['h']*self.pars['midi_external']/self.pars['Cm']

        self.__v[self.deadIDs] = self.pars['EL']  # clamp dead neurons to resting potential
        self.__w += self.pars['h'] * (self.__a * (self.__v - self.pars['EL']) -
                                      self.__w)/self.pars['tau_w']

        if not self.__recorder.done:
            self.__recorder.record(self.__v)


class ConfigParser:
    def __init__(self):
        self.input_config = {}
        self.output_config = {}
        self.__load_config()

    def __load_config(self):
        input_wiring = json.load(open('config/input_wiring.json', 'r'))
        for name, port in input_wiring.items():
            self.input_config[name] = {'midiport': port}

        outputs = json.load(open('config/outputs.json', 'r'))
        output_wiring = json.load(open('config/output_wiring.json', 'r'))
        for name, port in output_wiring.items():
            if name not in outputs:
                print("No config for device {} available, using default".format(name))
            else:
                self.output_config[name] = outputs[name]
                self.output_config[name]["midiport"] = port

    def get_outputs(self):
        return self.output_config

    def get_inputs(self):
        return self.input_config


class DeviceManager:
    def __init__(self, input_config, output_config, pars):
        self.spike_inputs = {}
        self.parameter_inputs = {}
        self.outputs = {}
        self.__create_inputs(input_config, pars)
        self.__create_outputs(output_config)

    def __create_inputs(self, input_config, pars):
        for name, settings in input_config.items():
            self.spike_inputs[name] = inputDevices.InputDevice(**settings)
            print("SETUP INPUT. Device `{}` connected to port `{}`".format(name, settings['midiport']))

        self.parameter_inputs[inputDevices.GuiAdapter.NAME] = inputDevices.GuiAdapter(pars)

    def __create_outputs(self, output_config):
        for name, settings in output_config.items():
            self.outputs[name] = outputDevices.OutputDevice(**settings)
            print("SETUP OUTPUT. Device `{}` connected to port `{}`".format(name, settings['midiport']))

    def get_spike_inputs(self):
        return list(self.spike_inputs.values())

    def get_parameter_inputs(self):
        return list(self.parameter_inputs.values())


class MainApp:
    def __init__(self, deviceManager, pars):
        self.__fullscreen = False

        self.pars = pars
        # self.keyboardInput = deviceManager.spike_inputs['KeyboardInput']

        inputHandler = InputHandler(
            spike_inputs=deviceManager.get_spike_inputs(),
            parameter_inputs=deviceManager.get_parameter_inputs(),
            pars=pars
        )
        outputHandler = OutputHandler(deviceManager.outputs, pars, display=outputDevices.DisplayAdapter())

        print("wiring....")
        connectivity_matrix = ConnectivityMatrix().get()
        print('wiring completed')

        self.network = SensoryNetwork(inputHandler, outputHandler, pars, connectivity_matrix)

    async def run(self):
        last_updated = time.time()
        while True:
            if time.time()-last_updated < self.pars['pause']:
                pass
            else:
                self.network.update()
                last_updated = time.time()

            await asyncio.sleep(0.001)


async def init_main():
    pars = parameters()
    for i, value in enumerate(sys.argv):
        if value == '-w':
            pars['screen_size'][0] = int(sys.argv[i+1])
        if value == '-h':
            pars['screen_size'][1] = int(sys.argv[i+1])

    parser = ConfigParser()
    dm = DeviceManager(parser.get_inputs(), parser.get_outputs(), pars)
    app = MainApp(dm, pars)

    dispatcher = Dispatcher()
    dispatcher.map(GUI_PAR_ADDRESS, dm.parameter_inputs[inputDevices.GuiAdapter.NAME].on_par_receive)
    dispatcher.map(GUI_SPIKE_ADDRESS, dm.parameter_inputs[inputDevices.GuiAdapter.NAME].on_spike_receive)

    server = AsyncIOOSCUDPServer((IP, GUI_PORT), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving

    if app.network is not None:
        await app.run()  # Enter main loop of program

        transport.close()  # Clean up serve endpoint
    else:
        print('Network setup failed')


if __name__ == '__main__':
    asyncio.run(init_main())
