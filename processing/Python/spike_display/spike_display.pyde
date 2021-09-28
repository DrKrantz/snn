import json
import math

add_library('oscP5')

IP = "127.0.0.1"
SPIKE_DISPLAY_PORT = 1338
SPIKE_DISPLAY_ADDRESS = '/display_spikes'

global spike_surface
spike_surface = None

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
            

def linear2grid(nid, n_col):
    # return col_id, row_id
    # neuron 0 will be in the bottom left corner with coordintates (0,0), neuron 1 is (1,0)
    #Nnotes = 120
    # the equation is n_col*row_id+col_id = nid
    col_id = math.remainder(nid, n_col)
    row_id = math.ceil((nid-col_id)/N_col)
    return col_id, row_id

class SpikeSurface:
    def __init__(self, n_col=20, n=400, width=500, height=500):
        self.__border = 5
        self.__n_col = n_col
        self.__n_row = math.ceil(n / n_col)
        self.__x_dist = (width - 2*self.__border) / self.__n_col # x-distance btwn grid
        self.__y_dist = (height - 2*self.__border) / self.__n_row  # y-distance btwn grid
        
        self.set_fired([])
        self.surface = createGraphics(width, height)
        self.surface.smooth()
        with self.surface.beginDraw():
            self.surface.background(0)
    
    def draw(self):
        with self.surface.beginDraw():
            self.surface.background(0)
            if len(self.__fired) == 0:
                self.surface.text("NICHTS", self.surface.width/2, self.surface.height/2)
            else:
                for n_id in self.__fired:
                    col_id, row_id = linear2grid(n_id, self.__n_col)
                    x = self.__border + col_id*self.__x_dist
                    y = self.__border + row_id*self.__y_dist
                    self.surface.circle(x,y)
                #self.surface.text("ETWAS", self.surface.width/2, self.surface.height/2)
        image(self.surface, 0, 0)
        self.set_fired([])
        
    def set_fired(self, fired):
        self.__fired = fired
        
def setup():
    size(500, 500)
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
    
