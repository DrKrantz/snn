#!/usr/bin/env python

""" DOCSTRING """

__author__ = "Benjamin Staude"
__email__ = "benjamin.staude@gmail.com"
__date__ = 140801

from numpy import array, intersect1d, unique, union1d

import mido
import sensoryNetwork

from pythonosc.udp_client import SimpleUDPClient


class InputDevice:
    def __init__(self, name):
        self.__messages = []
        self.__inport = mido.open_input(name, False, self.__store_incoming)

    def __store_incoming(self, msg):
        self.__messages.append(msg)

    def update(self):
        content = self.__messages
        self.__messages = []
        return content

'''
class InputDevice(pm.Input):
    def __init__(self, name, n_read=100):
        pm.init()
        self.nread = n_read
        deviceId = self.__getDeviceId(name)

        if deviceId == -1:
            print("SETUP WARNING!!! input: " + name + " not available!!!")
            return
        else:
            super(InputDevice,self).__init__(deviceId)
            print("SETUP input: " + name + " connected with id", deviceId)

    def __getDeviceId(self, name):
        for deviceId in range(pm.get_count()):
            if (pm.get_device_info(deviceId)[1] == name.encode()) & \
                    (pm.get_device_info(deviceId)[2] == 1):
                return deviceId
        return -1

    def getData(self):
        if self.poll():
            data = self.read(self.nread)
            data.reverse()
            return array([dd[0] for dd in data])

    def map_keys(self):
        """  print device's input """
        while True:
            try:
                if self.poll():
                    print(self.read(10))
            except KeyboardInterrupt:
                return

    def update(self, pars):
        """
        the interface-function
        :param pars:
        :return:
        """
        return {'fired': [], 'pars': {}}


class BCF(InputDevice):
    NAME = b'Virtual BCF2000'

    def __init__(self, midiport, pars):
        super(BCF, self).__init__(midiport)
        self.pars = pars

    def update(self, pars):
        self.pars = pars
        MIDI_data = self.getData()
        if MIDI_data is not None:
            key_data = MIDI_data[MIDI_data[:, 0] == self.pars['midistat_keys'], :]
            if key_data.__len__() > 0 and self.pars['midistat_keys'] is not None:
                key_data_on = key_data[key_data[:, 2] > 0, :]  # take only "note on"
                if key_data_on.__len__() > 0:
                    # maps the key inputs to external inputs to specific notes (1-to-1)
                    """  TO BE RE-IMPLEMENTED
                    key_ids_ext =
                        intersect1d(unique(key_data_on[:,1]), self.pars['key_ids_ext'])
                    v[note2neuron(key_ids_ext)] = self.pars['threshold']
                    """
                    # this maps key inputs to changes in parameters and external inputs
                    # i.e. gradual up/down changes
                    key_ids_pars = intersect1d(
                        unique(key_data_on[:, 1]),
                        self.pars['key_ids_pars']
                    )
                    self.__MIDI2pars(key_data, key_ids_pars, 'keys')

            # extract data from sliders
            slide_data = MIDI_data[MIDI_data[:, 0] == self.pars['midistat_slide'], :]
            slide_ids_ext = intersect1d(unique(slide_data[:, 1]),
                                        self.pars['slide_ids_ext'])
            if slide_ids_ext.__len__() > 0:
                self.__MIDI2external(slide_data,slide_ids_ext, 'slide')

            slide_ids_pars = intersect1d(unique(slide_data[:, 1]),
                                         self.pars['slide_ids_pars'])
            if slide_ids_pars.__len__() > 0:
                self.__MIDI2pars(slide_data, slide_ids_pars, 'slide')
        return {'pars': self.pars, 'fired': []}

    def __MIDI2pars(self, MIDI_data, in_ids, in_type):
        # convert the MIDI-input into parameter values
        ids = list(unique(MIDI_data[:, 1]))
        if in_type=='slide':
            for id in in_ids:
                param = \
                    self.pars['slide_action_pars'][self.pars['slide_ids_pars'].index(id)]

                self.pars[param] = \
                    self.pars[param+'_def'] + \
                    self.pars[param+'_step'] * MIDI_data[ids.index(id), 2]
        elif in_type == 'keys':
            for id in in_ids:
                parid = self.pars['key_action_pars'][self.pars['key_ids_pars'].index(id)]
                if parid == 0:
                    self.pars['s_e'] += \
                        -self.pars['s_e_step'] *\
                         (self.pars['s_e'] > self.pars['s_e_range'][0])
                if parid == 1:
                    self.pars['s_e'] += \
                        self.pars['s_e_step'] *\
                        (self.pars['s_e'] < self.pars['s_e_range'][1])
                if parid == 2:
                    self.pars['s_i'] += \
                        -self.pars['s_i_step'] *\
                        (self.pars['s_i'] > self.pars['s_i_range'][0])
                if parid == 3:
                    self.pars['s_i'] += \
                        self.pars['s_i_step'] *\
                        (self.pars['s_i'] < self.pars['s_i_range'][1])
                if parid == 4:
                    self.pars['tau_e'] += \
                        -self.pars['tau_e_step'] * \
                        (self.pars['tau_e'] >
                         self.pars['tau_e_range'][0])
                if parid == 5:
                    self.pars['tau_e'] += \
                        self.pars['tau_e_step'] * \
                            (self.pars['tau_e'] <
                             self.pars['tau_e_range'][1])
                if parid == 6:
                    self.pars['tau_i'] += \
                        -self.pars['tau_i_step'] * \
                        (self.pars['tau_i'] >
                         self.pars['tau_i_range'][0])
                if parid == 7:
                    self.pars['tau_i'] += \
                        self.pars['tau_i_step'] * \
                        (self.pars['tau_i'] < self.pars['tau_i_range'][1])

    def __MIDI2external(self, MIDI_data, in_ids, in_type):
        # convert the MIDI-input to the external input to the neurons
        ids = list(unique(MIDI_data[:, 1]))
        if in_type == 'slide':
            for id in in_ids:
                action = \
                    self.pars['slide_action_ext'][self.pars['slide_ids_ext'].index(id)]
                value = self.pars['ext_step'] * MIDI_data[ids.index(id), 2]/127
                #print action, value
                if action == 0:
                    #print value
                    self.pars['midi_ext_e'] = value
                    self.pars['midi_ext_i'] = value
                    self.pars['midi_external'][:] = value
                elif action == 1:
                    #print value
                    self.pars['midi_ext_e'] = value
                    self.pars['midi_external'][self.pars['Exc_ids']] = \
                        self.pars['midi_ext_e']
                elif action == 2:
                    #print value
                    self.pars['midi_ext_i'] = value
                    self.pars['midi_external'][self.pars['Inh_ids']] = \
                        self.pars['midi_ext_i']
                elif action == 3:
                    #print value
                    self.pars['midi_external'][[0, 4, 9, 14, 19]] = value
                elif action == 4:
                    #print value
                    self.pars['midi_external'][[24, 29, 34, 39]] = value
        elif in_type == 'keys':
            for id in in_ids:
                parid = self.pars['key_action_ext'][self.pars['key_ids_pars'].index(id)]
                if parid == 0:
                    self.pars['midi_external'] += -self.pars['ext_step']
                if parid == 1:
                    self.pars['midi_external'] += self.pars['ext_step']
                if parid == 2:
                    self.pars['midi_external'][self.pars['Exc_ids']] += \
                        -self.pars['ext_step']
                if parid == 3:
                    self.pars['midi_external'][self.pars['Exc_ids']] += \
                        self.pars['ext_step']
                if parid == 4:
                    self.pars['midi_external'][self.pars['Inh_ids']] = \
                        -self.pars['ext_step']
                if parid == 5:
                    self.pars['midi_external'][self.pars['Inh_ids']] += \
                        self.pars['ext_step']

'''


class KeyboardInput:
    def __init__(self, *args):
        self.triggered = array([], int)

    def update(self, pars):
        fired = self.triggered
        self.triggered = array([], int)
        return {'pars': pars, 'fired': fired}

    def triggerSpike(self, key):
        self.triggered = union1d(self.triggered, array([key], int))

"""
class SensoryObject(InputDevice):
    NAME = 'USB MIDI Device'

    def __init__(self, midiport, pars):
        super(SensoryObject, self).__init__(self.midiport)
        self.pars = pars

    def update(self, pars):
        self.pars = pars
        MIDI_data = self.getData()
        fired = []
        if MIDI_data is not None:
            [fired.append(dd[1]) for dd in MIDI_data]
            print('object:', fired)
        return {'pars': self.pars, 'fired': array(fired, int)}
"""

if __name__ == '__main__':
    import Dunkel_pars
    inputDevice = SensoryObject(Dunkel_pars.parameters(), '')
    inputDevice.map_keys()
