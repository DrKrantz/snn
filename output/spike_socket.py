import socket


class SpikeSocket(socket.socket):
    def __init__(self, address, *args, **kwargs):
        self.target_address = address

        super(SpikeSocket, self).__init__(socket.AF_INET, socket.SOCK_DGRAM, *args, **kwargs)

    def send_neuron(self, neuron_id):
        self.sendto(bytes(str(neuron_id), encoding='utf8'), self.target_address)


class SpikeForwarder(SpikeSocket):
    SIZE = 1024

    def start_forwarding(self, receiving_address):
        self.bind(receiving_address)
        while True:
            data, addr = self.recvfrom(SpikeForwarder.SIZE)  # buffer size is 1024 bytes
            if data:
                print('received: %s' % data)
                # TODO: translate neuron_ID to idx and forward to instrument
