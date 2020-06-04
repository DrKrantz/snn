from pythonosc.udp_client import SimpleUDPClient


class SingleAddressClient(SimpleUDPClient):
    def __init__(self, address, route):
        ip, port = address
        self.__route = route
        super(SingleAddressClient, self).__init__(ip, port)

    def send_to_base_address(self, value):
        super(SingleAddressClient, self).send_message(self.__route, value)
