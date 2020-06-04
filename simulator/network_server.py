import pickle

from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient

from config import routing


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

    osc_client = SimpleUDPClient(config_parser.config['ip']['output_server'],
                                 config_parser.config['port']['output_server'])

    server = NetworkServer(config_parser.get_address('simulator'), network_instance, osc_client)

    server.serve_forever()
