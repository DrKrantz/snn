import time
import numpy as np


class NetworkMock:
    MAX_RESOLUTION = 0.001
    """
    generates a binomial process with len(rates) neurons and sends spikes via OSC to the instrument
    """
    def __init__(self, client, rates, res=0.1, sim_time=None):
        self.__client = client
        self.__rates = rates
        self.__resS = res  # temporal resolution of simulation in seconds
        self.__sim_time = sim_time  # time to simulate. If set to None, simulation does not end

        self.__probs = rates * res  # probability for an event per time window
        self.__n = len(rates)
        self.__dur = 0
        self.__start_time = 0

    def __continue_simulation(self):
        if self.__sim_time is not None and self.__dur >= self.__sim_time:
            return False
        else:
            return True

    def run(self):
        now = time.time()
        self.__start_time = now
        while self.__continue_simulation():
            numbers = np.random.rand(self.__n)
            ids = (numbers < self.__probs).nonzero()[0].tolist()

            while time.time() - now < self.__resS:
                time.sleep(self.MAX_RESOLUTION)

            now = time.time()

            self.__dur = now - self.__start_time

            if ids:
                # print('Network-Mock sending: {} at t={}'.format(ids, self.__dur))
                self.__client.send_to_default(ids)
