import socket
import struct


class SpikeSocket(socket.socket):
    def __init__(self, target_address, convert=None, *args, **kwargs):
        self.target_address = target_address
        if convert is None:
            self.convert = lambda x: x
        else:
            self.convert = convert

        super(SpikeSocket, self).__init__(socket.AF_INET, socket.SOCK_DGRAM, *args, **kwargs)

    def send_converted(self, neuron_id):
        self.sendto(struct.pack('i', self.convert(neuron_id)), self.target_address)


class SpikeForwarder(socket.socket):
    SIZE = 4

    def __init__(self, receiving_address, *args, **kwargs):
        self.receiving_address = receiving_address
        self.targets = []
        super(SpikeForwarder, self).__init__(socket.AF_INET, socket.SOCK_DGRAM, *args, **kwargs)

    def register_target(self, target):
        self.targets.append(target)

    def start_forwarding(self):
        self.bind(self.receiving_address)

        while True:
            data, addr = self.recvfrom(SpikeForwarder.SIZE)
            if data:
                [neuron_id] = struct.unpack('i', data)
                print('received id {}'.format(neuron_id))
                [target.send_converted(neuron_id) for target in self.targets]


class InitSocket(socket.socket):
    def __init__(self, target_address, *args, **kwargs):
        self.target_address = target_address
        super(InitSocket, self).__init__(socket.AF_INET, socket.SOCK_DGRAM, *args, **kwargs)

    def send_init(self, frequencies):
        self.sendto(struct.pack('id', len(frequencies), 0.0), self.target_address)
        for idx, freq in enumerate(frequencies):
            self.sendto(struct.pack('id', idx, freq), self.target_address)
