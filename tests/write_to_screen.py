import time
import math
import sys

counter = 0
start = time.time()

print("-------Starting Network Simulation-------")
print('{}\t{}\n'.format(counter, time.time() - start))

while True:
    seconds_passed = math.floor(time.time()-start)
    if seconds_passed == counter:
        pass
    else:
        counter += 1
        print('{}\t{}\n'.format(counter, time.time()-start))
        sys.stdout.flush()
