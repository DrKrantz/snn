import numpy as np
from networks.network_base import NetworkBase


class Network(NetworkBase):
    def __init__(self):
        super(Network, self).__init__()

    def _neuron_parameters(self):
        self.a_e = 0.04e-6  # adaptation dynamics of e-synapses, S
        self.a_i = 0.08e-6  # adaptation dynamics of i-synapses, S
        self.b_e = 0  # 0.03e-9 # adaptation increment of e-synapses, A
        self.b_i = 0.03e-9  # adaptation increment of i-synapses, A

    def _network_parameters(self):
        self.N_col = 20
        self.N_row = 20
        self.percExc = 0.5  # proportion of excitatory neurons in network

    def _build_connectivity(self):
        n_ee = 0  # number of incoming synapses (from e to e)
        n_ei = 2  # number of incoming synapses (from e to i)
        n_ie = 8  # number of incoming synapses (from i to e)
        n_ii = 8  # number of incoming synapses (from i to i)

        self.A = np.zeros((self.N, self.N))
        #  ee is 0

        # exc presynaptic IDs for inh neurons
        pres_ids = np.random.choice(self.exc_ids, (self.N_i, n_ei))
        for pres_no, inh_id in enumerate(self.inh_ids):
            self.A[inh_id, pres_ids[pres_no]] = 1

        # inh presynaptic IDs for exc neurons
        pres_ids = np.random.choice(self.inh_ids, (self.N_e, n_ie))
        for pres_no, exc_id in enumerate(self.exc_ids):
            self.A[exc_id, pres_ids[pres_no]] = 1

        # inh presynaptic IDs for inh neurons
        pres_ids = np.random.choice(self.inh_ids, (self.N_i, n_ii))
        for pres_no, inh_id in enumerate(self.inh_ids):
            self.A[inh_id, pres_ids[pres_no]] = 1

        np.fill_diagonal(self.A, 0)  # remove self-loops!!!!

