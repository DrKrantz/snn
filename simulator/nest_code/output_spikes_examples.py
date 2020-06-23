import nest

neuron = nest.Create("iaf_psc_alpha")
noise = nest.Create("poisson_generator", 2)
spikedetector = nest.Create("spike_detector")

nest.SetStatus(noise, [{"rate": 80000.0}, {"rate": 15000.0}])
nest.SetStatus(spikedetector, {"withgid": True, "withtime": True, "to_file": True})

nest.Connect(noise, neuron, syn_spec={'weight': [[1.2, -1.0]], 'delay': 1.0})
nest.Connect(neuron, spikedetector)

nest.Simulate(1000.0)