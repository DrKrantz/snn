import csv
import time
import numpy as np


def load_gdf(file):
    times = []
    neurons = []
    with open(file, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for row in reader:
            neurons.append(int(row[0]))
            times.append(float(row[1]))
    return neurons, times


class FilePlayer:
    def __init__(self, filename, spike_socket, sim_to_real=1, time_to_start=0):
        self.neurons, sim_times = load_gdf(filename)
        self.spike_socket = spike_socket

        # sim_to_real second in simulation time corresponds to 1 second in real time
        self.times = list((np.array(sim_times) - time_to_start) / sim_to_real)

    def get_neuron_ids(self):
        return np.unique(self.neurons)

    def play(self):
        start_time = time.time()

        next_time = self.times.pop(0)
        while len(self.neurons) >= 1:
            time_passed = time.time() - start_time
            if time_passed >= next_time:
                neuron = self.neurons.pop(0)
                print('sending %s' % neuron)
                self.spike_socket.send_converted(neuron)
                next_time = self.times.pop(0)
