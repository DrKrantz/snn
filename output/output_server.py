from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from config import routing


class OutputServer:
    server = None
    dispatcher = None

    def __init__(self, address):
        self.dispatcher = Dispatcher()
        self.address = address

    def register_device(self, device):
        self.register_callback(routing.FIRING_NEURONS, device.update)
        self.register_callback(routing.DEVICE_OFF, device.turn_all_off)

    def register_callback(self, address, cb):
        self.dispatcher.map(address, cb)

    def start(self):
        self.server = BlockingOSCUDPServer(self.address, self.dispatcher)
        print('Starting output server')
        self.server.serve_forever()
