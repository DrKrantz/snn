import numpy as np


class Network:
    def __init__(self):
        self.N_col = 20
        self.N_row = 20

        self.percExc = 0.5  # proportion of excitatory neurons in network

        self.a_e = 0.04e-6  # adaptation dynamics of e-synapses, S
        self.a_i = 0.08e-6  # adaptation dynamics of i-synapses, S
        self.b_e = 0  # 0.03e-9 # adaptation increment of e-synapses, A
        self.b_i = 0.03e-9  # adaptation increment of i-synapses, A

        self.n_ee = 0  # number of incoming synapses (from e to e)
        self.n_ei = 2  # number of incoming synapses (from e to i)
        self.n_ie = 8  # number of incoming synapses (from i to e)
        self.n_ii = 8  # number of incoming synapses (from i to i)

        self.N = self.N_row * self.N_col
        self.N_e = int(self.N * self.percExc)
        self.N_i = self.N - self.N_e

        ids = np.random.permutation(np.arange(self.N))  # randomize arangement
        self.exc_ids = np.sort(ids[np.arange(self.N_e, dtype=int)])
        self.inh_ids = np.sort(ids[np.arange(self.N_e, self.N, dtype=int)])

        self.a = np.ones(self.N)
        self.a[self.exc_ids] = self.a_e
        self.a[self.inh_ids] = self.a_i
        self.b = np.ones(self.N)
        self.b[self.exc_ids] = self.b_e
        self.b[self.inh_ids] = self.b_i

        self._build_connectivity()

    def _build_connectivity(self):
        self.A = np.zeros((self.N, self.N))
        #  ee is 0

        # exc presynaptic IDs for inh neurons

        print()

        pres_ids = np.random.choice(self.exc_ids, (self.N_i, self.n_ei))
        for pres_no, inh_id in enumerate(self.inh_ids):
            self.A[inh_id, pres_ids[pres_no]] = 1

        # inh presynaptic IDs for exc neurons
        pres_ids = np.random.choice(self.inh_ids, (self.N_e, self.n_ie))
        for pres_no, exc_id in enumerate(self.exc_ids):
            self.A[exc_id, pres_ids[pres_no]] = 1

        # inh presynaptic IDs for inh neurons
        pres_ids = np.random.choice(self.inh_ids, (self.N_i, self.n_ii))
        for pres_no, inh_id in enumerate(self.inh_ids):
            self.A[inh_id, pres_ids[pres_no]] = 1
