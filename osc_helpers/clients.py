from pythonosc.udp_client import SimpleUDPClient


class DefaultClient(SimpleUDPClient):
    """ A SimpleUDPClient with a default target route  """
    def __init__(self, address: tuple, route):
        ip, port = address
        self.__route = route
        super(DefaultClient, self).__init__(ip, port)

    def send_to_default(self, value):
        super(DefaultClient, self).send_message(self.__route, value)


if __name__ == '__main__':
    import time
    import sys

    client_ip = '127.0.0.1'
    client_port = 8080
    if len(sys.argv) > 1:
        client_ip = sys.argv[1]
        client_port = sys.argv[2]

    client = DefaultClient((client_ip, client_port), '/test')
    client.send_to_default(1)
    time.sleep(0.3)
    client.send_to_default(2)
