# Simple little code for converting angular size into physical projected distance and vice-versa.
# Base code generated by ChatGPT-4o, tweaked for aesthetics

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


# Convert angular to physical size
def angular_to_physical(angular_size, distance, angular_unit, distance_unit):
    # Standardise units
	# First convert angular size to degrees. No need for any conversion if input is in parsecs
    if angular_unit == 'arcminutes':
        angular_size = angular_size / 60.0
    elif angular_unit == 'arcseconds':
        angular_size = angular_size / 3600.0
    
    # Next convert distance to parsecs
    if distance_unit == 'kpc':
        distance = distance * 1E3
    elif distance_unit == 'Mpc':
        distance = distance * 1E6
    
    # Calculate physical size in parsecs
	# ChatGPT's solution :
    #physical_size = 2 * distance * math.tan(math.radians(angular_size / 2))
	# I prefer my own formulation, base on the fraction of the circumference of a circle
    physical_size = (angular_size / 360.0) * 2.0 * pi * distance
	
	# Return the answer in this raw standardised form. Gets formatted and printed in different units
	# in the main part of the code.
    return physical_size


def physical_to_angular(physical_size, physical_unit, distance, distance_unit):
    # Standardise units, if input is not in pc. If it is, no need to alter the value
	# Convert physical size 
	if physical_unit == 'kpc':
		physical_size = physical_size * 1E3
	elif physical_unit == 'Mpc':
		physical_size = physical_size * 1E6
	
	# Convert distance
	if distance_unit == 'kpc':
		distance = distance * 1E3
	elif distance_unit == 'Mpc':
		distance = distance * 1E6
    
	# Calculate angular size in degrees
	# ChatGPT's answer with unnecessary trigonometry
	#angular_size = 2 * math.degrees(math.atan(physical_size / (2 * distance)))
	# My preferred, more physical formulation
	angular_size = (360.0*physical_size) / (2.0 * pi* distance)
    
	# Return angular size in raw units of degrees. Formatting and conversion to arcmin/sec is done
	# in the main part of the code.  
	return angular_size


# Streamlit GUI
st.title("Angular / Physical Size Converter")
st.write('### Converts angular to physical size and vice-versa')
st.write('Assumes a simple Euclidian geometry and does not account for any cosmological effects. Should give reasonable results at low redshifts, i.e. < 0.1 or so.')


# Define columns to hold the widgets for the user-entered parameters
left_column, left_mid_column, right_mid_column, right_column = st.columns(4)

# User first chooses which direction of conversion
conversion_type = st.radio("Choose conversion type", ("Angular to Physical", "Physical to Angular"))


if conversion_type == "Angular to Physical":
	with left_column:
		angular_size = st.number_input("Angular size")
	
	with left_mid_column:
		angular_unit = st.selectbox("Angular unit", ("degrees", "arcminutes", "arcseconds"))
    
	with right_mid_column:
		distance = st.number_input("Distance")
    
	with right_column:
		distance_unit = st.selectbox("Distance unit", ("pc", "kpc", "Mpc"))
    
	physical_size = angular_to_physical(angular_size, distance, angular_unit, distance_unit)
	
	st.write('##### Physical size in friendly numbers')
	nice_parsec  = nicenumber(physical_size)
	nice_kparsec = nicenumber(physical_size / 1000.0)
	nice_Mparsec = nicenumber(physical_size / 1000000.0)
	
	st.write(nice_parsec,'pc')
	st.write(nice_kparsec,'kpc')
	st.write(nice_Mparsec,'Mpc')
	
	st.write('##### Physical size unformatted')
	
	st.write(f"{physical_size} parsecs")

else:
	with left_column:
		physical_size = st.number_input("Physical size")
    
	with left_mid_column:
		physical_unit = st.selectbox("Size unit", ("pc", "kpc", "Mpc"))	
    
	with right_mid_column:
		distance = st.number_input("Distance")
    
	with right_column:
		distance_unit = st.selectbox("Distance unit", ("pc", "kpc", "Mpc"))
    
    #if st.button("Convert"):
	if distance > 0.0:
		angular_size = physical_to_angular(physical_size, physical_unit, distance, distance_unit)
		
		st.write('##### Angular size in friendly numbers')
		nice_degrees = nicenumber(angular_size)
		nice_arcmins = nicenumber(angular_size * 60.0)
		nice_arcsecs = nicenumber(angular_size * 3600.0)		
		
		st.write(nice_degrees, 'degrees')
		st.write(nice_arcmins, 'arcminutes')
		st.write(nice_arcsecs, 'arcseconds')
		
		st.write('##### Angular size unformatted')
		st.write(f"{angular_size} degrees")