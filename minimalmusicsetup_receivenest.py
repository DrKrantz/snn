#!/usr/bin/python

import nest
#
# nest.sli_run('statusdict/have_music ::')
# if not nest.spp():
#     import sys
#
#     print("NEST was not compiled with support for MUSIC, not running.")
#     sys.exit()

nest.set_verbosity("M_ERROR")

meip = nest.Create('music_event_in_proxy')
nest.SetStatus(meip, {'port_name': 'spikes_in', 'music_channel': 0})

n = nest.Create('iaf_psc_alpha')

nest.Connect(meip, n, 'one_to_one', {'weight': 750.0})

vm = nest.Create('voltmeter')
nest.SetStatus(vm, {'to_memory': False, 'to_screen': True})

nest.Connect(vm, n)

nest.Simulate(10)
