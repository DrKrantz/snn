from pythonosc.udp_client import SimpleUDPClient


class DefaultClient(SimpleUDPClient):
    """ A SimpleUDPClient with a default target route  """
    def __init__(self, address, route):
        ip, port = address
        self.__route = route
        super(DefaultClient, self).__init__(ip, port)

    def send_to_default(self, value):
        super(DefaultClient, self).send_message(self.__route, value)
