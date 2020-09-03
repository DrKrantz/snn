#!/usr/bin/env python

import music
import sys
from itertools import takewhile


setup = music.Setup()
stoptime = setup.config("stoptime")
timestep = setup.config("timestep")
buf = setup.config("buffer")

errorAt = setup.config("errorAt")
if errorAt < 0:
    errorAt = None

comm = setup.comm
rank = comm.Get_rank()
size = comm.Get_size()

inp = setup.publishEventInput("in")
out = setup.publishEventOutput("out")

width = inp.width()
local = width // size
rest = width % size
firstId = rank * local

# distribute the rest:
firstId += min(rank, rest)
if rank < rest:
    local += 1


the_list = []


def eventerr(d):
    if errorAt is None: return
    if d >= errorAt:
        raise RuntimeError("Hey")


time = None


def eventfunc(d, t, i):
    eventerr(d)
    the_list.append(i+10)
    sys.stderr.write("Translating rank {}: Event ({}, {}) at {}\n".
                     format(rank, i, d, time))


inp.map(eventfunc,
        music.Index.GLOBAL,
        base=firstId,
        size=local,
        maxBuffered=buf)

out.map(music.Index.GLOBAL,
        base=firstId,
        size=local,
        maxBuffered=buf)

runtime = music.Runtime(setup, timestep)
times = takewhile(lambda t: t <= stoptime, runtime)
for time in times:
    if len(the_list) > 0:
        sys.stderr.write('list has')
        # [out.insertEvent(1, k, music.Index.GLOBAL) for k in the_list]
        the_list = []
