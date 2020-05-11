from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer


ADDRESS_SPIKES = "/spikes"
ADDRESS_OFF = "/off/"


class OutputServer:
    server = None
    dispatcher = None

    def __init__(self, config):
        self.dispatcher = Dispatcher()
        self.address = (config['ip'], config['port'])

    def register_device(self, device):
        self.dispatcher.map(ADDRESS_SPIKES, device.update)
        self.dispatcher.map(ADDRESS_OFF, device.turn_all_off)

    def start(self):
        self.server = BlockingOSCUDPServer(self.address, self.dispatcher)
        print('Starting output server')
        self.server.serve_forever()
