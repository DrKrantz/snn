from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import numpy as np

import outputHandler
import SoundDevices
import neuron_to_note


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
    converter = neuron_to_note.Neuron2NoteConverter(np.arange(1, 96), neuron_to_note.SCALE_MAJOR)
    simple_synth = SoundDevices.SoundDevice(converter)
    server = SoundServer()
    server.register_device(simple_synth)
    server.start()

