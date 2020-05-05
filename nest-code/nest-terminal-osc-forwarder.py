# Taken from https://healeycodes.com/javascript/python/beginners/webdev/2019/04/11/talking-between-languages.html

from subprocess import Popen, PIPE
from pythonosc.udp_client import SimpleUDPClient


address = '/spikes'


class OSCForwarder:
    def __init__(self, client, simlator_script='brunel_delta_nest.py'):
        self.__client = client
        self.__recorder = Popen(['python3', simlator_script], stdout=PIPE)
        self.buffer = b''

    def run(self):

        while True:
            out = self.__recorder.stdout.read(1)

            if out == b'\n':
                if self.buffer.find(b'\t') > 0:
                    neuron, spiketime = self.buffer.split(b'\t')
                    client.send_message(address, int(neuron))
                    # print('Receiving: neuron {} at time {}'.format(
                    #     int(neuron), float(spiketime)))
                else:
                    print(str(self.buffer))
                self.buffer = b''
            else:
                self.buffer += out


if __name__ == '__main__':
    ip = '192.168.33.1'
    port = 8080
    client = SimpleUDPClient(ip, port)

    forwarder = OSCForwarder(client)
    forwarder.run()
