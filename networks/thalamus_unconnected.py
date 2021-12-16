import numpy as np
from networks.thalamus import Network as TlmNetwork


class Network(TlmNetwork):
    def __init__(self):
        super(Network, self).__init__()

    def _build_connectivity(self):
        self.A = np.zeros((self.N, self.N))
