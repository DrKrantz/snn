import numpy as np
import os
import json


def linear2grid(nid, n_col):
    """
    neuron 0 will be in the bottom left corner with coordintates (0,0), neuron 1 is (1,0)
    the equation is N_col*row_id+col_id = Nid
    :param nid:
    :param n:
    :param n_col:
    :return:
    """
    col_id = np.mod(nid, n_col)
    row_id = np.ceil((nid - col_id) / n_col)
    return int(col_id), int(row_id)


class Linear2GridConverter:
    def __init__(self, n=400, n_col=20):
        self.__data = {}
        for nid in range(n):
            self.__data[nid] = linear2grid(nid, n_col)
        self.__write(n, n_col)

    def __write(self, n, n_col):
        filename = "linear2grid_{}_{}.json".format(n, n_col)
        # print(self.__data)
        with open(os.path.join('../data', filename), 'w') as fp:
            json.dump(self.__data, fp)


if __name__ == '__main__':
    converter = Linear2GridConverter()
