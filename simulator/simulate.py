import sys
import pathlib
import os
import importlib

sys.path.append(str(pathlib.Path(os.path.dirname(__file__)).parent))
from output import sockets
import config_parser

print('********  BULDING NETWORK ***********')
network_module = importlib.import_module('simulator.nest_code.{}'.format(config_parser.get('simulation_script')))
network_instance = network_module.Network()
network_instance.setup()

init_socket = sockets.InitSocket(config_parser.get_address('forwarder_from_docker'))
init_socket.send_short_init(network_instance.get_recorded_neuron_ids())

print('********  RUNNING SIMULATION ***********')
network_instance.simulate()
