# -*- coding: utf-8 -*-
#
# brunel_delta_nest.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

"""Random balanced network (delta synapses)
----------------------------------------------

This script simulates an excitatory and an inhibitory population on
the basis of the network used in [1]_

When connecting the network customary synapse models are used, which
allow for querying the number of created synapses. Using spike
detectors the average firing rates of the neurons in the populations
are established. The building as well as the simulation time of the
network are recorded.

References
~~~~~~~~~~~~~~

.. [1] Brunel N (2000). Dynamics of sparsely connected networks of excitatory and
       inhibitory spiking neurons. Journal of Computational Neuroscience 8,
       183-208.

"""

###############################################################################
# Import all necessary modules for simulation, analysis and plotting.

import nest
import time
import pickle
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient
import json


ADDRESS_SIMULATE = '/simulate'
ADDRESS_RECORDED_NEURONS = '/recorded_neurons'
IP = "192.168.33.10"
PORT = 8080


class NetworkServer(BlockingOSCUDPServer):
    def __init__(self, network, client):
        self.network = network
        self.client = client

        dispatcher = Dispatcher()
        dispatcher.map(ADDRESS_SIMULATE, network.simulate)

        dispatcher.map(ADDRESS_RECORDED_NEURONS, self._send_recorded_neurons)
        super(NetworkServer, self).__init__((IP, PORT), dispatcher)

    def _send_recorded_neurons(self, *args):
        neurons = network.get_recorded_neuron_ids()
        msg = pickle.dumps(neurons)
        self.client.send_message(ADDRESS_RECORDED_NEURONS, msg)


