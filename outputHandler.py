
from numpy import intersect1d
import time
global pars


class OutputHandler(object):
    def __init__(self, outputs, pars, neuron2NoteConversion=4, display=None):
        self.pars = pars
        super(OutputHandler, self).__init__()

        self.display = display

        self.__output_external = None
        if "external" in outputs:
            self.__output_external = outputs.pop('external')
        self.__output = outputs

        self.__now = time.time()
        self.__activeNotes = set()
        self.__neuron2NoteConversion = neuron2NoteConversion

    def update(self, fired):
        neuron_ids = intersect1d(fired, self.pars['note_ids'])

        if len(neuron_ids) > 0:
            print('OutputHandler: fired: ', neuron_ids)
            self.__checkKeyChange(neuron_ids)

            for neuron_id in neuron_ids:
                for name, output in self.__output.items():
                    output.note_on(neuron_id)

        if self.display:
            # display spikes and update display
            self.display.update(fired)

    def update_external(self, fired):
        if self.__output_external is not None:
            neuron_ids = intersect1d(fired, self.pars['note_ids'])

            if len(neuron_ids) > 0:
                print('OutputHandler: input: ', neuron_ids)
                for neuron_id in neuron_ids:
                    self.__output_external.note_on(neuron_id)

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
