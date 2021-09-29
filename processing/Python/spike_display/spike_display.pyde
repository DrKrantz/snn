import json
import math

add_library('oscP5')

IP = "127.0.0.1"
SPIKE_DISPLAY_PORT = 1338
SPIKE_DISPLAY_ADDRESS = '/display_spikes'

global spike_surface
spike_surface = None

linear2grid = json.load(open("../../../data/linear2grid_400_20.json"))

class Listen(OscEventListener):
    def oscEvent(self, m):
        global loc, osc, spike_surface
        if m.checkAddrPattern(SPIKE_DISPLAY_ADDRESS) == True:
            data = json.loads(m.arguments()[0])
            # if len(data)>0:
            #     print("receiving", data)
            spike_surface.set_fired(data)
        else:
            print("Address not mapped")
            

# def linear2grid(nid, n_col):
#     # return col_id, row_id
#     # neuron 0 will be in the bottom left corner with coordintates (0,0), neuron 1 is (1,0)
#     #Nnotes = 120
#     # the equation is n_col*row_id+col_id = nid
#     col_id = math.remainder(nid, n_col)
#     row_id = math.ceil((nid-col_id)/N_col)
#     return col_id, row_id

class SpikeSurface:
    CIRCLE_SIZE = 5
    LINE_WIDTH = 5
    
    def __init__(self, n_col=20, n=400, plot_mode='dot', width=1280, height=720):
        self.__border = 5
        self.__n_col = n_col
        self.__n_row = math.ceil(n / n_col)
        self.__x_dist = (width - 2*self.__border) / self.__n_col # x-distance btwn grid
        self.__y_dist = (height - 2*self.__border) / self.__n_row  # y-distance btwn grid
        
        self.__plot_mode = plot_mode
        self.set_fired([])
        self.surface = createGraphics(width, height)
        self.surface.smooth()
        stroke(255)
        # strokeWeight(self.LINE_WIDTH)
        with self.surface.beginDraw():
            self.surface.background(0)
    
    def draw(self):
        with self.surface.beginDraw():
            self.surface.background(0)
            if len(self.__fired) == 0:
                pass  # self.surface.text("NICHTS", self.surface.width/2, self.surface.height/2)
            else:
                if self.__plot_mode == 'dot':
                    for n_id in self.__fired:
                        col_id, row_id = linear2grid[str(n_id)]
                        x = self.__border + col_id*self.__x_dist
                        y = self.__border + row_id*self.__y_dist
                        self.surface.circle(x,y, self.CIRCLE_SIZE)
                elif self.__plot_mode == 'line':
                    if len(self.__fired) == 1:
                        col_id, row_id = linear2grid[str(self.__fired[0])]
                        x = self.__border + col_id*self.__x_dist
                        y = self.__border + row_id*self.__y_dist
                        self.surface.circle(x,y, self.CIRCLE_SIZE)
                    else:
                        x_vals = []
                        y_vals = []
                        for n_id in self.__fired:
                            col_id, row_id = linear2grid[str(n_id)]
                            x_vals.append(self.__border + col_id*self.__x_dist)
                            y_vals.append(self.__border + row_id*self.__y_dist)
                        for idx, x1 in enumerate(x_vals):
                            y1 = y_vals[idx]
                            idx2 = idx+1 if idx < len(x_vals)-1 else 0
                            x2 = x_vals[idx2]
                            y2 = y_vals[idx2]
                            self.surface.line(x1, y1, x2, y2)
                    
                #self.surface.text("ETWAS", self.surface.width/2, self.surface.height/2)
        image(self.surface, 0, 0)
        self.set_fired([])
        
    def set_fired(self, fired):
        self.__fired = fired
        
def setup():
    frameRate(20)
    # fullScreen()
    size(1280, 720)
    background(200)
    global spike_surface
    
    spike_surface = build_surface()
    
    osc = OscP5(this, SPIKE_DISPLAY_PORT)  # the PERFORMER_PORT
    loc = NetAddress(IP, SPIKE_DISPLAY_PORT)  # send to self
    global listener
    listener = Listen()
    osc.addListener(listener)
    
def draw():
    global spike_surface
    if spike_surface is not None:
        spike_surface.draw()
    else:
        print("surface not yet bui;d")
        
def build_surface():
    surf = SpikeSurface()
    return surf

def stop():
    global osc
    osc.dispose()
    
