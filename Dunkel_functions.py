from numpy import *
import pygame


# packages need for the webcam

# packages needed for the parameter-display
from pygame.locals import *

from Dunkel_pars import parameters
global pars
pars = parameters()
# Created by B. Staude to simulate the Thalamic Network (Figs. 3 and 4) of Destexhe 2009, J Comp Neurosci.
# January 2010
# version 1.1: included deadtime, 22.1.10
# include the webcam image, 31.03.2010
# included parameter- and spiking display


def chordConversion():
    """
    create the midi notes of a major and a minor scale
    :return:
    """

    #dur
    a = array([0, 2, 4, 5, 7, 9, 11])
    b = []
    [b.append(a + k * 12) for k in range(11)]
    durlist = array(b).flatten()

    #moll
    a = array([0, 2, 3, 5, 7, 8, 10])
    b = []
    [b.append(a + k * 12) for k in range(11)]
    molllist = array(b).flatten()
    return durlist, molllist


def chromaticConversion():
    """
    create the midi notes of a major scale and its transpose (half-tome up)
    :return:
    """
    #low
    a = array([0, 2, 4, 5, 7, 9, 11])
    b = []
    [b.append(a + k * 12) for k in range(11)]
    listLow = array(b).flatten()

    #high
    a += 1
    b = []
    [b.append(a + k * 12) for k in range(11)]
    listHigh = array(b).flatten()
    return listLow, listHigh

def note2neuron(note_id):
#	pars = parameters()
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
        durlist, mollist = chordConversion()
        nnotes = len(durlist)
        note = durlist[int(mod(neuron_id, nnotes))]
    if conversion_type == 5:
        durlist, molllist = chordConversion()
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
			
def map_keys(eingang):
# prints the MIDI-info of the eingang if a button is pressed
	while 1:
		if eingang.poll():
			data = eingang.read(2)
			print(data)


# def construct_output(type='IAC Driver Bus 1', instrument=1):
# 	# this constructs an output
# 	return mido.open_out
#
# 	n_device = pm.get_count()
# 	out_id = -1
# 	for id in range(n_device):
# 		if int(pm.get_device_info(id)[1]==type) & int(pm.get_device_info(id)[3]==1):
# 			out_id = id
# 			ausgang = pm.Output(out_id,0)
# 			ausgang.set_instrument(instrument)
# 			print("output: "+type)
# 			return ausgang
# 	print("output: "+type+" not available")
# #	if out_id == -1:
# #		print "desired output: "+type+ " not available"
	
	

# def construct_input(type='MK-449C USB MIDI Keyboard'):
# 	pm.init()
# 	n_device = pm.get_count()
# 	in_id = -1
# 	for id in range(n_device):
# 		if int(pm.get_device_info(id)[1]==type) & int(pm.get_device_info(id)[2]==1):
# 			in_id = id
# 			print("input: "+type)
# #	if in_id == -1:
# #		print "desired input: "+type+ " not available"
#
# 	eingang = pm.Input(in_id)
# 	return eingang


		
# class MIDI:
# 	def __init__(self,instrument=1):
# 		########
#
# 		#type_in = 'USB MIDI ADC 64       '
# #		type_in ='MK-449C USB MIDI Keyboard'
# 		#type_in = 'MK-225C USB MIDI keyboard'
# 		type_in = 'Virtual BCF2000'#type_in='USB Axiom 61 Port 1'
# 		#type_in ='Network TEst'
# 		type_out ='SimpleSynth virtual input'
# 		#type_out_concious = 'MIDISPORT 2x2 Anniv B '
# #		type_out_soundextern = 'MIDISPORT 2x2 Anniv Port A'
# 		#type_out ='Network TEst'
# 		#type_out = 'PreSonus FIREBOX (1808) Plug 1'
# 		# initialize the MIDI-setup
# #		try:
# #			self.ausgang = construct_output(type_out,instrument)
# #		except:
# #			print "desired output: "+type_out+ " not available"
# #
# 		#try:
# 		#	self.ausgang_concious = construct_output(type_out_concious,instrument)
# 		#except:
# 		#	pass
# #			print "desired input: "+type_out_concious+ " not available"
# #		try:
# #			self.ausgang_soundextern = construct_output(type_out_soundextern,instrument)
# #		except:
# ##			pass
# #			print "desired input: "+type_out_soundextern+ " not available"
# 		try:
# 			self.eingang = construct_input(type_in)
# 		except:
# 			print("desired input: "+type_in+ " not available")
			
class Spike_Display:
	#global pars
	def __init__(self,N_col,N_row,disp_type='dot'):#disp_type='dot',
		# parnames: list of names for the parameters
		self.disp_type = disp_type
		self.N_col = N_col
		self.N_row = N_row
		self.point_size = 3 # the point size in case of 'dot'-display
		self.point_dist = 20 # the distance between th points
		self.border = 5

		w =  N_col*self.point_dist + self.border
		h = N_col*self.point_dist + self.border
		self.disp_size  = (w,h)
		self.text_color = (0,0,255,0)
		self.fill_color = (255,255,255,255)
		self.screen = pygame.display.set_mode(self.disp_size, 0, 32)
		self.par_surface = pygame.Surface( self.disp_size, flags=SRCALPHA, depth=32 )#
		self.par_surface.fill( self.fill_color )
	def update(self,fired):
		self.screen.fill((255,255,255))
		if self.disp_type == 'dot':
			for id in fired:
				coord = linear2grid(id,self.N_col)*self.point_dist+self.border
				pygame.draw.circle(self.screen,(0,0,255),coord,self.point_size,0)
		elif self.disp_type == 'lines':
			coord = []
			for id in fired:
				coord.append(linear2grid(id,self.N_col)*self.point_dist)
			coord = array(coord)+self.border
			#print coord
			if len(coord)>1:
				pygame.draw.lines(self.screen,(0,0,255),1,coord)
			elif len(coord)==1:
				pygame.draw.circle(self.screen,(0,0,255),coord[0],self.point_size,0)

