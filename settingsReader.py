#!/usr/bin/env python

""" read the settings-file """

__author__ = "Benjamin Staude"
__email__ = "benjamin.staude@gmail.com"
__date__ = 140620

import csv

class SettingsReader:
    def __init__(self, filename='settings.csv'):
        self.devices = {'inputs': {}, 'outputs': {}}
        self.filename = filename
        if self.filename == '':
            import fileSelector
            selector = fileSelector.FileSelector(self.setFilename)
            selector.mainloop()
        self.readSettings(self.filename)

    def getDevices(self):
        return self.devices

    def setFilename(self, filename):
        self.filename = filename

    def readSettings(self, filename):
        if filename[-3::] != 'csv':
            print('wrong file type: ' + filename[-3::])
            return

        with open(self.filename, 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')

            category = 'inputs'
            for row in csvreader:
                if row[0][0] != '#':
                    if row[0] == 'INPUTS':
                        category = 'inputs'
                    elif row[0] == 'OUTPUTS':
                        category = 'outputs'
                    else:
                        self.devices[category][row[0]] = row[1].strip()


if __name__=='__main__':
    reader = SettingsReader()
    print(reader.devices)
