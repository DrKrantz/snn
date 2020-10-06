import socket
import struct
from subprocess import Popen, PIPE

import numpy as np
import time

MESSAGETYPE_ERROR = -1
MESSAGETYPE_PERFORMANCE = 0
MESSAGETYPE_INIT = 1
MESSAGETYPE_INIT_CONTENT = 2

MESSAGESIZE_PERFORMANCE = 4
MESSAGESIZE_INIT = 7


class SpikeSocket(socket.socket):
    def __init__(self, target_address, convert=None, *args, **kwargs):
        self.target_address = target_address
        if convert is None:
            self.convert = lambda x: x
        else:
            self.convert = convert

        super(SpikeSocket, self).__init__(socket.AF_INET, socket.SOCK_DGRAM, *args, **kwargs)

    def send_converted(self, neuron_id):
        self.sendto(struct.pack('<bH', MESSAGETYPE_PERFORMANCE, self.convert(neuron_id)), self.target_address)


class SpikeForwarder(socket.socket):
    POPULATION_SIZE = 100

    def __init__(self, receiving_address, *args, **kwargs):
        self.receiving_address = receiving_address
        self.targets = []
        self.n_neurons = 0
        self.__neuron_ids = set()
        super(SpikeForwarder, self).__init__(socket.AF_INET, socket.SOCK_DGRAM, *args, **kwargs)

    def register_target(self, target):
        self.targets.append(target)

    def start_init(self):
        self.bind(self.receiving_address)
        while True:
            data, addr = self.recvfrom(MESSAGESIZE_INIT)
            if data:
                msg_type, index, number = struct.unpack('<bHf', data)
                # print('received type {} with index {} and number {}'.format(msg_type, index, number))
                if number == 0.0:
                    self.n_neurons = index
                    self.__neuron_ids = set()
                else:
                    self.__neuron_ids.add(int(number))
                    if self.n_neurons != 0 and len(self.__neuron_ids) == self.n_neurons:
                        print('Forwarder initialization complete!')
                        return True

    def start_forwarding(self):
        while True:
            data, addr = self.recvfrom(MESSAGESIZE_PERFORMANCE)
            if data:
                msg_type, neuron_id = self.__validate_performance_msg(data)
                if msg_type == MESSAGETYPE_ERROR:
                    print('Unknown neuron_id {}'.format(neuron_id))
                else:
                    print('received id {}'.format(neuron_id))
                    [target.send_converted(neuron_id) for target in self.targets]

    def __validate_performance_msg(self, data):
        msg_type, neuron_id = struct.unpack('<bH', data)
        if neuron_id not in self.__neuron_ids:
            msg_type = MESSAGETYPE_ERROR
        return msg_type, neuron_id


class InitSocket(socket.socket):
    def __init__(self, target_address, *args, **kwargs):
        self.target_address = target_address
        super(InitSocket, self).__init__(socket.AF_INET, socket.SOCK_DGRAM, *args, **kwargs)

    def send_long_init(self, data):
        n_data = len(data)
        package_size = 1000.

        print('Sending init to: ', self.target_address)
        self.sendto(
            struct.pack('<bHH', MESSAGETYPE_INIT, n_data, int(package_size)),
            self.target_address)

        n_chunks = int(np.ceil(n_data / package_size))
        padded_data = np.pad(data, (0, n_data-int(n_chunks * package_size)), mode='constant', constant_values=0)
        chunks = np.split(padded_data, n_chunks)
        for idx, chunk in enumerate(chunks):
            print('sending chunk {}/{}'.format(idx+1, n_chunks))
            # print(chunk)
            self.sendto(
                struct.pack('<b', MESSAGETYPE_INIT_CONTENT) + np.array(chunk).astype('f').tobytes(),
                self.target_address)
            time.sleep(1)

    def send_short_init(self, data):
        self.sendto(struct.pack('<bHf', MESSAGETYPE_INIT, len(data), 0.0), self.target_address)
        for idx, field in enumerate(data):
            self.sendto(struct.pack('<bHf', MESSAGETYPE_INIT, idx, field), self.target_address)


class ScreenParser:
    def __init__(self, cmd, send_cb):
        self.recorder = Popen(cmd, stdout=PIPE)
        self.__send_cb = send_cb

    def run(self):
        while True:
            out = self.recorder.stdout.readline()
            if out:
                self.__send_cb(out.decode())
