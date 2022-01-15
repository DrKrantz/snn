
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
            print('OutputHandler: fired: ', neuron_ids)

            if len(neuron_ids) > self.pars['N_concious']:
                neuron_2_note = (6 if self.__neuron2NoteConversion == 7 else 7)
                self.set_note_conversion(neuron_2_note)
            [output.update(neuron_ids) for output in self.__output.values()]

        if self.display:
            # display spikes and update display
            self.display.update(fired)

    def set_note_conversion(self, neuron_2_note):
        print('----------------------------------------key change')
        self.__neuron2NoteConversion = neuron_2_note
        self.__output["neuron_notes"].setNeuron2NoteConversion(
            self.__neuron2NoteConversion
        )

    def update_external(self, fired):
        if self.__output_external is not None:
            neuron_ids = self.__filter_fired(fired)

            if len(neuron_ids) > 0:
                print('OutputHandler: input: ', neuron_ids)
                for neuron_id in neuron_ids:
                    self.__output_external.note_on(neuron_id)

    def turn_off(self):
        if "neuron_notes" in self.__output:
            self.__output["neuron_notes"].turn_all_off()

    @staticmethod
    def __filter_fired(fired):
        """
        build filter to play only specific neuron IDs
        :param fired:
        :return:
        """
        return fired  #  intersect1d(fired, self.pars['note_ids']
