# From any two of the inputs radius, rotation velocity, and dynamical mass, calculates all in standard and 
# astronomical conventional units

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

# Create a custom style for use for subscript unicode characters (e.g. odot)
custom_style = 'style="font-size:60%; vertical-align: middle;"'


# Set the title and subtitle
st.title("Dynamical Mass and Circular Speed")
st.subheader("Calculates dynamical mass, circular speed and/or radius depending on user inputs")

# Description
st.write("Allows the user to convert using standard and astronomical units. Set any two parameters to non-zero values and the third to zero. All three will be printed in standard and conventional astronomial units. Optionally, it can also correct for inclination angle. No corrections are made for relativistic effects !")

# Inputs for Radius and Circular Speed
col1, col2, col3, col4 = st.columns(4)

with col1:
    radius = st.number_input("Radius", help='Enter the physical radius of the object in the appropriate units. Note that this is treated independently of the major and minor axes when using the inclination correction !')

with col2:
    radius_unit = st.selectbox("Radius unit", ("m", "pc", "kpc"), index=2)

with col3:
    circular_speed = st.number_input("Circular speed", help='Here either enter the circular speed directly (if known) or half the line width if you need to correct for inclination angle')

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
	
	
# Inclination correction for velocity. Retrieves inclination angles from the GUI, but since velocity may 
# be calculated from the other parameters, it must be an input parameter here
def incvel(rawvel):
	# Thin disc correction
	if simple_i == 0.0:
		thindisc_vcorr = None
	else:
		thindisc_vcorr = rawvel / maths.sin(maths.radians(simple_i))
		
	if complex_i == 0.0:
		thickdisc_vcorr = None
	else:
		thickdisc_vcorr = rawvel / maths.sin(maths.radians(complex_i))

	# Values are set to None if incalculable. Since these are the defaults used for the local variables 
	# in the main code, this avoids some extra checks that the calculation was done
		
	return thindisc_vcorr, thickdisc_vcorr
	

# Option inclination angle correction
correctangle = st.toggle('Inclination correction', help='Enable this if you need to correct for the inclination angle. Only applies if the circular speed is input directly, not if calculated from other parameters')

if correctangle == True:
	st.write("Enter either the major and minor axis dimensions, or directly the axial ratio b/a if known. If a, b and q are all entered, q will be calculated from the a and b entries. You'll also need the intrinstic axial ratio and a systematic correction. Note that as well as the standard Hubble estimate, the inclination will also be estimated assuming a simple thin circular disc.")
	st.write("The inclination correction will only be applied in the case that velocity is known, not when calculated from mass and radius.")

	col1, col2, col3, col4, col5 = st.columns(5)
	
	with col1:
		majoraxis = st.number_input('a', help="Major axis. Units don't matter as long as they're consistent with the minor axis", min_value=0.0)
	with col2:
		minoraxis = st.number_input('b', help="Minor axis. Units don't matter as long as they're consistent with the major axis", min_value=0.0)
	with col3:
		axialratio_obs = st.number_input('q', help="Observed axial ratio. If you already know this enter it here, otherwise fill in the a and b parameters. This value will only be used if either a or b are zero", min_value=0.0, max_value=1.0)
	with col4:
		axialratio_act = st.number_input('q0', help="Intrinsic axial ratio - the axial ratio which would be observed if face-on. Generally assumed to be between 0.1 and 0.2", value=0.2, min_value=0.0, max_value=1.0)
	with col5:
		sys_i = st.number_input('Systematic', help="Systematic angle correction in degrees. Inclination angles tend to give values which are slightly too low. Generally a correction of 3 degrees is applied", value=3.0, min_value=0.0, max_value=90.0)


	# Thin circular disc estimate. Set to a default of zero and calculate if possible. This will be shown to the user in an (editable)
	# parameter input box below
	thindisc_i = 0.0
	
	# a, b both known : use this to calculate q. Ignore the value of q in the input box.
	if (majoraxis != 0.0 and minoraxis != 0.0) and (majoraxis >= minoraxis):
		axialratio_obs = minoraxis/majoraxis
		
	# But if q is known and either a or b are unknown, use the input q value
	if (majoraxis == 0.0 or minoraxis == 0.0) and axialratio_obs != 0.0:
		axialratio_obs = axialratio_obs
	
	# As long as the ratio is non-zero, we can calculate inclination angle	
	if axialratio_obs != 0.0:
		thindisc_i = maths.degrees(maths.acos(axialratio_obs))
		
		
	# Complex calculation
	thickdisc_i = 0.0
	
	# Add some tolerance : if we use exactly one, rounding errors cause problems when the input a and b
	# values are seemingly exactly equal
	if axialratio_obs <= (1.0-0.0001) and axialratio_obs > 0.0:
		thickdisc_i = maths.degrees(maths.sqrt(maths.acos( (axialratio_obs**2.0 - axialratio_act**2.0) / (1.0 - axialratio_act**2.0) ))) + sys_i
	
	
	# Manual inputs for inclination angles. These are what's actually used in the calculations. If the
	# user re-enters (BOTH) a and b values, the GUI gets updated automatically
	col1, col2, col3 = st.columns([2,1,1])
	
	with col1:
		st.write('Alternatively, enter inclination angle directly, overriding any previous calculations (you can adjust either or both of the thin and thick disc angles).')
		
	with col2:
		simple_i = st.number_input('Thin disc i', help="Thin disc approximation of i", min_value=0.0, max_value=90.0, value=thindisc_i)
		
	with col3:
		complex_i = st.number_input('Thick disc i', help="Thick disc approximation of i", min_value=0.0, max_value=90.0, value=thickdisc_i)		

	

