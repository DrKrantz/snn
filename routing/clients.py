from pythonosc.udp_client import SimpleUDPClient


class SingleAddressClient(SimpleUDPClient):
    def __init__(self, ip, port, address):
        self.__address = address
        super(SingleAddressClient, self).__init__(ip, port)

    def send(self, value):
        super(SingleAddressClient, self).send_message(self.__address, value)
