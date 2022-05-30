# Simple calculator to compute the total HI flux in a top-hat profile. User specifies S/N, rms, line width, and
# distance. Useful for estimating mass sensitivity.
# Optionally, also computes the integrated S/N as defined by Saintonge 2007.

import streamlit as st
import math
import imp

# EXTERNAL SCRIPTS IMPORTED AS FUNCTIONS
# "nicenumber" function returns human-readable versions of numbers, e.g, comma-separated or scientific notation depending
# on size
import NiceNumber
imp.reload(NiceNumber)
from NiceNumber import nicenumber

# Function to calculate the total integrated S/N
import AASN
imp.reload(AASN)
from AASN import aasn


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
st.write('#### Calculate the HI mass for a top-hat profile, specifying line width, rms, S/N and distance')

# A new set of columns
left_column3, right_column3 = st.columns(2)

with left_column3:
	# Line width widget, row 1
	linewidth = st.number_input("HI line width", key="lw")
	
	# Rms widget, row 2
	rms = st.number_input("Spectra rms", key="noise")
	
	# Another distance widget, distinct from the earlier 1, row 3
	disttop = st.number_input("Distance to the source", key="distth")

	
	
with right_column3:
	# Line width unit, row 1
	lineunit = st.selectbox('Line width units', ('km/s', 'm/s'), key="lwunit")

	if lineunit == 'm/s':
		linewidth = float(linewidth) / 1000.0
	
	# Rms unit, row 2
	rmsunit = st.selectbox('Noise unit', ('mJy', 'Jy'), key="runit")

	if rmsunit == 'mJy':
		rms = rms / 1000.0

	# Distance unit widget, row 3
	distunitth = st.selectbox('Distance units', ('Mpc', 'kpc', 'pc'), key='topdist')

	if distunitth == 'pc':
		disttop = disttop / 1000000.0
	if distunitth == 'kpc':
		disttop = disttop / 1000.0


# S/N widget, dimensionless units. Keep outside the columns.
sn = st.number_input("Signal to noise ratio", key="snr")


# Optionally the user can provide other parameters for calculating the integrated S/N
dosncalc = False
totsn = None
topflux = sn*linewidth*rms

if st.checkbox('Calculate integrated S/N'):
	st.write('Optionally provide velocity resolution, rms and line width, for calculating the integrated S/N ratio according to the ALFALFA criteria of Saintonge et al. 2007)')
	dosncalc = True
	
	# Need to create new columns here to force a break. If we don't do this, the new parameters will be created ABOVE the checkbox, which just looks weird and 
	# confusing !
	left_column2, right_column2 = st.columns(2)
	
	with left_column2:
		# Velocity resolution number, row 1
		vres = st.number_input("Velocity resolution", key="vr")
		
	
	with right_column2:
		# Velocity resolution unit, row 1
		vrunit = st.selectbox('Velocity resolution units', ('km/s', 'm/s'), key="vresunit")
	

	# Only calculate the S/N if we won't divide by zero
	if vres > 0.0 and rms > 0.0:
		totsn = aasn(topflux, linewidth, vres, rms)	
	


st.write('##### Total flux = ',topflux,' in Jy km/s')

topmass = 2.36E5 * disttop*disttop * topflux
tophimasskg = topmass*1.98847E30
st.write("#### Total HI mass = ", nicenumber(topmass),'M<sub style="font-size:60%">&#8857;</sub>, or ', nicenumber(tophimasskg),'kg.', unsafe_allow_html=True) 
st.write('Exact values are',topmass,'M<sub style="font-size:60%">&#8857;</sub> and',tophimasskg,'kg.', unsafe_allow_html=True)
	
if totsn is not None:
	st.write('#### Integrated S/N = ', nicenumber(totsn))
	st.write('Values above 6.5 indicate that the source is generally considered reliable.')
if totsn is None and dosncalc == True:
		st.write('#### Errors in input values, cannot calculate integrated S/N value.')
		st.write('#### Check that the wdith and rms values are not zero.')
