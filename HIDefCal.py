# Calculates the HI deficiency parameter for a source, given its observed HI mass and (optionally) morphology. 
# Allows the user to select preset standard values for the a/b morphological parameters, or supply their own for 
# a range of Hubble types.

import streamlit as st
import math
from math import pi as pi
import imp

# EXTERNAL SCRIPTS IMPORTED AS FUNCTIONS
# "nicenumber" function returns human-readable versions of numbers, e.g, comma-separated or scientific notation depending
# on size
import NiceNumber
imp.reload(NiceNumber)
from NiceNumber import nicenumber

# Callback function for setting checbox
def reset_button():
	st.session_state["dounitcheckbox"] = False
	return

# STYLE
# Remove the menu button
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

# Remove vertical whitespace padding
st.write('<style>div.block-container{padding-top:0rem;}</style>', unsafe_allow_html=True)
st.write('<style>div.block-container{padding-bottom:0rem;}</style>', unsafe_allow_html=True)


# MAIN CODE
# Unit conversions
amu = 1.660540199E-24	# In grams, for Avogadro's number
hiamu = 1.00797
navogadro = 6.02214076E23
solarmass = 1.98847E30
pc = 3.0856775812799588E16 # 1 pc in m


st.write("# Compute HI deficiency")
st.write('### Provide the HI mass and (optionally) morphology. Use preset values for the a/b parameters, or specify your own.')


#HI mass				MassUnitDropdown
#Morphology 
#PresetDropdown 	a		b



	
left_column, right_column = st.columns(2)

with left_column:
	# HI flux number widget, row 1
	himass = st.number_input("Total HI mass", format="%.3f", key="mass")
	
	# Optical diameter number widget, row 2
	optd25 = st.number_input("Optical diameter", format="%.3f", key="od")
		
with right_column:
	# Mass unit widget, row 1 (adjacent to flux widget)
	massunit = st.selectbox('Mass units', ('Linear solar mass', 'Logarithmic solar mass', 'kg'), key="munit")

	# Optical diameter unit widget, row 2 (adjacent to optical diameter widget)
	optdunit = st.selectbox('Optical diameter units', ('m', 'pc', 'kpc', 'Mpc'), index=2, key="odunit")


# Column-independent dropdown for morphology
mtypechoice = st.selectbox('Morphology', ('Early', 'Sa, Sab', 'Sb', 'Sbc', 'Sc', 'Scd', 'Sd', 'Sdm, Sm', 'Im', 'Later (generally >= Scd)', 'General'), index=10, key="htype")


#with right_column:
	# On the second row we need three columns of unequal width. The first will be the numerical size of the HI, the second the 
	# specification of radius or diameter, and the third the unit
	# Providing a list of numbers (instead of a single number) sets the size ratio of each column

lcol, mcol, rcol = st.columns([2,1,1])
	
with lcol:
	# Morphology parameter selection box
	mparams = st.selectbox("Use preset or custom parameters", ('Haynes & Giovanelli 1984', 'Solanes et al. 1996', 'Gavazzi et al. 2005', 'Custom'), index=0, key="type")

with mcol:
	# A parameter number widger
	aparam = st.number_input("a", format="%.3f", key="keya")	
	
with rcol:
	# B parameter number widger
	bparam = st.number_input("b", format="%.3f", key="keyb")


# *** DONE UP TO THIS BIT ! ***


# First convert the mass into linear solar units :
if massunit == 'Linear solar mass':
	hisolarmasses = himass
	
if massunit == 'Logarithmic solar mass':
	hisolarmasses = 10.0**himass
	
if massunit == 'kg':
	hisolarmasses = himass/solarmass
	
# We'll also need that in logarithmic units for the deficiency calculation :
if hisolarmasses > 0.0:
	loghimass = math.log10(hisolarmasses)
	

# Next convert the optical diameter into kpc
if optdunit == 'm':
	optd = optd25 / (1000.0*pc)
	
if optdunit == 'pc':
	optd = optd25 / 1000.0
	
if optdunit == 'kpc':
	optd = optd25
	
if optdunit == 'Mpc':
	optd = optd25 / 1000000.0


# Set the a and b parameters	
if mparams == 'Custom':
	a = aparam
	b = bparam
	

if mparams == 'Haynes & Giovanelli 1984':	
	if mtypechoice == 'Early':
		a = 6.88
		b = 0.89*2.0

	if mtypechoice == 'Sa, Sab':
		a = 6.88
		b = 0.89*2.0	
			
	if mtypechoice == 'Sb':
		a = 7.17
		b = 0.82*2.0

	if mtypechoice == 'Sbc':
		a = 7.17
		b = 0.82*2.0
		
	if mtypechoice == 'Sc':
		a = 7.29
		b = 0.83*2.0
		
	if mtypechoice == 'Scd':
		a = 7.27
		b = 0.85*2.0
	
	if mtypechoice == 'Sd':
		a = 6.91
		b = 0.95
	
	if mtypechoice == 'Sdm, Sm':
		a = 7.0
		b = 0.94*2.0
	
	if mtypechoice == 'Im' or mtypechoice == 'Later (generally >= Scd)':
		a = 7.75
		b = 0.66		
		
	if mtypechoice == 'General':
		a = 7.12
		b = 0.88*2.0
	
	
if mparams == 'Solanes et al. 1996':
	if mtypechoice == 'Early':
		a = None
		b = None
		
	if mtypechoice == 'Sa, Sab':
		a = 7.75
		b = 1.19
		
	if mtypechoice == 'Sb':
		a = 7.82
		b = 1.25

	if mtypechoice == 'Sbc':
		a = 7.84
		b = 1.22

	if mtypechoice == 'Sc' or mtypechoice == 'Scd' or mtypechoice == 'Sdm, Sm' or mtypechoice == 'Im' or mtypechoice == 'Later (generally >= Scd)':
		a = 7.16
		b = 1.74
		
	if mtypechoice == 'General':
		a = 7.51
		b = 1.46
	
			
if mparams == 'Gavazzi et al. 2005':
	if mtypechoice == 'Early':
		a = None
		b = None
		
	if mtypechoice == 'Sa, Sab':
		a = 7.29
		b = 1.66
		
	if mtypechoice == 'Sb':
		a = 7.27
		b = 1.70

	if mtypechoice == 'Sbc':
		a = 6.91
		b = 1.90

	if mtypechoice == 'Sc' or mtypechoice == 'Scd' or mtypechoice == 'Sdm, Sm' or mtypechoice == 'Im' or mtypechoice == 'Later (generally >= Scd)':
		a = 7.00
		b = 1.88
		
	if mtypechoice == 'General':
		a = 7.16
		b = 1.64
	

# As long as a and b are defined, we can now calculate the expected HI mass and so get the deficiency
if a is not None and b is not None and optd is not None:
	if optd > 0.0:
		MHI_exp = a + b*math.log10(optd)
		HIdef = MHI_exp - loghimass
		st.write("#### Expected HI mass =",nicenumber(10.0**MHI_exp),"solar masses, or",nicenumber(MHI_exp), "in logarithmic units")
		st.write("#### HI deficiency =",nicenumber(HIdef))
		if mparams == 'Custom':
			st.write('Used the custom parameter values a='+str(a)+' and b='+str(b))
		if mparams != 'Custom':
			st.write('Used the preset parameter values a='+str(a)+' and b='+str(b))
		

# TO DO : FIND MORE A AND B VALUES



	
