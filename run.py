import argparse


parser = argparse.ArgumentParser()
parser.add_argument('app')
args = parser.parse_args()

if args.app == 'output':

    import config_parser
    from config import routing
    from output.output_server import OutputServer

    from output import neuron_to_note, output_devices

    server = OutputServer(config_parser.get_address('output_server'))  # TODO: allow other sound targets

    # import numpy as np
    # converter = neuron_to_note.TogglingConverter(np.arange(1, 96), neuron_to_note.SCALE_MAJOR,
    #                                              neuron_to_note.SCALE_MAJOR + 1)
    # # simple_synth = sound_devices.SoundDevice(converter)
    # server.register_device(simple_synth)

    # iac = output_devices.MidiDevice(converter, midi_port='IAC Driver Bus 1')

    converter = neuron_to_note.LinearConverter(offset=0)
    osc_device = output_devices.OscDevice(converter, config_parser.get_address('instrument'))

    server.register_device(osc_device)
    server.register_callback(routing.RECORDED_NEURONS, osc_device.init_instrument)

    server.start()

elif args.app == 'instrument':
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

else:
    print('Unknown app {}!'.format(args.app))
