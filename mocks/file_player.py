import csv
import time
import numpy as np
import socket
import struct
from output import sockets


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
    def __init__(self, filename, target_address, sim_to_real=1, time_to_start=0):
        self.neurons, sim_times = load_gdf(filename)
        self.target_address = target_address
        self.spike_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # sim_to_real second in simulation time corresponds to 1 second in real time
        self.times = list((np.array(sim_times) - time_to_start) / sim_to_real)

    def send_init(self):
        neuron_ids = np.unique(self.neurons)
        self.spike_socket.sendto(struct.pack('HH', sockets.MESSAGETYPE_TOTAL_NEURONS, len(neuron_ids)), self.target_address)
        for idx, n_id in enumerate(neuron_ids):
            self.spike_socket.sendto(struct.pack('HH', sockets.MESSAGETYPE_INIT_FORWARDER, n_id), self.target_address)

    def play(self):
        start_time = time.time()

        next_time = self.times.pop(0)
        while len(self.neurons) >= 1:
            time_passed = time.time() - start_time
            if time_passed >= next_time:
                neuron = self.neurons.pop(0)
                print('sending %s' % neuron)
                self.spike_socket.sendto(struct.pack('HH', sockets.MESSAGETYPE_PERFORMANCE, neuron), self.target_address)
                next_time = self.times.pop(0)
