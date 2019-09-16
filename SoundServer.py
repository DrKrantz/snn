from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

import outputHandler
import SoundDevices


class SoundServer:
    server = None
    dispatcher = None

    def __init__(self):
        self.dispatcher = Dispatcher()

    def register_device(self, device):
        self.dispatcher.map(outputHandler.ADDRESS_SOUND, device.update)

    def start(self):
        self.server = BlockingOSCUDPServer((outputHandler.IP, outputHandler.PORT), self.dispatcher)
        self.server.serve_forever()


if __name__ == '__main__':
    simple_synth = SoundDevices.SoundDevice()
    server = SoundServer()
    server.register_device(simple_synth)
    server.start()

