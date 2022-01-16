import numpy as np


scales = {
    'major': np.array([0, 2, 4, 5, 7, 9, 11]),
    'minor': np.array([0, 2, 3, 5, 7, 8, 10])
}


class Converter:
    def __init__(self, note_list: list):
        self.__note_list = note_list

    def convert(self, neuron_id):
        return self.__note_list[int(np.mod(neuron_id, len(self.__note_list)))]


def complete_scale(base_list, min_note=1, max_note=127, offset=0):
    b = []
    [b.append(base_list + offset + k * 12) for k in range(11)]
    b = np.array(b).flatten()
    return b[np.multiply(b >= min_note, b <= max_note)]


class Neuron2NoteConverter(object):
    def __init__(self, conversion=1, min_note=1, max_note=127):
        self.__conversion = conversion

        self.__converter = {
            1: Converter(list(range(min_note, max_note+1))),
            4: Converter(complete_scale(scales['major'], min_note, max_note)),
            5: Converter(complete_scale(scales['minor'], min_note, max_note)),
            6: Converter(complete_scale(scales['major'], min_note, max_note)),
            7: Converter(complete_scale(scales['major'], min_note, max_note, offset=1)),
            8: Converter(get_direct_visuals()),
            9: Converter(get_direct_audio()),
        }

    def convert(self, neuron_id):
        return self.__converter[self.__conversion].convert(neuron_id)


def get_direct_visuals():
    qlist = list(range(42, 59))
    [qlist.append(idx) for idx in range(64, 82)]
    [qlist.append(idx) for idx in range(96, 112)]
    return qlist


def get_direct_audio():
    return list(range(82, 128))