# Do calculation only if two inputs are non-zero and the other is zero
input_values = [radius, circular_speed, dynamical_mass]
non_zero_count = sum(1 for value in input_values if value != 0.0)


if non_zero_count == 2:
	# Mass for the case of no inclination correction will always be known or calculated, but need to set
	# the variables for the case when inclination correction is applied
	mass_si_thin_i = None
	mass_si_thick_i = None
	# Same for velocity
	thin_vel  = None
	thick_vel = None

	# If only the radius is unknown, use the given values for mass and velocity and calculate radius
	if radius == 0.0:
		# Get mass and velocity in SI units
		mass_si_no_i = mass_kg(dynamical_mass, dynamical_mass_unit)
		vcir_si = circular_ms(circular_speed, circular_speed_unit)
		
		# Calculate radius in SI units, using the astropy constant for G
		r_si = (G.value*mass_si_no_i)/(vcir_si*vcir_si)
			
	# If only the circular speed is unknown, use the given values for mass and radius and calculate speed			
	elif circular_speed == 0.0:
		# Get mass and radius in SI units
		mass_si_no_i = mass_kg(dynamical_mass, dynamical_mass_unit)
		r_si    = distance_metres(radius, radius_unit)
		
		# Calculate circular speed in SI units
		vcir_si = maths.sqrt((G.value*mass_si_no_i)/r_si)
		
	# If only the dynamical mass is unknown, use the given values for radius and speed and calculate mass	
	elif dynamical_mass == 0.0:
		# Get the radius and speed in SI units
		r_si    = distance_metres(radius, radius_unit)
		vcir_si = circular_ms(circular_speed, circular_speed_unit)
		
		# Might need to correct for inclination angle
		if correctangle == True:
			thin_vel, thick_vel = incvel(vcir_si)
			print('Velocities =', thin_vel, thick_vel)
		
		# Calculate mass in SI units
		# 1) No inclination correction
		mass_si_no_i = ((vcir_si*vcir_si)*r_si) / G.value
		# 2) Thin disc correction
		if thin_vel != None:
			mass_si_thin_i = ((thin_vel*thin_vel)*r_si) / G.value
		# 2) Thick disc correction
		if thick_vel != None:
			mass_si_thick_i = ((thick_vel*thick_vel)*r_si) / G.value

		

	# Convert everything to standard astronomical conventions (everything at this stage is currently in SI
	# units)
	# 1) Mass, for the case of no, thin, and thick disc inclination corrections
	# a) No inclinatnion correction
	mass_ac_no_i  = mass_si_no_i/M_sun.value
	mass_acl_no_i = maths.log10(mass_ac_no_i)
	# b) Thin disc correction
	if mass_si_thin_i is not None:
		mass_ac_thin_i  = mass_si_thin_i/M_sun.value
		mass_acl_thin_i = maths.log10(mass_ac_thin_i)
	# c) Thick disc correction
	if mass_si_thick_i is not None:
		mass_ac_thick_i  = mass_si_thick_i/M_sun.value
		mass_acl_thick_i = maths.log10(mass_ac_thick_i)	
	
	vcir_ac  = vcir_si/1000.0
	if thin_vel is not None:
		thin_vel_ac = thin_vel/1000.0
	if thick_vel is not None:
		thick_vel_ac = thick_vel/1000.0		
	r_ac     = r_si/pc.value
	r_ack    = r_ac/1000.0


	# Print the values, first in a sensible format using standard astronomical conventional units
	st.write('##### Values in astronomer-friendly format :')
	if correctangle == True:
		st.write('**Essential notes :** Inclination corrections are only applied for angles greater than 0&deg;. Inclination corrections are generally considered unreliable at angles < 30&deg;, and may produce unphysical velocities are angles less than a few degrees. Thick disc corrections are highlighted **in bold** as they should be more accurate.')
	
	# For radius, use kpc if more than 500 pc
	if r_ac <= 500.0:
		st.write('Radius :',nicenumber(r_ac),'pc')
	if r_ac > 500.0:
		st.write('Radius :',nicenumber(r_ack),'kpc')
		
	# Similarly for circular speed, revert to m/s if less than 500 km/s.
	if vcir_si <= 500.0:
		if correctangle == True:
			st.write('Circular speed (no inclination correction):',nicenumber(vcir_si),'m/s')
		else:
			st.write('Circular speed :',nicenumber(vcir_si),'m/s')
		if thin_vel is not None :
			st.write('Circular speed (thin circular disc):',nicenumber(thin_vel),'m/s')
		if thick_vel is not None :
			st.write('**Circular speed (thick circular disc):',nicenumber(thick_vel),'m/s**')	
	if vcir_si > 500.0:
		if correctangle == True:
			st.write('Circular speed (no inclination correction):',nicenumber(vcir_ac),'km/s')
		else:
			st.write('Circular speed :',nicenumber(vcir_ac),'km/s')	
		if thin_vel is not None :
			st.write('Circular speed (thin circular disc):',nicenumber(thin_vel_ac),'km/s')
		if thick_vel is not None :
			st.write('**Circular speed (thick circular disc):',nicenumber(thick_vel_ac),'km/s**')		
	
	# Finally, give dynamical mass in both linear and logarithmic units	
	if correctangle == True:
		st.write('Dynamical mass (no inclination correction) :',nicenumber(mass_ac_no_i),'linear M<sub style=custom_style>&#9737;</sub> ('+str(nicenumber(mass_acl_no_i)+' logarithmic M<sub style=custom_style>&#9737;</sub>)'), unsafe_allow_html=True)
		if mass_si_thin_i is not None:
			st.write('Dynamical mass (thin circular disc) :', nicenumber(mass_ac_thin_i),'linear M<sub style=custom_style>&#9737;</sub> ('+str(nicenumber(mass_acl_thin_i)+' logarithmic M<sub style=custom_style>&#9737;</sub>)'), unsafe_allow_html=True)
		if mass_si_thick_i is not None:
			st.write('**Dynamical mass (thick circular disc) :', nicenumber(mass_ac_thick_i),'linear M<sub style=custom_style>&#9737;</sub> ('+str(nicenumber(mass_acl_thick_i)+' logarithmic M<sub style=custom_style>&#9737;</sub>)**'), unsafe_allow_html=True)
	else :
		st.write('Dynamical mass :',nicenumber(mass_ac_no_i),'linear M<sub style=custom_style>&#9737;</sub> ('+str(nicenumber(mass_acl_no_i)+' logarithmic M<sub style=custom_style>&#9737;</sub>)'), unsafe_allow_html=True)
	
	
	st.write('##### Exact values in SI units :')
	st.write('Radius :',str(r_si),'m')
	if correctangle == True:
		st.write('Circular speed (no inclination correction) :',str(vcir_si),'m/s')
		if thin_vel is not None:
			st.write('Circular speed (thin circular disc) :',str(thin_vel),'m/s')
		if thick_vel is not None:
			st.write('**Circular speed (thick circular disc) :',str(thick_vel),'m/s**')	
	else:
		st.write('Circular speed :',str(vcir_si),'m/s')
		
	if correctangle == True:
		st.write('Dynamical mass (no inclination correction) :',str(mass_ac_no_i),'kg')
		if mass_si_thin_i is not None:
			st.write('Dynamical mass (thin circular disc) :',str(mass_si_thin_i),'kg')
		if mass_si_thick_i is not None:
			st.write('**Dynamical mass (thick circular disc) :',str(mass_si_thick_i),'kg**')
	else:
		st.write('Dynamical mass :',str(mass_ac_no_i),'kg')

else:
	st.write("Please enter non-zero values for exactly two inputs from radius, circular speed and dynamical mass.")
