import socket
import struct


class SpikeSocket(socket.socket):
    def __init__(self, address, *args, **kwargs):
        self.target_address = address
        super(SpikeSocket, self).__init__(socket.AF_INET, socket.SOCK_DGRAM, *args, **kwargs)

    def send_neuron(self, neuron_id):
        self.sendto(struct.pack('i', neuron_id), self.target_address)


class SpikeForwarder(SpikeSocket):
    SIZE = 4

    def start_forwarding(self, receiving_address):
        self.bind(receiving_address)

        while True:
            data, addr = self.recvfrom(SpikeForwarder.SIZE)
            if data:
                neuron_id = struct.unpack('i', data)
                print('received id: %s' % neuron_id)
                # TODO: translate neuron_ID to idx and forward to instrument


class InitSocket(socket.socket):
    def __init__(self, address, *args, **kwargs):
        self.target_address = address
        super(InitSocket, self).__init__(socket.AF_INET, socket.SOCK_DGRAM, *args, **kwargs)

    def send_init(self, frequencies):
        self.sendto(struct.pack('id', len(frequencies), 0.0), self.target_address)
        for idx, freq in enumerate(frequencies):
            self.sendto(struct.pack('id', idx, freq), self.target_address)
