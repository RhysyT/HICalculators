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
st.write('#### Calculate an average HI column density, given a mass and size for a source. Size can be either radius or diameter, with different units available for both mass and size.')


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


# Finally we can actually compute column density !
if hirad > 0.0:	# Avoid divide by zero error
	nhi_atomssqcm = hinatoms / (pi * (hiradm*100.0)**2.0)
	ni_msolsqpc = hisolarmasses / (pi * hiradpc**2.0)

	st.write("#### HI column density = " "{:.2e}".format(nhi_atomssqcm),' atoms per square cm, or ', nicenumber(ni_msolsqpc),' in solar masses per square parsec.') 
	st.write('Exact values are',nhi_atomssqcm,'in atoms per sq. cm and',ni_msolsqpc,'in solar masses per sq. pc.')
