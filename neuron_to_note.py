import numpy as np


SCALE_MAJOR = np.array([0, 2, 4, 5, 7, 9, 11])
SCALE_MINOR = np.array([0, 2, 3, 5, 7, 8, 10])


def multiply_scale(scale, n_octaves=12):
    big_scale = []
    [big_scale.append(scale + k * 12) for k in range(n_octaves)]
    return np.array(big_scale).flatten()


class Neuron2NoteConverter:

    def __init__(self, note_range, scale):
        self._note_range = note_range
        self._scale = self._extend_scale(scale)

    def convert(self, neuron_ids):
        return self._scale[np.mod(np.array(neuron_ids), len(self._scale)).astype('int')]

    def _extend_scale(self, scale):
        return np.intersect1d(self._note_range, multiply_scale(scale))


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


if __name__ == '__main__':
    converter = Neuron2NoteConverter(np.arange(1, 96), SCALE_MAJOR)
    print(converter.convert([1, 2, 3]))
