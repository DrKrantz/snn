import numpy as np
from networks.network_base import NetworkBase


class Network(NetworkBase):
    def __init__(self):
        super(Network, self).__init__()

    def _network_parameters(self):
        self.N_col = 25
        self.N_row = 20
        self.percExc = 0.8  # proportion of excitatory neurons in network

    def _neuron_parameters(self):
        self.a_e = 0.001e-6  # adaptation dynamics of e-synapses, S
        self.b_e = 0.04e-9  # adaptation increment of e-synapses, A
        self.a_lst = 0.002e-6
        self.b_lst = 0

        self.a_i = 0.001e-6  # adaptation dynamics of i-synapses, S
        self.b_i = 0  # adaptation increment of i-synapses, A

    def _build_neuron_arrays(self):
        super(Network, self)._build_neuron_arrays()
        # overwrite a and b values for LST-neurons
        perc_lst = 0.05  # percentage of excitatory neurons that have lst like dynamics
        N_lst = int(self.N_e * perc_lst)
        lst_ids = self.exc_ids[0:N_lst]
        self.a[lst_ids] = self.a_lst
        self.b[lst_ids] = self.b_lst

    def _build_connectivity(self):
        n_ee = 32  # number of incoming synapses (from e to e)
        n_ei = 32  # number of incoming synapses (from e to i)
        n_ie = 8  # number of incoming synapses (from i to e)
        n_ii = 8  # number of incoming synapses (from i to i)

        self.A = np.zeros((self.N, self.N))
        pres_ids = np.random.choice(self.exc_ids, (self.N_e, n_ee))
        for pres_no, exc_id in enumerate(self.exc_ids):
            self.A[exc_id, pres_ids[pres_no]] = 1

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
            self.A[inh_id, pres_ids[pres_no]] = 1  # TODO:

        np.fill_diagonal(self.A, 0)  # remove self-loops!!!!
