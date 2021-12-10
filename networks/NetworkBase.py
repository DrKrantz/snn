import numpy as np


class NetworkBase:
    def __init__(self):
        self._network_parameters()
        self.__build_network_arrays()
        self._neuron_parameters()
        self.__build_neuron_arrays()
        self._connectivity_parameters()
        self._build_connectivity()

    def _neuron_parameters(self):
        self.a_e = 0  # adaptation dynamics of e-synapses, S
        self.a_i = 0  # adaptation dynamics of i-synapses, S
        self.b_e = 0  # 0.03e-9 # adaptation increment of e-synapses, A
        self.b_i = 0  # adaptation increment of i-synapses, A

    def __build_neuron_arrays(self):
        self.a = np.ones(self.N)
        self.a[self.exc_ids] = self.a_e
        self.a[self.inh_ids] = self.a_i
        self.b = np.ones(self.N)
        self.b[self.exc_ids] = self.b_e
        self.b[self.inh_ids] = self.b_i

    def _network_parameters(self):
        self.N_row = 10
        self.N_col = 10
        self.percExc = 0.5  # proportion of excitatory neurons in network

    def __build_network_arrays(self):
        self.N = self.N_row * self.N_col
        self.N_e = int(self.N * self.percExc)
        self.N_i = self.N - self.N_e
        ids = np.random.permutation(np.arange(self.N))  # randomize arangement
        self.exc_ids = np.sort(ids[np.arange(self.N_e, dtype=int)])
        self.inh_ids = np.sort(ids[np.arange(self.N_e, self.N, dtype=int)])

    def _connectivity_parameters(self):
        pass

    def _build_connectivity(self):
        pass
