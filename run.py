import argparse


parser = argparse.ArgumentParser()
parser.add_argument('app')
args = parser.parse_args()

if args.app == 'instrument':
    from output import instrument
    import asyncio
    import os
    import config_parser

    target_file = os.path.join(os.path.dirname(__file__), 'data/sound.pkl')
    instrument_server = instrument.OscInstrument(
        volume_update_cb=instrument.update_volume_additive,
        target_file=target_file
    )

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(instrument_server.init_main(config_parser.get_address(args.app)))

elif args.app == 'start':
    from pythonosc.udp_client import SimpleUDPClient
    from config_parser import config
    from config import routing

    client = SimpleUDPClient(config['ip']['simulator'], config['port']['simulator'])

    print('Triggering Instrument initialization')
    client.send_message(routing.RECORDED_NEURONS, 1)

    print('Sending start signal to simulator')
    client.send_message(routing.START_SIMULATION, 1)

elif args.app == 'simulator':
    import socket
    import config_parser
    from output import sockets
    import struct

    spike_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def forward_cb(in_msg):
        if '\t' in in_msg:
            neuron, _ = in_msg.split('\t')
            out_msg = struct.pack('<bH', sockets.MESSAGETYPE_PERFORMANCE, int(neuron))
            spike_socket.sendto(out_msg, config_parser.get_address('forwarder_from_docker'))
        else:
            print(in_msg)
            
    parser = sockets.ScreenParser(['python', 'tests/network_server.py'], forward_cb)
    parser.run()

elif args.app == 'file-player':
    import config_parser
    from mocks.file_player import FilePlayer
    from output import neuron_to_note
    from output import sockets

    model_node = 'brunel-py-ex-15002'
    init_socket = sockets.InitSocket(config_parser.get_address('forwarder_local'))
    player = FilePlayer(model_node, init_socket, time_to_start=13 )

    print('Starting forwarder initialization')
    complete = 'n'
    while complete != 'Y':
        player.send_init()
        complete = input('Forwarder initialization complete? [Y / n]') or 'Y'

    player.play()

elif args.app == 'forwarder':
    from output.sockets import SpikeSocket, SpikeForwarder, InitSocket
    import config_parser
    from output import neuron_to_note
    import numpy as np

    converter = neuron_to_note.LinearConverter(offset=1)

    spike_forwarder = SpikeForwarder(config_parser.get_address('forwarder_local'))
    instrument_socket = SpikeSocket(config_parser.get_address('instrument'), converter.id_to_index)
    spike_forwarder.register_target(instrument_socket)

    print('Waiting for initialization')
    spike_forwarder.start_init()

    print('Starting instrument initialization')

    #  TODO: this is not a real neuron_ID to frequency conversion yet!
    first_f = 300
    last_f = 15000
    frequencies = np.linspace(first_f, last_f, spike_forwarder.n_neurons)

    init_socket = InitSocket(config_parser.get_address('instrument'))
    complete = 'n'
    while complete != 'Y':
        init_socket.send_long_init(frequencies)
        complete = input('Instrument initialization complete? [Y / n]') or 'Y'

    spike_forwarder.start_forwarding()

else:
    print('Unknown app {}!'.format(args.app))
