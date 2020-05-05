# Taken from https://healeycodes.com/javascript/python/beginners/webdev/2019/04/11/talking-between-languages.html

from subprocess import Popen, PIPE


recorder = Popen(['python3', 'brunel_delta_nest.py'], stdout=PIPE)
buffer = b''

while True:
    out = recorder.stdout.read(1)

    if out == b'\n':
        if buffer.find(b'\t') > 0:
            neuron, spiketime = buffer.split(b'\t')

            print('Receiving: neuron {} at time {}'.format(
                int(neuron), float(spiketime)))
        else:
            print(str(buffer))
        buffer = b''
    else:
        buffer += out
