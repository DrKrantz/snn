# Taken from https://healeycodes.com/javascript/python/beginners/webdev/2019/04/11/talking-between-languages.html

from subprocess import Popen, PIPE

#  to check on open ports, run `sudo netstat -lpn |grep :8080`


class OSCForwarder:
    def __init__(self, client, simlator_script='nest-code/brunel_delta_nest.py'):
        self.__client = client
        self.__recorder = Popen(['python3', simlator_script], stdout=PIPE)
        self.buffer = b''

    def run(self):
        while True:
            out = self.__recorder.stdout.read(1)

            if out == b'\n':
                if self.buffer.find(b'\t') > 0:
                    neuron, spiketime = self.buffer.split(b'\t')
                    self.__client.send_to_default(int(neuron))
                    # print('Receiving: neuron {} at time {}'.format(
                    #     int(neuron), float(spiketime)))
                else:
                    print(self.buffer.decode('utf-8'))
                self.buffer = b''
            else:
                self.buffer += out


if __name__ == '__main__':
    import config_parser
    from config import routing
    from osc_helpers.clients import DefaultClient

    osc_client = DefaultClient(config_parser.get_address('output_server'), routing.FIRING_NEURONS)

    print(" ----------------------- Creating forwarder")
    forwarder = OSCForwarder(osc_client)
    forwarder.run()
