# Simple program to calculate the average column density of a source, given input mass and size.
# Allows the user to use either radius or diameter, in different units. Returns result in both
# atoms per square cm and in solar masses per square parsec.

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


st.write("# Compute HI column density")
st.write('### Two ways to use this tool :')
st.write('#### 1) Unit conversion. If you know the total mass detected in a given radius, this will let you convert between standard units, e.g. atoms&thinsp;cm<sup style="font-size:60%">-2</sup> and M<sub style="font-size:60%">&#8857;</sub>&thinsp;pc<sup style="font-size:60%">-2</sup>', unsafe_allow_html=True)
st.write('#### 2) Telescope parameters. Given the flux sensitivity, velocity resolution, and angular size, convert this directly to a column density value and (optionally) total mass. Assumes a top-hat spectral profile.') 

# Radio buttons are toggles, can only choose one option at a time. Much easier for selecting mutually exclusive
# options than checkboxes !
opmode = st.radio("Operation mode ", ('Unit conversion', 'Telescope parameters'))

if opmode == 'Unit conversion':
	
	left_column, right_column = st.columns(2)

	with left_column:
		# HI flux number widget, row 1
		himass = st.number_input("Total HI mass", format="%.3f", key="mass")
		
	with right_column:
		# Mass unit widget, row 1 (adjacent to flux widget)
		massunit = st.selectbox('Mass units', ('Linear solar mass', 'Logarithmic solar mass', 'kg'), key="munit")

	# On the second row we need three columns of unequal width. The first will be the numerical size of the HI, the second the 
	# specification of radius or diameter, and the third the unit
	# Providing a list of numbers (instead of a single number) sets the size ratio of each column

	lcol, mcol, rcol = st.columns([2,1,1])
	
	with lcol:
		# Size number widget	
		sizenum = st.number_input("Size of the HI", format="%.3f", key="size")

	with mcol:
		# Choose between radius and diameter for the size
		sizechoice = st.selectbox('Size type', ('Radius', 'Diameter'), key="stype")
	
	with rcol:
		# Choose the size units. To specify a default with a selectbox widget, we use the index, not the value
		sizeunit = st.selectbox('Size unit', ('Mpc', 'kpc', 'pc', 'm'), index=1, key="sunit")


# Option 2. Telescope paramters. The calculation is essentially the same but with the intermediate step of calculating the mass.
# For this we need the rms, its unit, the line width, its unit, the S/N, the beam size type, and the angular size and unit
# of the beam and its unit.
if opmode == 'Telescope parameters':
	
	left_column, right_column = st.columns(2)

	with left_column:	
		# RMS, row 1
		rms = st.number_input("Spectra rms noise", format="%.3f", key="rms")
			
		# Line width, row 2
		lw = st.number_input("Line width (i.e. channel resolution)", format="%.3f", key="lw")
		
					
	with right_column:
		# RMS unit, row 1
		runit = st.selectbox('Noise unit', ('uJy', 'mJy', 'Jy'), index=1, key="rmsunit")
			
		# Line width unit, row 2
		lwunit = st.selectbox('Line width unit', ('m/s', 'km/s'), index=1, key="lwunit")

	# Optionally convert to total mass as well
	dist = 1.0
	distunit = 'Mpc'
	if st.checkbox('Convert to mass', key='domassconvert'):
		with left_column:
			dist = st.number_input("Distance to the source", value=1.0, key="dists")
			
		with right_column:
			distunit = st.selectbox('Distance units', ('pc', 'kpc', 'Mpc'), index=2, key='distu')
			
	
	# Beam size parameters
	lcol, mcol, rcol = st.columns([2,1,1])
	
	with lcol:
		# Size number widget	
		sizenum = st.number_input("Angular beam size", format="%.3f", key="absize")

	with mcol:
		# Choose between radius and diameter for the size
		sizechoice = st.selectbox('Beam size type', ('Radius', 'Diameter'), key="abstype")
	
	with rcol:
		# Choose the size units. To specify a default with a selectbox widget, we use the index, not the value
		sizeunit = st.selectbox('Size unit', ('Degrees', 'Arcminutes', 'Arcseconds'), index=1, key="sunit")
		
	# Without columns
	snr = st.number_input("S/N", format="%.3f", key="snrk")	
	
	
	# We can now convert to all the standardised parameters
	if distunit == 'Mpc':
		distance = dist
		
	if distunit == 'kpc':
		distance = dist/1000.0
		
	if distunit == 'pc':
		distance = dist/1000000.0
		
	if runit == 'Jy':
		rmsnoise = rms
				
	if runit == 'mJy':
		rmsnoise = rms / 1000.0
		
	if runit == 'uJy':
		rmsnoise = rms / 1000000.0
		
	if lwunit == 'km/s':
		lwuse = lw

	if lwunit == 'm/s':
		lwuse = lw*1000.0
		

	# Now we can calculate the HI mass in standard units. Distance is set by default to 1 Mpc so we can always calculate this.
	# Distance cancels with beam area when doing the NHI calculation, so the distance and its unit don't actually matter for that,
	# but this calculation will be wrong for the mass itself unless the user provides the correct value.
	massunit = 'Linear solar mass'		
	himass = 2.36E5* distance*distance* lw * snr * rmsnoise
				

