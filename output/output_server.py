from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import numpy as np

import outputHandler
from output import sound_devices, neuron_to_note


class OutputServer:
    server = None
    dispatcher = None

    def __init__(self, config):
        self.dispatcher = Dispatcher()
        self.address = (config['ip'], config['port'])

    def register_device(self, device):
        self.dispatcher.map(outputHandler.ADDRESS_SPIKES, device.update)
        self.dispatcher.map(outputHandler.ADDRESS_OFF, device.turn_all_off)

    def start(self):
        self.server = BlockingOSCUDPServer(self.address, self.dispatcher)
        self.server.serve_forever()


if __name__ == '__main__':
    import config_parser
    server = OutputServer(config_parser.config['sound']['neuron_notes'])  # TODO: allow other sound targets

    converter = neuron_to_note.TogglingConverter(np.arange(1, 96), neuron_to_note.SCALE_MAJOR,
                                                 neuron_to_note.SCALE_MAJOR + 1)
    # simple_synth = sound_devices.SoundDevice(converter)
    # server.register_device(simple_synth)

    iac = sound_devices.MidiDevice(converter, midi_port='IAC Driver Bus 1')
    server.register_device(iac)
    server.start()
