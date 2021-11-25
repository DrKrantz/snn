#!/usr/bin/env python

""" Matplotlib-display for membrane potentials"""

__author__ = "Benjamin Staude"
__email__ = "benjamin.staude@gmail.com"
__date__ = 140620


import matplotlib
matplotlib.use('Qt5Agg') # do this before importing pylab
import matplotlib.pyplot as plt
import numpy as np
import pickle


class Membrane_Display:
    size = (5, 10)

    def __init__(self, N, vrange):
        print(vrange)
        plt.rcParams['backend'] = 'Qt5Agg'
        plt.rcParams['interactive'] = 'True'

        self.vrange = np.array(vrange)
        self.N = N
        self.nsteps = 100
        normv = np.zeros((self.nsteps))
        startv = normv
        for k in range(self.N-1):
            startv = np.vstack((startv, normv + k + 1))
        self.fh = plt.figure(figsize=self.size)   # figure handle/
        self.lines = plt.plot(np.transpose(startv))
        plt.ylim(0, self.N)
        plt.xlim(0, self.nsteps)
        plt.draw()
        plt.show()

    def update(self, v):
        # plt.pause(0.01)
        normv = (v-self.vrange[0])/np.diff(self.vrange)+np.arange(self.N)
        for k in range(self.N):
            ydata = np.append(self.lines[k].get_ydata()[1:self.nsteps], normv[k])
            self.lines[k].set_ydata(np.array(ydata))
        plt.draw()

    def plot(self, v_mat):
        normv = (v_mat[0:self.N, :] - self.vrange[0]) / np.diff(self.vrange)
        startv = np.zeros_like(normv)
        for k in range(self.N-1):
            startv[k, :] = normv[k+1, :] + k+1

        self.fh.clf()
        self.lines = plt.plot(np.arange(startv.shape[1])/10, startv.T)  # TODO read proper resolution
        plt.draw()

    def test(self, nrep=100):
        for k in range(nrep):
            v = np.random.rand(self.N)
            self.update(v)
            plt.pause(0.001)


class MembraneDisplay:
    def __init__(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
#        win = self.fig.canvas.manager.window
#        self.fig.canvas.manager.window.after(100, self.start)
        self.x = np.arange(0, 2*np.pi, 0.01)        # x-array
        self.line, = self.ax.plot(self.x, np.sin(self.x))
        self.line.figure.show()
        self.__i = 0

    def start(self):
        for i in np.arange(1,200):
            self.move()
#        self.animate()

    def move(self):
        self.__i += 1
        self.line.set_ydata(np.sin(self.x+self.__i/10.0))          # update the data
        self.fig.canvas.draw()                        # redraw the canvas
        print('moved')
        self.line.figure.show()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', action='store_true', dest='test')
    args = parser.parse_args()

    with open('data/v_rec.pkl', 'rb') as f:
        v_loaded = np.array(pickle.load(f))
    n_display = 20

    display = Membrane_Display(n_display, vrange=[np.min(v_loaded), np.max(v_loaded)])
    while True:
        input('Press enter to refresh')
        with open('data/v_rec.pkl', 'rb') as f:
            v_loaded = np.array(pickle.load(f))
        display.plot(v_loaded)
