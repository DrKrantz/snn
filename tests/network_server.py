import pickle
from subprocess import Popen, PIPE

from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


ROUTE = '/test'
RECEIVER_ADDRESS = ('localhost', 5001)
NETWORK_ADDRESS = ('localhost', 5000)
START_SIMULATION = '/start'
RECORDED_NEURONS = '/neurons'


class TestServer(BlockingOSCUDPServer):
    def __init__(self, address):
        dispatcher = Dispatcher()
        dispatcher.set_default_handler(self.print)
        super(TestServer, self).__init__(address, dispatcher)

    def print(self, address, *args):
        print(f"{address}: {args}")


class OSCForwarder:
    """ start this script and forward the data written to STDOUT via osc.
     to check on open ports, run
       LINUX: `sudo netstat -lpn |grep :8080`
       OSX `lsof -Pn -i4 | grep 8080`
    """
    def __init__(self, client: SimpleUDPClient):
        self.__client = client
        self.recorder = Popen(['python3', 'tests/write_to_screen.py'], stdout=PIPE)
        self.buffer = b''

    def run(self):
        while True:
            out = self.recorder.stdout.read(1)
            if out == b'\n':
                if self.buffer.find(b'\t') > 0:
                    neuron, spiketime = self.buffer.split(b'\t')
                    self.__client.send_message(ROUTE, int(neuron))
                    # print('Receiving: neuron {} at time {}'.format(
                    #     int(neuron), float(spiketime)))
                else:
                    print(self.buffer.decode('utf-8'))
                self.buffer = b''
            else:
                self.buffer += out


class NetworkServer(BlockingOSCUDPServer):
    def __init__(self, address, network, client):
        self.network = network
        self.client = client

        dispatcher = Dispatcher()
        dispatcher.map(START_SIMULATION, network.simulate)

        dispatcher.map(RECORDED_NEURONS, self._send_recorded_neurons)
        super(NetworkServer, self).__init__(address, dispatcher)

    def _send_recorded_neurons(self, *args):
        neurons = self.network.get_recorded_neuron_ids()
        msg = pickle.dumps(neurons)
        self.client.send_message(RECORDED_NEURONS, msg)


if __name__ == '__main__':
    # import sys
    # sys.path.append('..')
    # from simulator.nest_code import brunel_basic
    #
    # network_instance = brunel_basic.Network()
    # network_instance.setup()
    #
    # osc_client = SimpleUDPClient(RECEIVER_ADDRESS[0], RECEIVER_ADDRESS[1])
    #
    # server = NetworkServer(NETWORK_ADDRESS, network_instance, osc_client)
    #
    # server.serve_forever()
    server = TestServer(NETWORK_ADDRESS)
    server.serve_forever()
