add_library('oscP5')
addr = "?"


SPIKE_DISPLAY_ADDRESS = '/display_spikes'

class Listen(OscEventListener):

    def oscEvent(self, m):
        global loc, osc
        if m.checkAddrPattern(SPIKE_DISPLAY_ADDRESS) == True:
            print(m.arguments())
            

def setup():
    size (1000, 500)
    background(200)
    
    osc = OscP5(this, 5050)  # the PERFORMER_PORT
    loc = NetAddress('192.168.1.156', 5050)  # send to self
    global listener
    listener = Listen()
    osc.addListener(listener)
