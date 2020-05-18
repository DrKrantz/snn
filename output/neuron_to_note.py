import numpy as np


SCALE_MAJOR = np.array([0, 2, 4, 5, 7, 9, 11])
SCALE_MINOR = np.array([0, 2, 3, 5, 7, 8, 10])


def multiply_scale(scale, n_octaves=12):
    big_scale = []
    [big_scale.append(scale + k * 12) for k in range(n_octaves)]
    return np.array(big_scale).flatten()


class Neuron2NoteConverter:
    def __init__(self, all_neuron_ids, scale):
        self._all_neuron_ids = all_neuron_ids
        self.midi_notes = self._extend_scale(scale)

    def convert(self, neuron_ids):
        return self.midi_notes[np.mod(np.array(neuron_ids), len(self.midi_notes)).astype('int')]

    def _extend_scale(self, scale):
        return np.intersect1d(self._all_neuron_ids, multiply_scale(scale))


class LinearConverter:
    def __init__(self, offset=0):
        self.__offset = offset

    def convert(self, neuron_ids):
        return [neuron_id + self.__offset for neuron_id in neuron_ids]


class TogglingConverter(Neuron2NoteConverter):
    TOGGLE_COUNT = 20
    _current_scale_id = 0

    def __init__(self, note_range, scale1, scale2):
        super(TogglingConverter, self).__init__(note_range, scale1)
        self._scales = [self._scale, self._extend_scale(scale2)]

    def convert(self, neuron_ids):
        if len(neuron_ids) >= self.TOGGLE_COUNT:
            self._current_scale_id = (self._current_scale_id + 1) % 2
            self._scale = self._scales[self._current_scale_id]
            print("TogglingConverter: scale switched")
        return self._scale[np.mod(np.array(neuron_ids), len(self._scale)).astype('int')]


def note_to_freq(notes):
    notes = np.array(notes)
    a = 440  # frequency of A (common value is 440Hz)
    return (a / 32) * (2 ** ((notes - 9) / 12))


class Neuron2FrequencyConverter(Neuron2NoteConverter):
    def __init__(self, all_neuron_ids, scale):
        super(Neuron2FrequencyConverter, self).__init__(all_neuron_ids, scale)
        self.all_notes = self.convert(self._all_neuron_ids)
        self.frequencies = self.note_to_freq(self.all_notes)

    @staticmethod
    def note_to_freq(notes):
        a = 440  # frequency of A (common value is 440Hz)
        return (a / 32) * (2 ** ((notes - 9) / 12))


def get_frequencies_for_group(name):
    if name == 'excitatory':
        start = 440
        end = 2 * start
        return np.linspace(start, end, 50)
    elif name == 'inhibitory':
        start = 880
        end = 2 * start
        return np.linspace(start, end, 50)


def get_frequencies_for_range(start, stop, n):
    return np.linspace(start, stop, n)


if __name__ == '__main__':
    converter = Neuron2NoteConverter(np.arange(1, 96), SCALE_MAJOR)
    print(converter.convert([1, 2, 3]))
