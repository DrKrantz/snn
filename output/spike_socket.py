import socket
import struct


class SpikeSocket(socket.socket):
    def __init__(self, target_address, *args, **kwargs):
        self.target_address = target_address
        super(SpikeSocket, self).__init__(socket.AF_INET, socket.SOCK_DGRAM, *args, **kwargs)

    def send_neuron(self, neuron_id):
        self.sendto(struct.pack('i', neuron_id), self.target_address)


class SpikeForwarder(SpikeSocket):
    SIZE = 4

    def start_forwarding(self, receiving_address, id_to_index):
        self.bind(receiving_address)

        while True:
            data, addr = self.recvfrom(SpikeForwarder.SIZE)
            if data:
                [neuron_id] = struct.unpack('i', data)
                index = id_to_index(neuron_id)
                print('received id {} and converted to index {}'.format(neuron_id, index))
                self.send_neuron(index)


class InitSocket(socket.socket):
    def __init__(self, target_address, *args, **kwargs):
        self.target_address = target_address
        super(InitSocket, self).__init__(socket.AF_INET, socket.SOCK_DGRAM, *args, **kwargs)

    def send_init(self, frequencies):
        self.sendto(struct.pack('id', len(frequencies), 0.0), self.target_address)
        for idx, freq in enumerate(frequencies):
            self.sendto(struct.pack('id', idx, freq), self.target_address)
