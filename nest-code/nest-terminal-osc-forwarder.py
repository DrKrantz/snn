# Taken from https://healeycodes.com/javascript/python/beginners/webdev/2019/04/11/talking-between-languages.html

from subprocess import Popen, PIPE
from pythonosc.udp_client import SimpleUDPClient


class OSCForwarder:
    def __init__(self, client, address, simlator_script='nest-code/brunel_delta_nest.py'):
        self.__client = client
        self.__address = address
        self.__recorder = Popen(['python3', simlator_script], stdout=PIPE)
        self.buffer = b''

    def run(self):
        while True:
            out = self.__recorder.stdout.read(1)

            if out == b'\n':
                if self.buffer.find(b'\t') > 0:
                    neuron, spiketime = self.buffer.split(b'\t')
                    self.__client.send_message(self.__address, int(neuron))
                    # print('Receiving: neuron {} at time {}'.format(
                    #     int(neuron), float(spiketime)))
                else:
                    print(self.buffer.decode('utf-8'))
                self.buffer = b''
            else:
                self.buffer += out


if __name__ == '__main__':
    import config_parser
    ip = config_parser.config['sources']['simulator']['ip']
    port = config_parser.config['sources']['simulator']['port']
    osc_client = SimpleUDPClient(ip, port)

    forwarder = OSCForwarder(osc_client, config_parser.config['sources']['simulator']['address'])
    forwarder.run()
