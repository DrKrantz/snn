#!/usr/bin/env python

""" Bundle all display classes """

__author__ = "Benjamin Staude"
__email__ = "benjamin.staude@gmail.com"
__date__ = 140620

from utils.Dunkel_functions import *


class Display:
    def __init__(self, N_col, N_row, parnames=[],
                 disp_type='dot', screenSize=(480, 250)):  # disp_type='dot'
        pygame.init()
        # pars = parameters()
        # parnames: list of names for the parameters
        self.parnames = parnames
        n_pars = len(parnames)
        self.disp_type = disp_type
        self.N_col = N_col
        self.N_row = N_row

        self.spikeScreenSize = screenSize  # (1920,1050) #(960,525)#
        self.text_color = (100, 100, 100, 0)
        self.textfill_color = (255, 255, 255, 255)
        self.spikefill_color = (0, 0, 0, 0)
        self.spike_color = (255, 255, 255, 255)

        self.point_size = 3  # the point size in case of 'dot'-display
        self.line_width = 3
        self.pointXDist = self.spikeScreenSize[0] / self.N_col  # x-distance btwn points
        self.pointYDist = self.spikeScreenSize[1] / self.N_row  # y-distance btwn points
        self.border = 5
        self.font_size = 16

        self.text_width = 150
        self.dot_width = N_col*self.pointXDist + 2*self.border
        w = self.dot_width + self.border + self.text_width
        h = max([(self.N_row + 2) * self.pointYDist, (n_pars + 1) * self.font_size])
        self.disp_size = (w, h)

        self.screen = pygame.display.set_mode((0, 0), 0, 32)
        self.par_surface = pygame.Surface((self.text_width, h), flags=SRCALPHA, depth=32)
        self.par_surface.fill(self.textfill_color)
        pygame.font.init()
        self.font = pygame.font.Font(None, self.font_size)

        self.spikeScreen = pygame.display.set_mode(self.spikeScreenSize, 0, 32)
        self.spikeSurface = pygame.Surface(self.spikeScreenSize, flags=SRCALPHA, depth=32)
        self.spikeSurface.fill(self.spikefill_color)

#        modes = pygame.display.list_modes(16)
#        pygame.display.set_mode(modes[0], FULLSCREEN, 16)

        self.update_pars(parnames)

    def update_pars(self, update_names):
        for ii in range(len(update_names)):
            idx = self.parnames.index(update_names[ii])
            text_rect = pygame.Rect((0, idx * self.font_size),
                                    (self.text_width, self.disp_size[1]))
            text = update_names[ii] + ": " + small2string(pars[update_names[ii]])
            ren = self.font.render(text, 1, self.text_color, self.textfill_color)
            self.par_surface.blit(ren, text_rect)
        self.screen.blit(self.par_surface, (self.dot_width + self.border, 0))

    def update_fired(self, fired):
        self.spikeScreen.fill(self.spikefill_color)
        if self.disp_type == 'dot':
            for id in fired:
                coord = self.border + \
                        linear2grid(id, self.N_col) * (self.pointXDist, self.pointYDist)
                pygame.draw.circle(self.screen, (0, 0, 255), coord, self.point_size, 0)
        elif self.disp_type == 'lines':
            coord = [linear2grid(n_id, self.N_col) * (self.pointXDist, self.pointYDist) for n_id in fired]
            coord = array(coord, dtype=int) + self.border

            if len(coord) > 1:
                pygame.draw.lines(self.spikeScreen,
                                  self.spike_color,
                                  1,
                                  coord,
                                  self.line_width)
            elif len(coord) == 1:
                pygame.draw.circle(self.spikeScreen,
                                   self.spike_color,
                                   coord[0],
                                   self.point_size,
                                   0)
        elif self.disp_type == 'square':
            coord = (50, 50)  # linear2grid(id,self.N_col)*(self.pointXDist,self.pointYDist)+self.border
            #  TODO
            pygame.draw.rect(self.spikeScreen, self.spike_color, coord, 1)


class DisplayTest:
    def __init__(self):
        pygame.init()
        pm.init()
        self.__display = Display(pars['N_col'],pars['N_row'],\
                ['Ne','Ni','s_e','s_i','tau_e','tau_i','midi_ext_e','midi_ext_i','cam_ext','cam_external_max'],\
                'lines')

    def start(self):
        input('feddich wenn Sie es sind...')
        for k in range(1000):
            if k % 100 == 0:
                print('jetze')
                self.__display.update_fired(array([20, 40, 70]) + 2 * k)
                #  self.__display.update_fired(array([]))
                pygame.display.flip()
                time.sleep(0.1)


if __name__ == '__main__':
    # uwe = Membrane_Display(4)
    uwe = DisplayTest()
    uwe.start()
