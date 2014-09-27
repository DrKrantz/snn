#!/usr/bin/env python

""" read the settings-file """

__author__ = "Benjamin Staude"
__email__ = "benjamin.staude@gmail.com"
__date__ = 140620

import csv

class SettingsReader:
    def __init__(self, filename = 'settings.csv'):
        self.devices = {'inputs':{}, 'outputs':{}}
        with open(filename, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')

            category = 'inputs'
            for row in reader:
                if row[0] == 'INPUTS':
                    category = 'inputs'
                elif row[0] == 'OUTPUTS':
                    category = 'outputs'
                else:
                    self.devices[category][row[0]] = row[1]


if __name__=='__main__':
    reader = SettingsReader()
    print reader.devices
