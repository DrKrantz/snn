import numpy as np
import pygame
from Dunkel_functions import linear2grid
from Dunkel_pars import parameters
import outputHandler
import asyncio

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer

refresh_rate = 100.  # Hz


class SpikeDisplay:

    def __init__(self, n_col, n_row, screen_size=(1680, 1050)):
        pygame.init()

        self.n_col = n_col
        self.n_row = n_row

        self.spike_screen = pygame.display.set_mode(screen_size, 0, 32)

        self.pointXDist = screen_size[0] / self.n_col  # x-distance btwn points
        self.pointYDist = screen_size[1] / self.n_row  # y-distance btwn points
        self.point_size = 3  # the point size in case of 'dot'-display
        self.border = 5
        self.spike_color = (255, 255, 255, 255)
        self.spikefill_color = (0, 0, 0, 0)
        self.line_width = 3

    def update(self, fired):
        pygame.event.get()
        self.spike_screen.fill(self.spikefill_color)

        coord = [linear2grid(n_id, self.n_col) * (self.pointXDist, self.pointYDist) for n_id in fired]
        coord = np.array(coord, dtype=int) + self.border

        if len(coord) > 1:
            pygame.draw.lines(self.spike_screen,
                              self.spike_color,
                              1,
                              coord,
                              self.line_width)
        elif len(coord) == 1:
            pygame.draw.circle(self.spike_screen,
                               self.spike_color,
                               coord[0],
                               self.point_size,
                               0)
        pygame.display.update()
        pygame.display.flip()

    def turn_all_off(self, _, *__):
        self.spike_screen.fill(self.spikefill_color)


class DisplayServer:
    server = None

    def __init__(self, display, config):
        self.fired = []
        self.display = display
        self.config = config

    def handle_spikes(self, _, *fired):
        self.fired += fired

    async def loop(self):
        while True:

            self.display.update(self.fired)
            self.fired = []
            await asyncio.sleep(1. / refresh_rate)

    async def init_main(self):
        dispatcher = Dispatcher()
        dispatcher.map(outputHandler.ADDRESS_SPIKES, self.handle_spikes)

        self.server = AsyncIOOSCUDPServer((self.config['ip'], self.config['port']), dispatcher,
                                          asyncio.get_event_loop())
        transport, protocol = await self.server.create_serve_endpoint()  # Create datagram endpoint and start serving
        await self.loop()  # Enter main loop of program

        transport.close()  # Clean up serve endpoint


if __name__ == '__main__':
    pars = parameters()
    display_class = SpikeDisplay(pars['N_col'], pars['N_row'], screen_size=(200, 200))
    import config_parser
    if 'spike_display' not in config_parser.config['displays']:
        raise ValueError('spike_display not configured in config-file')
    display_server = DisplayServer(display_class, config_parser.config['displays']['spike_display'])
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(display_server.init_main())
