import pygame.font
from numpy import intersect1d
from pythonosc.udp_client import SimpleUDPClient

from outputDevices import *

ADDRESS_SOUND_SPIKES = "/sound/spikes/"
ADDRESS_SOUND_OFF = "/sound/all_off/"
ADDRESS_VISUAL_SPIKES = "/visual/spikes/"
IP = "127.0.0.1"
PORT = 1337
VISUAL_PORT = 1338


class OutputHandler(object):
    def __init__(self, pars):
        super(OutputHandler, self).__init__()
        self.pars = pars

        self.__client = SimpleUDPClient(IP, PORT)
        self.__visual_client = SimpleUDPClient(IP, VISUAL_PORT)
        pm.init()

        self.__now = time.time()
        self.__activeNotes = set()

    def update(self, fired):
        neuron_ids = intersect1d(fired, self.pars['note_ids'])

        if len(neuron_ids) > 0:
            ids = [int(i) for i in neuron_ids]  # TODO: I'm sure there's a smarter way to fix this
            self.__client.send_message(ADDRESS_SOUND_SPIKES, ids)
            self.__visual_client.send_message(ADDRESS_VISUAL_SPIKES, ids)

    def turn_off(self):
        self.__client.send_message(ADDRESS_SOUND_OFF, 0)


if __name__ == '__main__':
    from Dunkel_functions import parameters
    output_handler = OutputHandler(parameters())
    input('feddich wenn Sie es sind...')
    basic = np.array([1, 2, 7, 55])
    for k in range(10):
        output_handler.update(basic + k * 10)
        pygame.display.update()
        time.sleep(0.1)
