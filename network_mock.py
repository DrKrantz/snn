import numpy as np
import time

if __name__ == '__main__':
    from sound_devices import OscPlayer

    rates = np.array([10, 3, 12])  # Hz
    freqs = [140, 440, 620]
    h = 1./1000  # resolution of time, in s
    N = len(rates)

    player = OscPlayer()
    player.init_instrument(freqs)
    time.sleep(1)

    now = time.time()
    while True:
        fired = np.nonzero(np.random.random(N) <= rates*h)[0]
        [player.note_on(int(note)) for note in fired]

        time_to_pause = h - (time.time() - now)
        print(time_to_pause)
        if time_to_pause > 0:
            time.sleep(time_to_pause)
        now = time.time()
