from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import numpy as np
import pickle

from config.osc import IP, RECORDING_PORT, RECORDING_ADDRESS


class Recorder:
    def __init__(self, n):
        self.__k = 0
        self.__nIter = 500
        self.__vRec = np.zeros((n, self.__nIter))

    def record(self, v):
        self.__vRec[:, self.__k] = v
        self.__k += 1

        if self.__k >= self.__nIter:
            self.__write()
            self.__k = 0

    def __write(self):
        print('--------- WRITING WRITING --------------')
        with open('display/v_rec.pkl', 'wb') as f:
            pickle.dump(self.__vRec, f)


class RecordingServer:
    def __init__(self, recorder):
        self.recorder = recorder
        dispatcher = Dispatcher()
        dispatcher.map(RECORDING_ADDRESS, self.record)
        self.server = ThreadingOSCUDPServer((IP, RECORDING_PORT), dispatcher)

    def record(self, _, *data):
        self.recorder.record(data)


if __name__ == '__main__':
    n_display = 500
    rec = Recorder(n_display)
    server = RecordingServer(rec)
    server.server.serve_forever()