# First do the mass conversions. We need to have mass in both atoms and linear solar masses. Do the conversion into linear 
# solar masses for each unit (trivial) and also into kg. We'll do the final conversion into atoms at the end.
if massunit == 'Linear solar mass':
	hisolarmasses = himass
	hikgmass = himass*solarmass
	
if massunit == 'Logarithmic solar mass':
	hisolarmasses = 10.0**himass
	hikgmass = hisolarmasses*solarmass
	
if massunit == 'kg':
	hisolarmasses = himass/solarmass
	hikgmass = himass
	

# Now we can get the number of atoms
hinatoms = (hikgmass*1000.0) / (hiamu * amu)


# Next the size conversion. First convert to radius if necessary
if sizechoice == 'Radius':
	hirad = sizenum
	
if sizechoice == 'Diameter':
	hirad = sizenum / 2.0
	
# Now we get this in both metrea and parsecs
if sizeunit == 'm':
	hiradpc = hirad / pc
	hiradm  = hirad
	
if sizeunit == 'pc':
	hiradpc = hirad
	hiradm  = hirad * pc	
	
if sizeunit == 'kpc':
	hiradpc = hirad * 1000.0
	hiradm  = hirad * (1000.0*pc)
	
if sizeunit == 'Mpc':
	hiradpc = hirad * 1000000.0
	hiradm  = hirad * (1000000.0*pc)
	
# If we have angular units, we have to convert to physical units first. Note we've still already converted to radius,
# as well as having distance in Mpc.
if sizeunit == 'Degrees':
	hiradpc = (hirad / 360.0) * 2.0 * pi * distance * 1000000.0
	hiradm = hiradpc * pc

if sizeunit == 'Arcminutes':
	hiradpc = ((hirad/60.0) / 360.0) * 2.0 * pi * distance * 1000000.0
	hiradm = hiradpc * pc

if sizeunit == 'Arcseconds':
	hiradpc = ((hirad/3660.0) / 360.0) * 2.0 * pi * distance * 1000000.0
	hiradm = hiradpc * pc


# Finally we can actually compute column density !
if hirad > 0.0:	# Avoid divide by zero error
	nhi_atomssqcm = hinatoms / (pi * (hiradm*100.0)**2.0)
	ni_msolsqpc = hisolarmasses / (pi * hiradpc**2.0)

	st.write("#### HI column density = ",nicenumber(nhi_atomssqcm),' atoms&thinsp;cm<sup style="font-size:60%">-2</sup>, or ', nicenumber(ni_msolsqpc),'M<sub style="font-size:60%">&#8857;</sub>&thinsp;pc<sup style="font-size:60%">-2</sup>', unsafe_allow_html=True)
	st.write('Exact values are',nhi_atomssqcm,'in atoms&thinsp;cm<sup style="font-size:60%">-2</sup> and',ni_msolsqpc,'M<sub style="font-size:60%">&#8857;</sub>&thinsp;pc<sup style="font-size:60%">-2</sup>.', unsafe_allow_html=True)

# The mass conversion option is only available in the telescope parameter mode
if opmode == 'Telescope parameters':	
	if st.session_state['domassconvert'] == True:
		st.write("#### Total HI mass = ", nicenumber(himass), 'in M<sub style="font-size:60%">&#8857;</sub>', unsafe_allow_html=True)
	
