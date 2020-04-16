# Taken from https://healeycodes.com/javascript/python/beginners/webdev/2019/04/11/talking-between-languages.html


import sys
from subprocess import Popen, PIPE


temperatures = []  # store temperatures
recorder = Popen(['python', 'simulator-to-terminal.py'], stdout=PIPE)
buffer = b''

while True:
    out = recorder.stdout.read(1)

    if out == b'\n':
        spiketime, neuron = buffer.split(b' ')
        print('Receiving: neuron {} at time {}'.format(
            int(neuron), float(spiketime)))
        buffer = b''
    else:
        buffer += out
