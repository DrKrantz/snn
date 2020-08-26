import pickle
from subprocess import Popen, PIPE

from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import routing


class OSCForwarder:
    """ start this script and forward the data written to STDOUT via osc.
     to check on open ports, run
       LINUX: `sudo netstat -lpn |grep :8080`
       OSX `lsof -Pn -i4 | grep 8080`
    """
    def __init__(self, client):
        self.__client = client
        self.recorder = Popen(['python3', __file__], stdout=PIPE)
        self.buffer = b''

    def run(self):
        while True:
            out = self.recorder.stdout.read(1)

            if out == b'\n':
                if self.buffer.find(b'\t') > 0:
                    neuron, spiketime = self.buffer.split(b'\t')
                    self.__client.send_to_default(int(neuron))
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
        dispatcher.map(routing.START_SIMULATION, network.simulate)

        dispatcher.map(routing.RECORDED_NEURONS, self._send_recorded_neurons)
        super(NetworkServer, self).__init__(address, dispatcher)

    def _send_recorded_neurons(self, *args):
        neurons = self.network.get_recorded_neuron_ids()
        msg = pickle.dumps(neurons)
        self.client.send_message(routing.RECORDED_NEURONS, msg)


if __name__ == '__main__':
    import config_parser
    import importlib

    network_module = importlib.import_module('simulator.nest_code.{}'.format(config_parser.get('simulation_script')))

    network_instance = network_module.Network()
    network_instance.setup()

    osc_client = SimpleUDPClient(config_parser.config['ip']['spike_forwarder'],
                                 config_parser.config['port']['spike_forwarder'])

    server = NetworkServer(config_parser.get_address('simulator'), network_instance, osc_client)

    server.serve_forever()
