import threading
import time
import random

isi = 1
N = 10
t = 0

def printer(spiketime, neuron):
    print(spiketime, neuron)


now = time.time()

while True:
    if time.time() - now > isi:
        now = time.time()
        neuron_id = random.randint(1, N)
        # threading.Timer(isi, printer, neuron_id, t)
        print(now, neuron_id, flush=True, end='\n')

