from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.osc_server import BlockingOSCUDPServer

import argparse

import config_parser
from config import routing


parser = argparse.ArgumentParser()
parser.add_argument('app')
args = parser.parse_args()

if args.app == 'simulator-server':
    def success(*args):
        print('Success: simulator receive')

    ip, port = config_parser.get_address('simulator')
    dispatcher = Dispatcher()
    dispatcher.map(routing.START_SIMULATION, success)
    simul_server = BlockingOSCUDPServer((ip, port), dispatcher)
    print('Starting simulator server')
    simul_server.serve_forever()

elif args.app == 'start-client':
    ip, port = config_parser.get_address('simulator')
    client = SimpleUDPClient(ip, port)
    print('Sending start signal')
    client.send_message(routing.START_SIMULATION, 1)

elif args.app == 'simulator-client':
    ip, port = config_parser.get_address('spike_forwarder')
    client = SimpleUDPClient(ip, port)
    print('Sending Firing neurons: [1]')
    client.send_message(routing.FIRING_NEURONS, [1])

elif args.app == 'output-client':
    ip, port = config_parser.get_address('instrument')
    client = SimpleUDPClient(ip, port)
    print('Sending Firing neurons: [1, 2]')
    client.send_message(routing.FIRING_NEURONS, [1, 2])

elif args.app == 'instrument-server':
    def success(_, *indices):
        print('Success: instrument-server receives {}'.format(indices))


    ip, port = config_parser.get_address('instrument')

    dispatcher = Dispatcher()
    dispatcher.map(routing.FIRING_NEURONS, success)
    output_server = BlockingOSCUDPServer((ip, port), dispatcher)
    print('Starting instrument-server')
    output_server.serve_forever()

else:
    print("Unkonwn app ", args.app)


