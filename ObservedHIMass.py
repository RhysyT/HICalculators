# Simple script to calculate the HI mass of a source given its total flux and distance. Optionally also calculates the
# integrated S/N ratio according to the prescription of Saintonge 2007. Gives the results in nicely formated values.

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
st.write("# Observed HI mass calculator")
st.write('#### Calculate the HI mass given a measured flux value')


left_column, right_column = st.columns(2)


with left_column:
	# HI flux number widget, row 1
	hiflux = st.number_input("Total HI flux", key="flux")
		
	# Distance number widget, row 2 (rows are generated automatically within columns)
	distance = st.number_input("Distance to the source", key="dist")


with right_column:
	# Flux unit widget, row 1 (adjacent to flux widget)
	fluxunit = st.selectbox('Flux units', ('Jy', 'mJy'), key="funit")

	# If units are in mJy, convert to Jy for the mass calculation
	if fluxunit == 'mJy':
		hiflux = hiflux*1000.0
	
	# Distance unit widget, row 2 (adjacent to distance number widget)
	# Need to provide a "key" parameter as we will be using an otherwise identical widget later on and the two must 
	# be different
	distunit = st.selectbox('Distance units', ('Mpc', 'kpc', 'pc'), key='obsdist') 

	if distunit == 'pc':
		distance = distance / 1000000.0
	if distunit == 'kpc':
		distance = distance / 1000.0
		

himass = 2.36E5 * distance*distance * hiflux
himasskg = himass*1.98847E30


# Optionally the user can provide other parameters for calculating the integrated S/N
dosncalc = False
totsn = None

if st.checkbox('Calculate integrated S/N'):
	st.write('Optionally provide velocity resolution, rms and line width, for calculating the integrated S/N ratio according to the ALFALFA criteria of Saintonge et al. 2007)')
	dosncalc = True
	
	# Need to create new columns here to force a break. If we don't do this, the new parameters will be created ABOVE the checkbox, which just looks weird and 
	# confusing !
	left_column2, right_column2 = st.columns(2)
	
	with left_column2:
		# Velocity resolution number, row 1
		vres = st.number_input("Velocity resolution", key="vr")
		
		# W50, row 2
		w50 = st.number_input("Line width (W50, FWHM)", key="vr")
		
		# RMS value, row 3
		orms = st.number_input("Spectra rms", key="onoise")
	
	with right_column2:
		# Velocity resolution unit, row 1
		vrunit = st.selectbox('Velocity resolution units', ('km/s', 'm/s'), key="vresunit")
	
		if vrunit == 'm/s':
			vres = vres / 1000.0
			#st.write("Velocity resolution = ", vres, ' in km/s')
		
		# Width unit, row 2
		wunit = st.selectbox('Line width units', ('km/s', 'm/s'), key="wunitk")
	
		if wunit == 'm/s':
			w50 = w50 / 1000.0
			#st.write("Line width = ", w50, ' in km/s')
		
		# Rms unit, row 3
		ormsunit = st.selectbox('Noise unit', ('mJy', 'Jy'), key="orkey")

		# Input rms to the aasn routine in Jy, will be converted to mJy in the function itself
		if ormsunit == 'mJy':
			orms = orms / 1000.0
			#st.write('Rms noise = ',orms,' in Jy')

	# Only calculate the S/N if we won't divide by zero
	if w50 > 0.0 and orms > 0.0:
		totsn = aasn(hiflux, w50, vres, orms)


st.write("#### Total HI mass = ", nicenumber(himass),' in solar masses, or ', nicenumber(himasskg),' in kg.') 
st.write('Exact values are',himass,'in solar masses and',himasskg,'in kg.')

if totsn is not None:
	st.write('#### Integrated S/N = ', nicenumber(totsn))
	st.write('Values above 6.5 indicate that the source is generally considered reliable.')
if totsn is None and dosncalc == True:
		st.write('#### Errors in input values, cannot calculate integrated S/N value.')
		st.write('#### Check that the wdith and rms values are not zero.')