class Network:
    def __init__(self):
        nest.ResetKernel()

        self.__set_parameters()

    def __set_parameters(self):
        ###############################################################################
        # Assigning the simulation parameters to variables.

        self.dt = 0.1  # the resolution in ms
        self.simtime = 1000.0  # Simulation time in ms
        self.delay = 1.5  # synaptic delay in ms

        ###############################################################################
        # Definition of the parameters crucial for asynchronous irregular firing of
        # the neurons.

        self.g = 5.0  # ratio inhibitory weight/excitatory weight
        self.eta = 2.0  # external rate relative to threshold rate
        self.epsilon = 0.1  # connection probability

        ###############################################################################
        # Definition of the number of neurons in the network and the number of neuron
        # recorded from

        self.order = 2500
        self.NE = 4 * self.order  # number of excitatory neurons
        self.NI = 1 * self.order  # number of inhibitory neurons
        self.N_neurons = self.NE + self.NI  # number of neurons in total
        self.N_rec = 2  # record from 50 neurons

        ###############################################################################
        # Definition of connectivity parameter

        self.CE = int(self.epsilon * self. NE)  # number of excitatory synapses per neuron
        self.CI = int(self.epsilon * self.NI)  # number of inhibitory synapses per neuron
        self.C_tot = int(self.CI + self.CE)  # total number of synapses per neuron

        ###############################################################################
        # Initialization of the parameters of the integrate and fire neuron and the
        # synapses. The parameter of the neuron are stored in a dictionary.

        self.tauMem = 20.0  # time constant of membrane potential in ms
        self.theta = 20.0  # membrane threshold potential in mV
        self.neuron_params = {"C_m": 1.0,
                              "tau_m": self.tauMem,
                              "t_ref": 2.0,
                              "E_L": 0.0,
                              "V_reset": 0.0,
                              "V_m": 0.0,
                              "V_th": self.theta}
        self.J = 0.1  # postsynaptic amplitude in mV
        self.J_ex = self.J  # amplitude of excitatory postsynaptic potential
        self.J_in = -self.g * self.J_ex  # amplitude of inhibitory postsynaptic potential

        ###############################################################################
        # Definition of threshold rate, which is the external rate needed to fix the
        # membrane potential around its threshold, the external firing rate and the
        # rate of the poisson generator which is multiplied by the in-degree CE and
        # converted to Hz by multiplication by 1000.

        self.nu_th = self.theta / (self.J * self.CE * self.tauMem)
        self.nu_ex = self.eta * self.nu_th
        self.p_rate = 1000.0 * self.nu_ex * self.CE

    def setup(self):
        ###############################################################################
        # Assigning the current time to a variable in order to determine the build
        # time of the network.

        self.startbuild = time.time()

        ###############################################################################
        # Configuration of the simulation kernel by the previously defined time
        # resolution used in the simulation. Setting ``print_time`` to `True` prints the
        # already processed simulation time as well as its percentage of the total
        # simulation time.

        nest.SetKernelStatus({"resolution": self.dt, "print_time": False,
                              "overwrite_files": True})

        print("Building network")

        ###############################################################################
        # Configuration of the model ``iaf_psc_delta`` and ``poisson_generator`` using
        # ``SetDefaults``. This function expects the model to be the inserted as a
        # string and the parameter to be specified in a dictionary. All instances of
        # theses models created after this point will have the properties specified
        # in the dictionary by default.

        nest.SetDefaults("iaf_psc_delta", self.neuron_params)
        nest.SetDefaults("poisson_generator", {"rate": self.p_rate})

        ###############################################################################
        # Creation of the nodes using ``Create``. We store the returned handles in
        # variables for later reference. Here the excitatory and inhibitory, as well
        # as the poisson generator and two spike detectors. The spike detectors will
        # later be used to record excitatory and inhibitory spikes.

        self.nodes_ex = nest.Create("iaf_psc_delta", self.NE)
        self.nodes_in = nest.Create("iaf_psc_delta", self.NI)
        self.noise = nest.Create("poisson_generator")
        self.espikes = nest.Create("spike_detector")
        self.ispikes = nest.Create("spike_detector")

        ###############################################################################
        # Configuration of the spike detectors recording excitatory and inhibitory
        # spikes using ``SetStatus``, which expects a list of node handles and a list
        # of parameter dictionaries. Setting the variable ``to_file`` to `True` ensures
        # that the spikes will be recorded in a .gdf file starting with the string
        # assigned to label. Setting ``withtime`` and ``withgid`` to `True` ensures that
        # each spike is saved to file by stating the gid of the spiking neuron and
        # the spike time in one line.

        nest.SetStatus(self.espikes, [{"label": "brunel-py-ex", "record_to": "screen"}])

        nest.SetStatus(self.ispikes, [{"label": "brunel-py-in"}])

        print("Connecting devices")

        ###############################################################################
        # Definition of a synapse using ``CopyModel``, which expects the model name of
        # a pre-defined synapse, the name of the customary synapse and an optional
        # parameter dictionary. The parameters defined in the dictionary will be the
        # default parameter for the customary synapse. Here we define one synapse for
        # the excitatory and one for the inhibitory connections giving the
        # previously defined weights and equal delays.

        nest.CopyModel("static_synapse", "excitatory",
                       {"weight": self.J_ex, "delay": self.delay})
        nest.CopyModel("static_synapse", "inhibitory",
                       {"weight": self.J_in, "delay": self.delay})

        ###############################################################################
        # Connecting the previously defined poisson generator to the excitatory and
        # inhibitory neurons using the excitatory synapse. Since the poisson
        # generator is connected to all neurons in the population the default rule
        # (# ``all_to_all``) of ``Connect`` is used. The synaptic properties are inserted
        # via ``syn_spec`` which expects a dictionary when defining multiple variables
        # or a string when simply using a pre-defined synapse.

        nest.Connect(self.noise, self.nodes_ex, syn_spec="excitatory")
        nest.Connect(self.noise, self.nodes_in, syn_spec="excitatory")

        ###############################################################################
        # Connecting the first ``N_rec`` nodes of the excitatory and inhibitory
        # population to the associated spike detectors using excitatory synapses.
        # Here the same shortcut for the specification of the synapse as defined
        # above is used.

        nest.Connect(self.nodes_ex[:self.N_rec], self.espikes, syn_spec="excitatory")
        nest.Connect(self.nodes_in[:self.N_rec], self.ispikes, syn_spec="excitatory")

        print("Connecting network")

        print("Excitatory connections")

        ###############################################################################
        # Connecting the excitatory population to all neurons using the pre-defined
        # excitatory synapse. Beforehand, the connection parameter are defined in a
        # dictionary. Here we use the connection rule ``fixed_indegree``,
        # which requires the definition of the indegree. Since the synapse
        # specification is reduced to assigning the pre-defined excitatory synapse it
        # suffices to insert a string.

        conn_params_ex = {'rule': 'fixed_indegree', 'indegree': self.CE}
        nest.Connect(self.nodes_ex, self.nodes_ex + self.nodes_in, conn_params_ex, "excitatory")

        print("Inhibitory connections")

        ###############################################################################
        # Connecting the inhibitory population to all neurons using the pre-defined
        # inhibitory synapse. The connection parameter as well as the synapse
        # paramtere are defined analogously to the connection from the excitatory
        # population defined above.

        conn_params_in = {'rule': 'fixed_indegree', 'indegree': self.CI}
        nest.Connect(self.nodes_in, self.nodes_ex + self.nodes_in, conn_params_in, "inhibitory")


        ###############################################################################
        #  ADD MUSIC
        #

        # N_music = 20  # the number of neurons to send spikes to music
        # music_out = nest.Create('music_event_out_proxy', 1,
        #                         params={'port_name':'p_out'})
        #
        # for i, n in enumerate(nodes_ex[:N_music]):
        #     nest.Connect([n], music_out, "one_to_one", {'music_channel': i})
        #

        ###############################################################################

        # Storage of the time point after the buildup of the network in a variable.
        self.endbuild = time.time()

    def simulate(self, *args):
        ###############################################################################
        # Simulation of the network.

        print("Simulating")

        nest.Simulate(self.simtime)

        ###############################################################################
        # Storage of the time point after the simulation of the network in a variable.
        self.endsimulate = time.time()

    def read(self):

        ###############################################################################
        # Reading out the total number of spikes received from the spike detector
        # connected to the excitatory population and the inhibitory population.

        events_ex = nest.GetStatus(self.espikes, "n_events")[0]
        events_in = nest.GetStatus(self.ispikes, "n_events")[0]

        ###############################################################################
        # Calculation of the average firing rate of the excitatory and the inhibitory
        # neurons by dividing the total number of recorded spikes by the number of
        # neurons recorded from and the simulation time. The multiplication by 1000.0
        # converts the unit 1/ms to 1/s=Hz.

        rate_ex = events_ex / self.simtime * 1000.0 / self.N_rec
        rate_in = events_in / self.simtime * 1000.0 / self.N_rec

        ###############################################################################
        # Reading out the number of connections established using the excitatory and
        # inhibitory synapse model. The numbers are summed up resulting in the total
        # number of synapses.

        num_synapses = (nest.GetDefaults("excitatory")["num_connections"] +
                        nest.GetDefaults("inhibitory")["num_connections"])

        ###############################################################################
        # Establishing the time it took to build and simulate the network by taking
        # the difference of the pre-defined time variables.

        build_time = self.endbuild - self.startbuild
        sim_time = self.endsimulate - self.endbuild

        ###############################################################################
        # Printing the network properties, firing rates and building times.

        print("Brunel network simulation (Python)")
        print("Number of neurons : {0}".format(self.N_neurons))
        print("Number of synapses: {0}".format(num_synapses))
        print("       Exitatory  : {0}".format(int(self.CE * self.N_neurons) + self.N_neurons))
        print("       Inhibitory : {0}".format(int(self.CI * self.N_neurons)))
        print("Excitatory rate   : %.2f Hz" % rate_ex)
        print("Inhibitory rate   : %.2f Hz" % rate_in)
        print("Building time     : %.2f s" % build_time)
        print("Simulation time   : %.2f s" % sim_time)

    def write_recorded_neurons(self):
        filename = 'recorded_neurons.json'
        path = os.path.dirname(os.path.dirname(__file__))

        with open(os.path.join(path, 'config', filename), 'w') as f:
            json.dump(
                {'excitatory': self.nodes_ex[:self.N_rec].tolist()},
                f
            )

    def get_recorded_neuron_ids(self):
        neuron_ids = self.nodes_ex[:self.N_rec].tolist()
        neuron_ids.extend(self.nodes_in[:self.N_rec].tolist())
        return neuron_ids


###############################################################################
# Plot a raster of the excitatory neurons and a histogram.

# nest.raster_plot.from_device(espikes, hist=True)


if __name__ == '__main__':
    import os
    import sys
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.append(path)

    import config_parser

    network = Network()
    network.setup()

    osc_client = SimpleUDPClient(config_parser.config['output']['server']['ip'],
                                 config_parser.config['output']['server']['port'])

    server = NetworkServer(network, osc_client)

    server.serve_forever()
