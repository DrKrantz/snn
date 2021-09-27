# import pygame.font
from numpy import intersect1d
# import pygame.midi as pm

from display import Display
from outputDevices import *
global pars


class OutputHandler(object):
    def __init__(self, outputs, pars, neuron2NoteConversion=4, display=False):
        self.pars = pars
        super(OutputHandler, self).__init__()

        self.display = display
        if self.display:
            self.display = Display(pars['N_col'], pars['N_row'],
                                   ['Ne', 'Ni', 's_e', 's_i', 'tau_e', 'tau_i', 'midi_ext_e', 'midi_ext_i',
                                    'cam_ext', 'cam_external_max'], 'lines', screenSize=pars['screen_size'])
        self.__output = outputs
        self.__input = {}

        self.__now = time.time()
        self.__activeNotes = set()
        self.__neuron2NoteConversion = neuron2NoteConversion

    def update(self, fired):
        neuron_ids = intersect1d(fired, self.pars['note_ids'])
        n_fired = len(neuron_ids)

        if n_fired > 0:
            print('OutputHandler: fired: ', neuron_ids)
            self.__checkKeyChange(neuron_ids)
            
            for neuron_id in neuron_ids:
                for name, output in self.__output.items():
                    output.note_on(neuron_id)

        if self.display:
            # display spikes and update display
            self.display.update_fired(fired)
            self.display.update_pars(
                ['cam_ext', 'midi_ext_e', 'midi_ext_i', 's_e', 's_i',
                 'tau_e', 'tau_i', 'cam_external_max'])
            pygame.display.update()

    def turn_off(self):
        for name in self.__output.keys():
            if name == "neuron_notes":
                self.__output[name].turn_all_off()

    def __checkKeyChange(self, neuron_ids):
        if len(neuron_ids) > 20:
            self.__neuron2NoteConversion = (1 if self.__neuron2NoteConversion == 7 else 7)
            self.__output["neuron_notes"].setNeuron2NoteConversion(
                self.__neuron2NoteConversion
            )
            # [output.setNeuron2NoteConversion(self.__neuron2NoteConversion) for
            #             name, output in self.__output.iteritems()]

            print('----------------------------------------key change')
