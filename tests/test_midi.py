import mido
import time
import threading as th


port = mido.open_output('IAC Driver Bus 1')


def turnalloff():
    offmsg = mido.Message('note_off')
    for k in range(127):
        port.send(offmsg.copy(note=k+1))


def cycle(inbetween_pause=0, ncycles=200, **kwargs):
    for k in range(ncycles):
        onoff(**kwargs)
        time.sleep(inbetween_pause/1000)
    turnalloff()


def onoff(onoff_pause=0, note_pause=0):
    for k in range(127):
        port.send(mido.Message('note_off', note=k+1))
        time.sleep(onoff_pause/1000)
        port.send(mido.Message('note_on', note=k+1))
        time.sleep(note_pause/1000)


def threaded_cycle(inbetween_pause=0, ncycles=200, **kwargs):
    for k in range(ncycles):
        threaded_onoff(**kwargs)
        time.sleep(inbetween_pause/1000)
    # turnalloff()


def threaded_onoff(onoff_pause=0, note_pause=0, start=0, end=127):
    timer = list(range(end-start))
    for k in range(start, end):
        port.send(mido.Message('note_on', note=k+1))
        # timer[k-start] = th.Timer(onoff_pause/1000, lambda: port.send(mido.Message('note_off', note=k+1)))
        # timer[k-start].start()
        time.sleep(note_pause/1000)

    th.Timer(onoff_pause/1000, lambda: turnalloff()).start()
