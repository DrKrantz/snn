import socket
import struct

MESSAGETYPE_ERROR = -1
MESSAGETYPE_PERFORMANCE = 0
MESSAGETYPE_INIT = 1

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
        self.__neuron_ids = []
        super(SpikeForwarder, self).__init__(socket.AF_INET, socket.SOCK_DGRAM, *args, **kwargs)

    def register_target(self, target):
        self.targets.append(target)

    def start_init(self):
        self.bind(self.receiving_address)
        while True:
            data, addr = self.recvfrom(MESSAGESIZE_INIT)
            if data:
                msg_type, index, number = struct.unpack('<bHf', data)
                print('received type {} with index {} and number {}'.format(msg_type, index, number))
                if number == 0.0:
                    self.n_neurons = index
                else:
                    self.__neuron_ids.append(int(number))
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

    def send_init(self, data):
        self.sendto(struct.pack('<bHf', MESSAGETYPE_INIT, len(data), 0.0), self.target_address)
        for idx, field in enumerate(data):
            self.sendto(struct.pack('<bHf', MESSAGETYPE_INIT, idx, field), self.target_address)
