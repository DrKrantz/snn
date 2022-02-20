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
import time
import sys
import asyncio
import pickle
import numpy as np

from Dunkel_pars import parameters
from config.osc import IP, GUI_PORT, RECORDING_PORT, RECORDING_ADDRESS, \
    GUI_PAR_ADDRESS, GUI_SPIKE_ADDRESS, GUI_RESET_ADDRESS, GUI_OUTPUT_SETTINGS_ADDRESS, GUI_START_ADDRESS,\
    GUI_STOP_ADDRESS
from outputHandler import OutputHandler
from inputHandler import InputHandler
import outputDevices
import inputDevices
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient
from networks.cortex import Network


class SensoryNetwork(object):
    def __init__(self, inputHandler, outputHandler, pars, network_model, client=None):
        super(SensoryNetwork, self).__init__()
        self.inputHandler = inputHandler
        self.outputHandler = outputHandler
        self.pars = pars
        self.model = network_model
        self.__client = client
        self.__A = self.model.A

        self.reset()
        
    def update(self):
        #  UPDATE VIEWER & INPUTS ###########
        self.inputHandler.update()
        self.pars.update(self.inputHandler.getPars())

        ext_fired_ids = self.inputHandler.getFired()
        fired_ids = np.array(np.union1d(self.__fired_ids, ext_fired_ids), int)

        # update conductances of inh. synapses
        external_i = np.random.poisson(self.pars['lambda_i'] * self.pars['h'])
        fired_i = np.intersect1d(fired_ids, self.model.inh_ids)  # spiking i-neurons
        nPreSp_i = np.sum(self.__A[:, fired_i], axis=1) + external_i  # number of presynaptic i-spikes
        self.__gi += -self.pars['h'] * self.__gi/self.pars['tau_i'] + nPreSp_i * self.pars['s_i']

        # update conductances of excitatory synapses
        external_e = np.random.poisson(self.pars['lambda_e'] * self.pars['h'])
        fired_e = np.intersect1d(fired_ids, self.model.exc_ids)  # spiking e-neurons
        nPreSp_e = np.sum(self.__A[:, fired_e], axis=1) + external_e  # number of presynaptic e-spikes

        if self.__T < self.pars['stimdur']:
            extstim = np.zeros(self.model.N)
            ext_spikes = np.random.poisson(self.pars['stimrate'] * self.pars['h'], len(self.__stim_ids))
            extstim[self.__stim_ids] = ext_spikes
            nPreSp_e += extstim
            print("T = ", self.__T)
        elif self.__T <= self.pars['stimdur']+self.pars['h']:
            print('Stimulation Over!!!')
        self.__ge += -self.pars['h'] * self.__ge/self.pars['tau_e'] + nPreSp_e * self.pars['s_e']

        # update membrane and get fired IDs
        neuron_dynamics = -self.pars['gL']*(self.__v-self.pars['EL']) + \
              self.pars['gL']*self.pars['Delta']*np.exp((self.__v-self.pars['threshold'])/self.pars['Delta']) - \
              self.__w/self.pars['S']
        network_input = (-self.__ge*(self.__v-self.pars['Ee']) - self.__gi*(self.__v-self.pars['Ei']))/self.pars['S']
        self.__v += self.pars['h']*(neuron_dynamics + network_input + self.pars['midi_external'])/self.pars['Cm']

        self.__v[self.deaddur > 0] = self.pars['EL']  # clamp dead neurons to resting potential
        fired_ids, = np.nonzero(self.__v > self.pars['threshold'])
        self.__v[fired_ids] = self.pars['EL']  # clamp fired neurons to resting potential

        # UPDATE DEADIMES  ###########
        self.deaddur[self.deaddur > 0] += self.pars['h']  # increment deaddur
        self.deaddur[self.deaddur > self.pars['dead']] = 0  # reanimate newly the living
        self.deaddur[fired_ids] = self.pars['h']/10  # set deaddur of the fired neurons != 0

        # Update adaptation variable
        self.__w += self.pars['h'] * (self.model.a * (self.__v - self.pars['EL']) - self.__w)/self.pars['tau_w']
        self.__w[fired_ids] += self.model.b[fired_ids]  # increment adaptation variable of fired neurons

        self.__fired_ids = fired_ids  # store fired neurons for synaptic input in next iteration

        # SEND TO HANDLER ###
        self.outputHandler.turn_off()
        self.outputHandler.update_external(ext_fired_ids)
        self.outputHandler.update(np.array(np.union1d(self.__fired_ids, ext_fired_ids), int))

        if self.__client is not None:
            n_rec = 200
            rec_data = {'v': self.__v[0:n_rec],
                        'g_e': self.__ge[0:n_rec],
                        'g_i': self.__gi[0:n_rec],
                        'w': self.__w[0:n_rec]}
            pkl = pickle.dumps(rec_data)
            try:
                self.__client.send_message(RECORDING_ADDRESS, pkl)
            except OverflowError:
                print('Not recording, float too large to pack!')

        self.__T += self.pars['h']

    def reset(self):
        n = self.model.N
        self.__fired_ids = np.array([])
        self.__ge = self.pars['s_e']*np.ones(n)  # conductances of excitatory synapses
        self.__gi = self.pars['s_i']*np.ones(n)  # conductances of inhibitory synapses
        self.__v = self.pars['EL']*np.ones(n)  # Initial values of the mmbrane potential v
        self.__w = np.ndarray.copy(self.model.b)  # Initial values of adaptation variable w
        # self.__neurons = np.array([])   # neuron IDs
        # self.__hasPrinted = False
        self.deaddur = np.zeros(n)  # duration (secs) the dead neurons have been dead (is 0 for aluve neurons)
        self.__T = 0
        self.__stim_ids = np.random.choice(np.arange(n), int(self.pars['p_stim']*n), False)  # stimulated neurons


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

    def update_output_settings(self, _, device_name, max_num_signals, update_interval, synchrony_limit):
        print("Setting", device_name, max_num_signals, update_interval, synchrony_limit)
        if device_name in self.outputs:
            self.outputs[device_name].set_vars(max_num_signals, update_interval, synchrony_limit)

    def get_spike_inputs(self):
        return list(self.spike_inputs.values())

    def get_parameter_inputs(self):
        return list(self.parameter_inputs.values())


