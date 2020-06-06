from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher


class TestServer(BlockingOSCUDPServer):
    def __init__(self, address):
        dispatcher = Dispatcher()
        dispatcher.map('/test', print)
        super(TestServer, self).__init__(address, dispatcher)


if __name__ == '__main__':
    import sys
    server_ip = '127.0.0.1'
    server_port = 8080
    print(sys.argv)
    if len(sys.argv) > 1:
        server_ip = sys.argv[1]
        server_port = sys.argv[2]

    server = TestServer((server_ip, server_port))
    print('starting')
    server.serve_forever()
