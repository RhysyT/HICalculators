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
st.write('Simple calculator to convert HI flux into mass (solar units). Requires the flux and distance. Optionally, estimates the integrated S/N if additional parameters are provided. Can also accept input in a few different units.')
st.write('Uses the standard mass equation : M<sub style="font-size:80%">HI</sub>&thinsp;=&thinsp;2.36x10<sup>5</sup>&thinsp;d<sup>2</sup>&thinsp;F<sub style="font-size:80%">total</sub><br>Where d is the distance in Mpc and F<sub style="font-size:80%">total</sub> is the total integrated flux in Jy&thinsp;km/s.', unsafe_allow_html=True)

left_column, right_column = st.columns(2)


with left_column:
	# HI flux number widget, row 1
	hiflux = st.number_input("Total HI flux", key="flux", help='Total integrated flux over the whole line width of the source')
		
	# Distance number widget, row 2 (rows are generated automatically within columns)
	distance = st.number_input("Distance to the source", key="dist")


with right_column:
	# Flux unit widget, row 1 (adjacent to flux widget)
	fluxunit = st.selectbox('Flux units', ('Jy', 'mJy'), key="funit")

	# If units are in mJy, convert to Jy for the mass calculation
	if fluxunit == 'mJy':
		hiflux = hiflux/1000.0
	
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
	st.write('Optionally provide velocity resolution, rms and line width, for calculating the integrated S/N ratio according to the ALFALFA criteria of Saintonge et al. 2007 :')
	st.latex(r'''S/N =\frac{1000F_{total}}{W_{50}}\frac{w^{1/2}_{smo}}{rms}''')
	st.write('Where w<sub style="font-size:60%">smo</sub> is a smoothing function depending on W50. If W50 &#8804; 400 km/s :', unsafe_allow_html=True)
	st.latex(r'''w_{smo} = W50 / (2 \times v_{res})''')
	st.write('And if W50 > 400 km/s :')
	st.latex(r'''w_{smo} = 400 / (2 \times v_{res})''')
	st.write('')
	
	dosncalc = True
	
	# Need to create new columns here to force a break. If we don't do this, the new parameters will be created ABOVE the checkbox, which just looks weird and 
	# confusing !
	left_column2, right_column2 = st.columns(2)
	
	with left_column2:
		# Velocity resolution number, row 1
		vres = st.number_input("Velocity resolution", key="vr", help='Velocity resolution after smoothing')
		
		# W50, row 2
		w50 = st.number_input("Line width (W50, FWHM)", key="w50", help='Estimated line width of the source at 50% of the peak flux')
		
		# RMS value, row 3
		orms = st.number_input("Spectra rms", key="onoise")
	
	with right_column2:
		# Velocity resolution unit, row 1
		vrunit = st.selectbox('Velocity resolution units', ('km/s', 'm/s'), key="vresunit")
	
		if vrunit == 'm/s':
			vres = vres / 1000.0
			#st.write("Velocity resolution = ", vres, ' in km/s')
		
		# Width unit, row 2
		wunit = st.selectbox('Line width resolution units', ('km/s', 'm/s'), key="wunitk")
	
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


# Use a different unicode character for the odot symbol in heading and standard text, as this gives more visually consistent results
st.write("#### Total HI mass = ", nicenumber(himass),'M<sub style="font-size:60%">&#9737;</sub>, or ', nicenumber(himasskg),'kg.', unsafe_allow_html=True) 
# Exact values printed as strings for font consistency (numbers are shown in green by default)
st.write('Exact values are '+str(himass)+'&thinsp;M<sub style="font-size:60%">&#8857;</sub> and '+str(himasskg)+'&thinsp;kg.', unsafe_allow_html=True)

if totsn is not None:
	st.write('#### Integrated S/N = ', nicenumber(totsn))
	st.write('Values above 6.5 indicate that the source is generally considered reliable.')
if totsn is None and dosncalc == True:
	st.write('#### Errors in input values, cannot calculate integrated S/N value.')
	st.write('#### Check that the wdith and rms values are not zero.')
