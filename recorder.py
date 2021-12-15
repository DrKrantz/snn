from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import numpy as np
import pickle

from config.osc import IP, RECORDING_PORT, RECORDING_ADDRESS


class Recorder:
    def __init__(self):
        self.__k = 0
        self.__nIter = 500
        self.__reset(0)

    def record(self, pkl):
        data = pickle.loads(pkl)
        if len(self.__vRec) == 0:
            self.__reset(len(data['v']))
        self.__vRec[:, self.__k] = data['v']
        self.__ge[:, self.__k] = data['g_e']
        self.__gi[:, self.__k] = data['g_i']
        self.__w[:, self.__k] = data['w']
        self.__k += 1

        if self.__k >= self.__nIter:
            self.__write()
            self.__k = 0
            self.__reset(len(data['v']))

    def __write(self):
        print('--------- WRITING WRITING --------------')
        with open('data/v_rec.pkl', 'wb') as f:
            pickle.dump({
                'v': self.__vRec,
                'g_e': self.__ge,
                'g_i': self.__gi,
                'w': self.__w},
                f)

    def __reset(self, n):
        self.__vRec = np.zeros((n, self.__nIter))
        self.__ge = np.zeros((n, self.__nIter))
        self.__gi = np.zeros((n, self.__nIter))
        self.__w = np.zeros((n, self.__nIter))


class RecordingServer:
    def __init__(self, recorder):
        self.recorder = recorder
        dispatcher = Dispatcher()
        dispatcher.map(RECORDING_ADDRESS, self.record)
        self.server = ThreadingOSCUDPServer((IP, RECORDING_PORT), dispatcher)

    def record(self, _, pkl):
        self.recorder.record(pkl)


if __name__ == '__main__':
    rec = Recorder()
    server = RecordingServer(rec)
    server.server.serve_forever()
