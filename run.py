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

elif args.app == 'file_player':
    import config_parser
    from mocks.file_player import FilePlayer
    from output import neuron_to_note

    file = 'simulator/nest_code/brunel-py-ex-12502-0.gdf'
    player = FilePlayer(file, config_parser.get_address('spike_forwarder'), time_to_start=13)

    complete = 'n'
    while complete != 'Y':
        player.send_init()
        complete = input('Initialization complete? [Y / n]') or 'Y'

    player.play()

elif args.app == 'spike_forwarder':
    from output.sockets import SpikeSocket, SpikeForwarder
    import config_parser
    from output import neuron_to_note
    converter = neuron_to_note.LinearConverter(offset=1)

    spike_forwarder = SpikeForwarder(config_parser.get_address('spike_forwarder'))
    instrument_socket = SpikeSocket(config_parser.get_address('instrument'), converter.id_to_index)
    spike_forwarder.register_target(instrument_socket)

    spike_forwarder.run()

else:
    print('Unknown app {}!'.format(args.app))
