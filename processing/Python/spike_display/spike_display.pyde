add_library('oscP5')
addr = "?"

IP = "127.0.0.1"
SPIKE_DISPLAY_PORT = 1338
SPIKE_DISPLAY_ADDRESS = '/display_spikes'


class Listen(OscEventListener):
    def oscEvent(self, m):
        global loc, osc
        if m.checkAddrPattern(SPIKE_DISPLAY_ADDRESS) == True:
            data = json.loads(m.arguments()[0])[1]
            print(data)
            

class Surface:
    def __init__():
        self.surface = createGraphics(1000, 500)
        self.surface.smooth()
        with self.surface.beginDraw():
                self.surface.background(222)
                

def setup():
    size(1000, 500)
    background(200)
    
    osc = OscP5(this, SPIKE_DISPLAY_PORT)  # the PERFORMER_PORT
    loc = NetAddress(IP, SPIKE_DISPLAY_PORT)  # send to self
    global listener
    listener = Listen()
    osc.addListener(listener)
