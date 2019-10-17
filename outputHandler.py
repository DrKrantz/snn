import pygame.font
from numpy import intersect1d
from pythonosc.udp_client import SimpleUDPClient

from outputDevices import *

ADDRESS_SPIKES = "/spikes/"
ADDRESS_OFF = "/off/"


class OutputHandler(object):
    __clients = []

    def __init__(self, pars, output_config):
        super(OutputHandler, self).__init__()
        self.pars = pars
        for docs in output_config.values():
            print(docs)
            [self.__clients.append(SimpleUDPClient(specs['ip'], specs['port'])) for _, specs in docs.items()]

        self.__now = time.time()
        self.__activeNotes = set()

    def update(self, fired):
        neuron_ids = intersect1d(fired, self.pars['note_ids'])

        if len(neuron_ids) > 0:
            ids = [int(i) for i in neuron_ids]  # TODO: I'm sure there's a smarter way to fix this
            [client.send_message(ADDRESS_SPIKES, ids) for client in self.__clients]

    def turn_off(self):
        [client.send_message(ADDRESS_OFF, 0) for client in self.__clients]


if __name__ == '__main__':
    from Dunkel_functions import parameters
    import config_parser
    pm.init()
    output_handler = OutputHandler(parameters(), config_parser.config)
    input('feddich wenn Sie es sind...')
    basic = np.array([1, 2, 7, 55])
    for k in range(10):
        output_handler.update(basic + k * 10)
        time.sleep(0.1)
    output_handler.turn_off()
