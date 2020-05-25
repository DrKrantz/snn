import argparse


parser = argparse.ArgumentParser()
parser.add_argument('app')
args = parser.parse_args()

if args.app == 'network':
    from mocks import network
    import numpy as np
    from routing.clients import SingleAddressClient

    import config_parser

    ip = config_parser.config['output']['server']['ip']
    port = config_parser.config['output']['server']['port']
    address = config_parser.config['output']['server']['route']
    osc_client = SingleAddressClient(ip, port, address)

    N = 5
    min_rate = 0.1
    max_rate = 3
    res = 0.1
    sim_time = 10

    rates = np.random.random(N) * (max_rate - min_rate) + min_rate
    network = network.NetworkMock(osc_client, rates, res=res, sim_time=sim_time)

    network.run()
