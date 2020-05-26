import argparse


parser = argparse.ArgumentParser()
parser.add_argument('app')
args = parser.parse_args()

if args.app == 'network':
    import numpy as np
    import pickle

    from mocks import network
    from routing.clients import SingleAddressClient
    from output import neuron_to_note, instrument

    N = 50
    min_rate = 0.1
    max_rate = 3
    res = 0.1
    sim_time = 10
    rates = np.random.random(N) * (max_rate - min_rate) + min_rate

    init_client = SingleAddressClient(instrument.IP, instrument.PORT, instrument.INIT_ADDRESS)
    frequencies = neuron_to_note.get_frequencies_for_range(440, 1200, N)
    message = {'ids': list(range(N)),
               'frequencies': frequencies}
    init_client.send_to_base_address(pickle.dumps(message))

    osc_client = SingleAddressClient(instrument.IP, instrument.PORT, instrument.UPDATE_ADDRESS)
    network = network.NetworkMock(osc_client, rates, res=res, sim_time=sim_time)

    input("Ready? Wating for go signal")

    network.run()
