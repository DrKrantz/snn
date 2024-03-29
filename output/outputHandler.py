
from numpy import intersect1d
import time
global pars


class OutputHandler(object):
    def __init__(self, outputs, pars, neuron2NoteConversion=7, display=None):
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
        neuron_ids = self.__filter_fired(fired)

        if len(neuron_ids) > 0:
            # print('OutputHandler: fired: ', neuron_ids)
            self.__checkKeyChange(neuron_ids)
            for output in self.__output.values():
                output.update(neuron_ids)

        if self.display:
            # display spikes and update display
            self.display.update(fired)

    def update_external(self, fired):
        if self.__output_external is not None:
            neuron_ids = self.__filter_fired(fired)

            if len(neuron_ids) > 0:
                print('OutputHandler: input: ', neuron_ids)
                for neuron_id in neuron_ids:
                    self.__output_external.note_on(neuron_id)

    def initialize_visuals(self):
        if "visuals" in self.__output:
            self.__output["visuals"].note_on(70, overwrite_conversion=True)

    def turn_off(self):
        for name in self.__output.keys():
            if name == "neuron_notes":
                self.__output[name].turn_all_off()

    def __checkKeyChange(self, neuron_ids):
        if len(neuron_ids) > self.pars['N_concious']:
            self.__neuron2NoteConversion = (6 if self.__neuron2NoteConversion == 2 else 2)
            self.__output["neuron_notes"].setNeuron2NoteConversion(
                self.__neuron2NoteConversion
            )
            # [output.setNeuron2NoteConversion(self.__neuron2NoteConversion) for
            #             name, output in self.__output.iteritems()]

            print('----------------------------------------key change')

    @staticmethod
    def __filter_fired(fired):
        """
        build filter to play only specific neuron IDs
        :param fired:
        :return:
        """
        return fired  #  intersect1d(fired, self.pars['note_ids']
