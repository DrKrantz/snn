import argparse


parser = argparse.ArgumentParser()
parser.add_argument('app')
args = parser.parse_args()

if args.app == 'network':
    import numpy as np
    import pickle

    from mocks import network
    from osc_helpers.clients import DefaultClient
    from output import neuron_to_note
    import config_parser
    from config import routing

    N = 50
    min_rate = 0.1
    max_rate = 3
    res = 0.1
    sim_time = 10
    rates = np.random.random(N) * (max_rate - min_rate) + min_rate

    #  initialize instrument
    client = DefaultClient(config_parser.get_address('instrument'), routing.FIRING_NEURONS)
    frequencies = neuron_to_note.get_frequencies_for_range(440, 1200, N)
    message = {'ids': list(range(N)),
               'frequencies': frequencies}
    client.send_message(routing.INIT_INSTRUMENT, pickle.dumps(message))

    # create network-mock
    network = network.NetworkMock(client, rates, res=res, sim_time=sim_time)

    input("Ready? Wating for go signal")

    network.run()
