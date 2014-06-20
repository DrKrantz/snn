'''

THIS SCRIPT CONSTAINS THE PARMETERS NEEDED FOR SNESORYNETWORK.PY

Benjamin Staude, Berlin, July 2010
'''


from numpy import *
from scipy import *


##################    DEFINE THE DEFAULT PARAMETERS  #########################
def parameters():
    pars = dict()
    # The connectivity of the torus demands square grid!
    pars['N_col'] = 20 #pars['N_col'] = int(ceil(sqrt(pars['N'])/10)*10)
    pars['N_row'] = pars['N_col'] #    pars['N_row'] = pars['N']/pars['N_col']
    pars['ex/in'] = 4
    pars['N'] = pars['N_col']*pars['N_row']
    pars['Ni'] =pars['N']/pars['ex/in'] # size of excit. population                
    pars['Ne'] =pars['N'] - pars['Ni']  # size of inh. population
    pars['Ts'] = 1000 # total simulation time in secs
    pars['h'] = 1e-3# resolution of simulation in s
    ids = random.permutation(arange((pars['N']))) # randomize arangement
    pars['Exc_ids']=sort(ids[arange(pars['Ne'])]) # hence the INDICES of the neurons run from 0 to N-1!!!!!!!
    pars['Inh_ids']=sort(ids[pars['Ne']+arange(pars['Ni'])])
    
    # parameters of the neuron model
    pars['threshold'] = -50e-3 #firing threshold of individual neurons, V
    pars['Cm'] = 1e-6 # membrane capacitance, F/cm2
    pars['gL'] = 0.05e-3 # leak conductances, S/cm2
    pars['EL'] = -60e-3 # resting potential = reset after spike, V
    pars['Delta'] = 2.5e-3 # steepness of exponential, V
    pars['S'] = 20000e-8 # membrane area, cm2
    pars['a_e'] = 0#0.08e-6 # adaptation dynamics of e-synapses, S
    pars['a_i'] = 0#0.04e-6 # adaptation dynamics of i-synapses, S
    pars['b_e'] = 0#0.03e-9 # adaptation increment of e-synapses, A
    pars['b_i'] = 0#0e-9 # adaptation increment of i-synapses, A
    pars['dead']=2.5e-3 # deadtime

    # Parameters of Synapses 
    pars['s_e_range']=(1e-11,1e-8) #the allowed range of s_e values
    pars['s_e_step']=diff(pars['s_e_range'])[0]/127 #additive increase of s_e when pressing the corresonding  button 
    pars['s_e'] = 6e-10 # increment of excitatory synaptic conductance per spike, S, 
    pars['s_e_def'] = pars['s_e_range'][0] # the default value...
    
    pars['s_i_range']=(1e-11,1e-8)
    pars['s_i_step']=diff(pars['s_i_range'])[0]/127
    pars['s_i'] = 67e-10  # increment of inhibitory synaptic conductance S per spike
    pars['s_i_def'] = pars['s_i_range'][0]
    
    pars['tau_e_range'] = (5e-5,5e-2)
    pars['tau_e_step'] = diff(pars['tau_e_range'])[0]/127
    pars['tau_e'] = 5e-3 #sec,
    pars['tau_e_def'] = pars['tau_e_range'][0]

    pars['tau_i_range'] = (5e-5,5e-2)
    pars['tau_i_step'] = diff(pars['tau_i_range'])[0]/127
    pars['tau_i'] = 10e-3 #sec
    pars['tau_i_def'] = pars['tau_i_range'][0]

    pars['tau_w'] = 600e-3# time-constant of adaptation variable, sec
    pars['Ee'] = 0e-3 #reversal potential of excitatory synapses, V
    pars['Ei'] = -80e-3 #reversal potential of inhibitory synapses, V

    ''' Connectivity parameters '''
    pars['p_ee'] = 0.1 # probability of e->e connections
    pars['p_ei'] = 0.1 # probability of i->e connections
    pars['p_ie'] = 0.1 # probability of e->i connections
    pars['p_ii'] = 0.1 # probability of e->i connections
    pars['ncon'] = 30
    pars['sigma_con'] = double(pars['N_col'])/4
    # parameters of external drive in the beginning phase of the simulation
    pars['p_ext'] = 0 # probability for a neuron to receive external stimulation
    pars['extrate'] = 0#20 # Rate of stimulation, Hz
    pars['stimdur'] = pars['Ts']#0.1 # duration of stimulation
    
    ''' parameters of membrane potential display '''
    pars['v_disp'] = 0 # 0: off; 1: on
    pars['v_range'] = [pars['EL'], -30e-3]
    pars['v_show_ids']=hstack((pars['Exc_ids'][0:5],pars['Inh_ids'][0:5])) # size of the dots for each neuron

    ''' parameters of WEBCAM stimuluation generation '''
    pars['cam_flux']=10 # if subsequent webcam pixels (in time) deviate further than this value, the difference will be treated as  signal
    pars['diff_min']=10
    pars['diff_max'] = 100
    pars['cam_external_range']=[0, 1e-5] #the range of external drive that the webcam can generate 
    pars['cam_external_max']=1e-5 #the maximum of the camera-drive
    pars['cam_external_max_def']=pars['cam_external_max']
    pars['cam_thres']=1e-7
    pars['cam_ext_start']=0
    pars['cam_ext']=pars['cam_ext_start']

    ''' parameters of MIDI stimulation generation '''
    pars['pause'] = 0
    pars['n_read'] = 100 # buffersize to be read from the input in each simulation step
    pars['velocity'] = 64 
    pars['note_add'] = 36
    pars['midi_external'] = zeros((pars['N']))
    pars['midi_ext_e'] = 0; #external drive to excitatory population
    pars['midi_ext_i'] = 0; #external drive to inhibitory population
    pars['note_ids'] = arange(pars['N'])# the neurons that are played
    pars['midi_per_sec'] = 5 # maximal number of midi-sounds o be sent to Qlab per sec

    pars['ext_step'] = 0.25e-5
    pars['tau_ext'] = 1e-2 # if external drive should be exponentiallt decaying
    
    # parameters of conciousness 
    pars['N_concious'] = 10 # the numbers of synchronous neurons to generate 'concious' events
    
    pars['midi_spikepitch'] = range(64,107) 
    pars['midi_spikeneuron'] = range(64,107)
    
    keys = 'virtual'
    if keys=='home': #my home-configuration
        pars['midistat_keys'] = 146 # the MIDI status that identifies keys (black and white)
        pars['key_ids_ext'] = range(36,85) # the 0-octave keyboard notes
        pars['key_ids_pars'] = array((),int)
        pars['key_action_pars'] = array((),int)
        pars['midistat_slide'] = 178 # the MIDI status that identifies sliders
        pars['slide_ids_pars'] = [71,5, 84,7] # these IDs control parameters
        pars['slide_action_pars'] = ['s_e','s_i','tau_e','tau_i']
        pars['slide_action_ext'] =        [0,  1,  2,  3,  4] # the actions corresponding to the slide_ids
            # 0: input to all neurons
            # 1: input to excitatory neurons (ids 1:pars['Ne'])
            # 2: input to inhibitory neurons (ids pars['Ne']+0:pars['Ni'])
            # 3: input to ids [0 4 9 14 19]
            # 4: input to ids [24 29 34 39]
        pars['slide_ids_ext'] = [73, 72, 91, 93, 74]# MIDI controllers that control external input
    elif keys=='virtual': # the BCF2000
        pars['midistat_keys'] = None # the MIDI status that identifies keys (black and white)
        pars['key_ids_ext'] = None # 
        pars['key_ids_pars'] = array((),int)
        pars['key_action_pars'] = array((),int)
        pars['midistat_slide'] = 176 # the MIDI status that identifies sliders
        pars['slide_ids_pars'] = range(81,86) # these IDs control parameters
        pars['slide_action_pars'] = ['s_e','s_i','tau_e','tau_i','cam_external_max']
        pars['slide_action_ext'] =        [0,  1,  2] # the actions corresponding to the slide_ids
            # 0: input to all neurons
            # 1: input to excitatory neurons, i.e. pars['Exc_ids']
            # 2: input to inhibitory neurons, i.e. pars['Inh_ids']
        pars['slide_ids_ext'] = [86,87,88]# MIDI controllers that control external input
    elif keys=='boris': #joens sein usb-keyboars
        pars['midistat_keys'] = 144 # the MIDI status that identifies keys (black and white)
        pars['key_ids_ext'] = range(36,85) # the 0-octave keyboard notes
        pars['key_ids_pars'] = array((),int)
        pars['key_action_pars'] = array((),int)
        pars['midistat_slide'] = 176 # the MIDI status that identifies sliders
        pars['slide_ids_pars'] = [47,48, 49,50] # these IDs control parameters
        pars['slide_action_pars'] = ['s_e','s_i','tau_e','tau_i']
        pars['slide_action_ext'] =        [0,  1,  2] # the actions corresponding to the slide_ids
            # 0: input to all neurons
            # 1: input to excitatory neurons (ids 1:pars['Ne'])
            # 2: input to inhibitory neurons (ids pars['Ne']+0:pars['Ni'])
            # 3: input to ids [0 4 9 14 19]
            # 4: input to ids [24 29 34 39]
        pars['slide_ids_ext'] = [71, 74, 52]# MIDI controllers that control external input
    elif keys=='D-50':
        pars['midistat_keys'] = 200
        pars['key_ids_ext'] = range(40,80)
        pars['key_ids_pars'] = range(10,16) # those keys that will control continous parameters
        pars['key_action_pars'] = range(14)
            # 0: increase all external input
            # 1: decrease all external input 
            # 2: increase excit input
            # 3: decrease excit input
            # 4: increase inhib input
            # 5: decrease inhib input
            # 6: increase s_e
            # 7: decreae s_e
            # 8: increase s_i
            # 9: decreae s_i
            # 10: increase tau_e
            # 11: decreae tau_e
            # 12: increase tau_i
            # 13: decreae tau_i
        pars['midistat_slide'] = None
    elif keys=='andys':
        pars['midistat_keys'] = 159
        pars['key_ids_ext'] = [36,38,40,41,43,45]
        pars['key_action_ext'] = range(6)
            # 0: decrease all external input
            # 1: increase all external input 
            # 2: decrease input to excit pop.
            # 3: increase input to excit pop.
            # 4: decrease input to inhib pop.
            # 5: increase input to inhib pop.
        pars['key_ids_pars'] = [48,50,52,53,55,57,59,60] # those keys that will control continous parameters
        pars['key_action_pars'] = range(8)
            # 0: decreae s_e
            # 1: increase s_e
            # 2: decreae s_i
            # 3: increase s_i
            # 4: decreae tau_e
            # 5: increase tau_e
            # 6: decreae tau_i
            # 7: increase tau_i
        pars['midistat_slide'] = None
        pars['slide_ids_ext'] = None
        pars['slide_ids_pars'] = None
    return pars