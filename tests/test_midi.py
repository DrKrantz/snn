import mido
import time


def cycle(inbetween_pause=0, ncycles=200, **kwargs):
    for k in range(ncycles):
        onoff(**kwargs)
        time.sleep(inbetween_pause)


def onoff(onoff_pause=0, note_pause=0):
    port = mido.open_output('IAC Driver Bus 1')

    onmsg = mido.Message('note_on')
    offmsg = mido.Message('note_off')
    for k in range(127):
        time.sleep(note_pause)
        port.send(offmsg.copy(note=k+1))
        time.sleep(onoff_pause)
        port.send(onmsg.copy(note=k+1))
        time.sleep(note_pause)
    #
    #
    # msg = mido.Message('note_off', note=1)
    # for k in range(127):

