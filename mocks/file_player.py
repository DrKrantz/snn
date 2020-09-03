import csv
import time
import os
import glob
import numpy as np
import struct
from output import sockets


def load_spike_file(model_node):
    times = []
    neurons = []
    for file in glob.glob(os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                       'data/{}-[0-9].dat'.format(model_node))):

        print('Reading %s ' % file)
        with open(file, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')
            for row in reader:
                # skip first three rows
                if row[0][0] not in ['#', 's']:
                    neurons.append(int(row[0]))
                    times.append(float(row[1]))

    # nest does not write the times in chronological order, hence sorting is necessary
    indices = np.argsort(times)
    times = np.array(times)[indices]
    neurons = np.array(neurons)[indices]

    return neurons.tolist(), times.tolist()


class FilePlayer:
    def __init__(self, model_node, init_socket, sim_to_real=1, time_to_start=0):
        """
        :param model_node: the name of the file to use.  See
        https://nest-simulator-sg.readthedocs.io/en/latest/guides/parallel_computing.html?highlight=parallel#device-distribution
        for documentation
        :param target_address:
        :param sim_to_real:
        :param time_to_start:
        """
        self.neurons, sim_times = load_spike_file(model_node)
        self.target_address = init_socket.target_address
        self.socket = init_socket

        # sim_to_real second in simulation time corresponds to 1 second in real time
        self.times = list((np.array(sim_times) - time_to_start) / sim_to_real)

    def send_init(self):
        self.socket.send_init()

    def play(self):
        start_time = time.time()

        next_time = self.times.pop(0)
        while len(self.neurons) >= 1:
            time_passed = time.time() - start_time
            if time_passed >= next_time:
                neuron = self.neurons.pop(0)
                print('sending %s' % neuron)
                self.socket.sendto(struct.pack('<bH', sockets.MESSAGETYPE_PERFORMANCE, neuron), self.target_address)
                next_time = self.times.pop(0)
