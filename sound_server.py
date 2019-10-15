from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import numpy as np

import outputHandler
import sound_devices
import neuron_to_note


class SoundServer:
    server = None
    dispatcher = None

    def __init__(self):
        self.dispatcher = Dispatcher()

    def register_device(self, device):
        self.dispatcher.map(outputHandler.ADDRESS_SOUND_SPIKES, device.update)
        self.dispatcher.map(outputHandler.ADDRESS_SOUND_OFF, device.turn_all_off)

    def start(self):
        self.server = BlockingOSCUDPServer((outputHandler.IP, outputHandler.PORT), self.dispatcher)
        self.server.serve_forever()


if __name__ == '__main__':
    server = SoundServer()

    converter = neuron_to_note.TogglingConverter(np.arange(1, 96), neuron_to_note.SCALE_MAJOR, neuron_to_note.SCALE_MAJOR+1)
    simple_synth = sound_devices.SoundDevice(converter)
    server.register_device(simple_synth)

    server.start()
