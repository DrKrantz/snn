import pygame.font
from numpy import intersect1d
from pythonosc.udp_client import SimpleUDPClient

from display import Display
from outputDevices import *
global pars

ADDRESS_SOUND = "/sound"
IP = "127.0.0.1"
PORT = 1337


class OutputHandler(object):
    def __init__(self, outputs, pars, neuron2NoteConversion=4):
        super(OutputHandler, self).__init__()
        self.__output = outputs
        self.pars = pars
        self.__neuron2NoteConversion = neuron2NoteConversion

        self.display = Display(pars['N_col'], pars['N_row'],
                               ['Ne', 'Ni', 's_e', 's_i', 'tau_e', 'tau_i', 'midi_ext_e', 'midi_ext_i',
                                'cam_ext', 'cam_external_max'], 'lines', screenSize=pars['screen_size'])

        self.__client = SimpleUDPClient(IP, PORT)
        pm.init()

        if Visuals.NAME in self.__output:  # TODO: why is this here?
            self.__output[Visuals.NAME].note_on(1)

        self.__now = time.time()
        self.__activeNotes = set()

    def update(self, fired):
        neuron_ids = intersect1d(fired, self.pars['note_ids'])

        # self.__checkKeyChange(neuron_ids)

        if len(neuron_ids) > 0:
            ids = [int(i) for i in neuron_ids]  # TODO: I'm sure there's a smarter way to fix this
            self.__client.send_message(ADDRESS_SOUND, ids)
                
        # display spikes and update display
        self.display.update_fired(fired)
        self.display.update_pars(
            ['cam_ext', 'midi_ext_e', 'midi_ext_i', 's_e', 's_i',
             'tau_e', 'tau_i', 'cam_external_max'])
        pygame.display.update()

    def turnOff(self):
        for outputName in self.__output.keys():
            if outputName == NeuronNotes.NAME:
                self.__output[outputName].turnAllOff()

    def __checkKeyChange(self, neuron_ids):
        if len(neuron_ids) > 20:
            print(self.__output)
            self.__neuron2NoteConversion = (1 if self.__neuron2NoteConversion == 7 else 7)
            self.__output[NeuronNotes.NAME].setNeuron2NoteConversion(
                self.__neuron2NoteConversion
            )
            # [output.setNeuron2NoteConversion(self.__neuron2NoteConversion) for
            #             name, output in self.__output.iteritems()]

            print('----------------------------------------key change')
