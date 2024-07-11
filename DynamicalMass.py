# From any two of the inputs radius, rotation velocity, and dynamical mass, calculates all in
# standard and astronomical conventional units

import streamlit as st
import astropy
from astropy import units as u
from astropy.constants import M_sun
from astropy.constants import G
from astropy.constants import pc
import imp
import math as maths

# External script imported as function
# Returns human-readable versions of numbers, e.g, comma-separated or scientific notation depending on size
import NiceNumber
imp.reload(NiceNumber)
from NiceNumber import nicenumber


# STREAMLIT STYLE
# Remove the menu button
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

# Remove vertical whitespace padding
st.write('<style>div.block-container{padding-top:0rem;}</style>', unsafe_allow_html=True)
st.write('<style>div.block-container{padding-bottom:0rem;}</style>', unsafe_allow_html=True)


# Set the title and subtitle
st.title("Dynamical Mass and Circular Speed")
st.subheader("Calculates dynamical mass, circular speed and/or radius depending on user inputs")

# Description
st.write("Allows the user to convert using standard and astronomical units. Set any two parameters to non-zero values and the third to zero. All three will be printed in standard and conventional astronomial units. No corrections are made for relativistic effects !")

# Inputs for Radius and Circular Speed
col1, col2, col3, col4 = st.columns(4)

with col1:
    radius = st.number_input("Radius")

with col2:
    radius_unit = st.selectbox("Radius unit", ("m", "pc", "kpc"), index=2)

with col3:
    circular_speed = st.number_input("Circular speed")

with col4:
    circular_speed_unit = st.selectbox("Circular speed unit", ("m/s", "km/s", "mph"), index=1)

# Inputs for Dynamical Mass
col5, col6 = st.columns(2)

with col5:
    dynamical_mass = st.number_input("Dynamical mass")

with col6:
    dynamical_mass_unit = st.selectbox("Dynamical mass unit", ("kg", "Msolar", "log(Msolar)"), index=1)


# Unit conversions. Calculations will be done in SI units
def distance_metres(input_value, input_unit_type):
	if input_unit_type == 'm':
		si_distance = input_value
	
	if input_unit_type == 'pc':
		si_distance = u.pc.to(u.m, input_value)
	
	if input_unit_type == 'kpc':
		si_distance = u.kpc.to(u.m, input_value)
		
	return si_distance
	
	
def circular_ms(input_value, input_unit_type):
	if input_unit_type == 'm/s':
		si_speed = input_value
	
	if input_unit_type == 'km/s':
		si_speed = input_value*1000.0
		
	if input_unit_type == 'mph':
		si_speed = (input_value*1609.344)/3600.0
		
	return si_speed
	
def mass_kg(input_value, input_unit_type):
	if input_unit_type == 'kg':
		si_mass = input_value
		
	if input_unit_type == 'Msolar':
		si_mass = input_value*M_sun.value	# Use the astropy constant
		
	if input_unit_type == 'log(Msolar)':
		msol_linear = 10.0**input_value
		si_mass = msol_linear*M_sun.value	# Use the astropy constant
		
	return si_mass
	



# Do calculation only if two inputs are non-zero and the other is zero
input_values = [radius, circular_speed, dynamical_mass]
non_zero_count = sum(1 for value in input_values if value != 0.0)


if non_zero_count == 2:
	# If only the radius is unknown, use the given values for mass and velocity and calculate radius
	if radius == 0.0:
		# Get mass and velocity in SI units
		mass_si = mass_kg(dynamical_mass, dynamical_mass_unit)
		vcir_si = circular_ms(circular_speed, circular_speed_unit)
		
		# Calculate radius in SI units, using the astropy constant for G
		r_si = (G.value*mass_si)/(vcir_si*vcir_si)
			
	# If only the circular speed is unknown, use the given values for mass and radius and calculate speed			
	elif circular_speed == 0.0:
		# Get mass and radius in SI units
		mass_si = mass_kg(dynamical_mass, dynamical_mass_unit)
		r_si    = distance_metres(radius, radius_unit)
		
		# Calculate circular speed in SI units
		vcir_si = maths.sqrt((G.value*mass_si)/r_si)
		
	# If only the dynamical mass is unknown, use the given values for radius and speed and calculate mass	
	elif dynamical_mass == 0.0:
		# Get the radius and speed in SI units
		r_si    = distance_metres(radius, radius_unit)
		vcir_si = circular_ms(circular_speed, circular_speed_unit)
		
		# Calculate mass in SI units
		mass_si = ((vcir_si*vcir_si)*r_si) / G.value


	# Convert everything to standard astronomical conventions
	mass_ac  = mass_si/M_sun.value
	mass_acl = maths.log10(mass_ac)
	vcir_ac  = vcir_si/1000.0
	r_ac     = r_si/pc.value
	r_ack    = r_ac/1000.0

	# Print the values, first in a sensible format using standard astronomical conventional units
	st.write('##### Values in astronomer-friendly format :')
	
	# For radius, use kpc if more than 500 pc
	if r_ac <= 500.0:
		st.write('Radius :',nicenumber(r_ac),'pc')
	if r_ac > 500.0:
		st.write('Radius :',nicenumber(r_ack),'kpc')
		
	# Similarly for circular speed, revert to m/s if less than 500 km/s
	if vcir_si <= 500.0:
		st.write('Circular speed :',nicenumber(vcir_si),'m/s')
	if vcir_si > 500.0:
		st.write('Circular speed :',nicenumber(vcir_ac),'km/s')
	
	# Finally, give dynamical mass in both linear and logarithmic units	
	st.write('Dynamical mass :',nicenumber(mass_ac),'linear solar masses ('+str(nicenumber(mass_acl)+' logarithmic units)'))
	
	st.write('##### Exact values in SI units :')
	st.write('Radius :',str(r_si),'m')
	st.write('Circular speed :',str(vcir_si),'m/s')
	st.write('Dynamical mass :',str(mass_si),'kg')

else:
	st.write("Please enter values for exactly two inputs.")


