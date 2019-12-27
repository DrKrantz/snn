frequencies = {
    'C1': 32.70,
    'C#1': 34.65,
    'D1': 36.71,
    'D#1': 38.89,
    'E1': 41.20,
    'F1': 43.65,
    'F#1': 46.25,
    'G1': 49.00,
    'G#1': 51.91,
    'A1': 55.00,
    'A#1': 58.27,
    'B1': 61.74
}


def get_octaves(n_oct=3, start_oct=1):
    freqs = []
    for f in frequencies.values():
        for mult in range(n_oct):
            freqs.append((mult+start_oct+1)*f)
    return sorted(freqs)
