#!/usr/bin/env python

""" Matplotlib-display for membrane potentials"""

__author__ = "Benjamin Staude"
__email__ = "benjamin.staude@gmail.com"
__date__ = 140620


import matplotlib
matplotlib.use('TkAgg') # do this before importing pylab
import matplotlib.pyplot as plt
import numpy as np
from Dunkel_pars import parameters
from Dunkel_functions import *


class Membrane_Display:
    def __init__(self, N, vrange=[0, 1]):
        plt.rcParams['backend'] = 'macosx'
        plt.rcParams['interactive'] = 'True'

        self.vrange = np.array(vrange)
        #print self.vrange
        self.N = N
        self.nsteps = 100
        #normv = (v-self.vrange[0])/diff(self.vrange)[0]+arange((self.N)-diff(self.vrange)[0]/2)
        #startv = vstack((normv,normv))# resize(normv,[self.nsteps,self.N])
        normv = np.zeros((self.nsteps))
        startv = normv
        for k in range(self.N-1):
            startv = np.vstack((startv, normv + k + 1))
        self.fh = plt.figure()   # figure handle
        self.lines = plt.plot(np.transpose(startv))
        plt.ylim(0, self.N)
        plt.xlim(0, self.nsteps)
        plt.draw()
        #pl.show()
    def update(self,v):
        normv = (v-self.vrange[0])/np.diff(self.vrange)+np.arange(self.N)
        for k in range(self.N):
            ndata = [self.lines[k].get_ydata()[idx] for idx in range(1,self.nsteps)]
            ndata.append(normv[k])
            self.lines[k].set_ydata(array(ndata))
        plt.draw()
    def test(self,nrep=100):
        for k in range(nrep):
            v = np.random.rand(self.N)
            self.update(v)

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
        print 'moved'
        self.line.figure.show()