class MainApp:
    def __init__(self, deviceManager, pars):
        self.pars = pars
        self.__is_running = False
        print("wiring....")
        network_model = Network()
        print('wiring completed')

        # self.keyboardInput = deviceManager.spike_inputs['KeyboardInput']

        inputHandler = InputHandler(
            spike_inputs=deviceManager.get_spike_inputs(),
            parameter_inputs=deviceManager.get_parameter_inputs(),
            exc_ids=network_model.exc_ids,
            pars=pars
        )
        outputHandler = OutputHandler(deviceManager.outputs, pars, display=outputDevices.DisplayAdapter())
        client = SimpleUDPClient(IP, RECORDING_PORT)

        self.network = SensoryNetwork(inputHandler, outputHandler, pars, network_model, client=client)

    async def run(self):
        last_updated = time.time()
        self.__is_running = True
        while True:
            if self.__is_running:
                if time.time()-last_updated < self.pars['pause']:
                    pass
                else:
                    self.network.update()
                    last_updated = time.time()
                await asyncio.sleep(0.00001)
            else:
                await asyncio.sleep(1)
                print("pausing")

    def stop(self, *_):
        self.network.reset()
        self.__is_running = False

    def pause(self):
        self.__is_running = False

    def start(self, *_):
        self.__is_running = True


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
    dispatcher.map(GUI_OUTPUT_SETTINGS_ADDRESS, dm.update_output_settings)
    dispatcher.map(GUI_START_ADDRESS, app.start)
    dispatcher.map(GUI_STOP_ADDRESS, app.stop)
    dispatcher.map(GUI_RESET_ADDRESS, dm.parameter_inputs[inputDevices.GuiAdapter.NAME].on_reset)

    server = AsyncIOOSCUDPServer((IP, GUI_PORT), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving

    if app.network is not None:
        await app.run()  # Enter main loop of program

        transport.close()  # Clean up serve endpoint
    else:
        print('Network setup failed')


if __name__ == '__main__':
    asyncio.run(init_main())
