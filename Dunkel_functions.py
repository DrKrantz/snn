from numpy import *


from Dunkel_pars import parameters
from output.conversion import chord_conversion

global pars
pars = parameters()
# Created by B. Staude to simulate the Thalamic Network (Figs. 3 and 4) of Destexhe 2009, J Comp Neurosci.
# January 2010
# version 1.1: included deadtime, 22.1.10
# include the webcam image, 31.03.2010
# included parameter- and spiking display


def note2neuron(note_id):
    # pars = parameters()
    return note_id-pars['note_add']


def neuron2note(neuron_id, conversion_type):
    # conversion_type: 1 - linear tonal arrangement
    #		2 - neurons are arranged on a grid, the row determines the note
    #		3 - all excitatory have one note, all inhibitory have another
    #		4 - linear tonal arrangement in C-dur
    #		5 - linear tonal arrangement in C-moll
    #print conversion_type

    if conversion_type == 1:
        note = int(mod(neuron_id, 127)+1)
    if conversion_type == 2:
        coord = linear2grid(neuron_id,pars['N_col'])
        note = coord[1]
    if conversion_type == 3:
        if any((pars['Exc_ids'] - neuron_id) == 0):
            note = 120
        else:
            note = 20
    if conversion_type == 4:
        durlist, mollist = chord_conversion()
        nnotes = len(durlist)
        note = durlist[int(mod(neuron_id, nnotes))]
    if conversion_type == 5:
        durlist, molllist = chord_conversion()
        nnotes=len(molllist)
        #print mod(neuron_id,nnotes)
        #print molllist
        note = molllist[int(mod(neuron_id, nnotes))]
    return note

def grid2linear(coord,N_col):
    Nid = N_col*coord[1]+coord[0]
    return Nid
	
def toric_length(coord,nrow,ncol):
	# the length of the vector coord, assuming a torus. coord can have negative entries!
	if abs(double(coord[0]+1)/ncol)>0.5:
		coord[0] = coord[0] - sign(coord[0])*ncol
	if abs(double(coord[1]+1)/nrow)>0.5:
		coord[1] = coord[1] - sign(coord[1])*nrow
	#print coord
	return sum(coord**2)**.5

def get_LCRN_post(pre_id,s_nrow,s_ncol,t_nrow,t_ncol,ncon,con_sigma):
	s_y = floor(pre_id/s_nrow)
	s_x = remainder(pre_id,s_ncol)
	s_y = s_y *(t_nrow/s_nrow)
	s_x = s_x *(t_nrow/s_nrow)
	phi = random.rand(ncon)*2*pi
	radius = random.randn(ncon)*con_sigma
	x2 = ceil(cos(phi)*radius)
	y2 = ceil(sin(phi)*radius)
	x_id = pylab.find(x2<0)
	x2[x_id] = x2[x_id] + t_ncol
	x_id = pylab.find(x2>t_ncol-1)
	x2[x_id] = x2[x_id] - t_ncol
	y_id = pylab.find(y2<0)
	y2[y_id] = y2[y_id] + t_nrow
	y_id = pylab.find(y2>t_nrow-1)
	y2[y_id] = y2[y_id] - t_nrow
	target_id = x2 *(t_ncol-1) + y2
	target_id = target_id.astype(int)
	target_id = abs(target_id)
	z_id  = pylab.find(target_id==pre_id)
	target_id[z_id] = target_id[z_id]+1
	return target_id

def small2string(number):
# convert doubles into human readible strings
	if number<=0:
		value = '0'
	else:
		exponent = int(floor(log10(number)))
		base = str( round(10*number*10**(-exponent))/10)
		value = base + 'e' + str(exponent)
	return value

