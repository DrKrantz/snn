import numpy as np
import time

if __name__ == '__main__':
    from output.output_devices import OscDevice
    from config import frequencies
    freqs = frequencies.get_octaves(n_oct=2, start_oct=4)

    # freqs = [140, 210, 250, 330, 400, 440, 620, 700, 800, 880, 900]
    N = len(freqs)
    rates = 3 + np.random.random(N) * 15
    h = 1./1000  # resolution of time, in s

    player = OscDevice()
    player.init_instrument(freqs)
    time.sleep(1)

    now = time.time()
    while True:
        fired = np.nonzero(np.random.random(N) <= rates*h)[0]
        [player.update('uwe', int(note)) for note in fired]

        time_to_pause = h - (time.time() - now)
        if time_to_pause > 0:
            time.sleep(time_to_pause)
        now = time.time()
