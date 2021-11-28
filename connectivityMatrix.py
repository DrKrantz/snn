#!/usr/bin/env python

""" connectivityMatrix.py: DOCSTRING """

__author__ = "Benjamin Staude"
__email__ = "benjamin.staude@gmail.com"
__date__ = 140620

import random
import numpy as np

from Dunkel_functions import *


class ConnectivityMatrix(object):
    def __init__(self, connect_type='random', pars=parameters()):

        if connect_type == 'random':
            ee = (np.random.rand(pars['Ne'], pars['Ne']) < pars['p_ee'])
            ei = (np.random.rand(pars['Ne'], pars['Ni']) < pars['p_ei'])
            ii = (np.random.rand(pars['Ni'], pars['Ni']) < pars['p_ii'])
            ie = (np.random.rand(pars['Ni'], pars['Ne']) < pars['p_ie'])
            self.A = np.vstack((np.hstack((ee, ei)), np.hstack((ie, ii))))
            self.A[list(range(pars['Ne'] + pars['Ni'])), list(range(pars['Ne'] + pars['Ni']))] = 0  # remove selfloops

        elif connect_type == 'none':
            self.A = np.zeros((pars['N'], pars['N']))  # no connectivity

        elif connect_type == 'uni_torus':  # torus with uniform connectivity profile
            self.A = np.zeros((pars['N'], pars['N']))

            # construct matrix of pairwise distance
            distMat = np.zeros((pars['N'], pars['N']))
            for n1 in range(pars['N']):
                coord1 = linear2grid(n1, pars['N_col'])
                for n2 in np.arange(n1 + 1, pars['N']):
                    coord2 = linear2grid(n2, pars['N_col']) - coord1  # this sets neuron n1 to the origin
                    distMat[n1, n2] = toric_length(coord2, pars['N_row'], pars['N_col'])
            distMat = distMat + distMat.transpose()

            # construct adjajency matrix
            for n1 in range(pars['N']):
                neighbor_ids = np.nonzero(distMat[:, n1] < pars['sigma_con'])[0]
                random.shuffle(neighbor_ids)
                idx = neighbor_ids[0:min([pars['ncon'], len(neighbor_ids)])]
                self.A[idx, n1] = 1

        elif connect_type == 'destexhe':
            self.A = np.zeros((pars['N'], pars['N']))
            #  ee is 0

            # exc presynaptic IDs for inh neurons
            pres_ids = np.random.choice(pars['Exc_ids'], (pars['Ni'], pars['n_ei']))
            for pres_no, inh_id in enumerate(pars['Inh_ids']):
                self.A[inh_id, pres_ids[pres_no]] = 1

            # inh presynaptic IDs for exc neurons
            pres_ids = np.random.choice(pars['Inh_ids'], (pars['Ne'], pars['n_ie']))
            for pres_no, exc_id in enumerate(pars['Exc_ids']):
                self.A[exc_id, pres_ids[pres_no]] = 1

            # inh presynaptic IDs for inh neurons
            pres_ids = np.random.choice(pars['Inh_ids'], (pars['Ni'], pars['n_ii']))
            for pres_no, inh_id in enumerate(pars['Inh_ids']):
                self.A[inh_id, pres_ids[pres_no]] = 1

        else:
            print("type " + connect_type + " not yet implemented")

    def get(self):
        return self.A
