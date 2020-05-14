import argparse


parser = argparse.ArgumentParser()
parser.add_argument('app')
args = parser.parse_args()

if args.app == 'output':
    import numpy as np
    import config_parser
    from output.output_server import OutputServer

    from output import neuron_to_note, output_devices

    server = OutputServer(config_parser.config['output']['server'])  # TODO: allow other sound targets

    # converter = neuron_to_note.TogglingConverter(np.arange(1, 96), neuron_to_note.SCALE_MAJOR,
    #                                              neuron_to_note.SCALE_MAJOR + 1)
    # # simple_synth = sound_devices.SoundDevice(converter)
    # server.register_device(simple_synth)

    # iac = output_devices.MidiDevice(converter, midi_port='IAC Driver Bus 1')

    converter = neuron_to_note.LinearConverter(offset=0)
    osc_device = output_devices.OscDevice(converter)

    ADDRESS_RECORDED_NEURONS = '/recorded_neurons'
    server.register_device(osc_device)
    server.register_callback(ADDRESS_RECORDED_NEURONS, osc_device.init_instrument)

    server.start()

elif args.app == 'instrument':
    from output import instrument
    import asyncio

    instrument_server = instrument.OscInstrument(volume_update_cb=instrument.update_volume_additive)

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(instrument_server.init_main())

elif args.app == 'start':
    from pythonosc.udp_client import SimpleUDPClient

    ADDRESS_RECORDED_NEURONS = '/recorded_neurons'
    ADDRESS_SIMULATE = '/simulate'
    IP = "192.168.33.10"
    PORT = 8080
    client = SimpleUDPClient(IP, PORT)

    print('Triggering Instrument initialization')
    client.send_message(ADDRESS_RECORDED_NEURONS, 1)

    print('Sending start signal to simulator')
    client.send_message(ADDRESS_SIMULATE, 1)
