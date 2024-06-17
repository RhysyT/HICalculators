# Converts between different velocity systems. If the user has only the frequency, they must provide
# the rest frequency for the line as well. Gives access to Splatalogue.
# Returns the optical, radio, and relativisitic velocities, as well as frequency and redshift.

import numpy
import astropy
from astropy import units as u
import math
import imp
import streamlit as st
from streamlit.components.v1 import html
from astropy import constants

# Speed of light in m/s
c = constants.c.value

# External script imported as function
# Returns human-readable versions of numbers, e.g, comma-separated or scientific notation depending on size
import NiceNumber
imp.reload(NiceNumber)
from NiceNumber import nicenumber

# User can provide :
# Velocity
# Frequency
# Redshift
# They can request the redshifted values of :
# Frequency
# Wavelength
# Velocity (optical, radio, relativisitc)
# Redshift


# Standard conversion routine. Calculation of the rest/observed frequency, if not provided directly, is done within the main code.
# This part does the standard conversions to all the other possible values. 
# NOTE : Both input values must be real numbers in units of Hz, not astropy objects containing the unit types.
def conversion(restfreq, obsfrq):
	# Set up the equivalences for the conversion of the observed values
	restfreq = restfreq*u.Hz
	obsfrq = obsfrq*u.Hz
	
	freq_to_radvel = u.doppler_radio(restfreq)
	freq_to_optvel = u.doppler_optical(restfreq)
	freq_to_relvel = u.doppler_relativistic(restfreq)
													 
	# Calculate observed optical, radio, relativistic velocities
	obsoptvel = (obsfrq).to(u.km / u.s, equivalencies=freq_to_optvel)
	obsradvel = (obsfrq).to(u.km / u.s, equivalencies=freq_to_radvel)
	obsrelvel = (obsfrq).to(u.km / u.s, equivalencies=freq_to_relvel)
											
	# Calculate observed redshift (unless specified already)
	if obstype != 'Redshift':
		redshift = (restfreq.value - obsfrq.value) / restfreq.value
	if obstype == 'Redshift':
		redshift = obsvalue
		
	restfrq_astro = restfreq
	waveval_astro = (restfrq_astro).to(u.m, equivalencies=u.spectral())
	
	# *** DEPRECATED. Since the input is always in Hz (unitless real number), there is no point in
	# using the GUI value - the input has already been standardised ! ***
	
	# Calculate observed wavelength. Need to have this here with the astropy units for the equivalencies
	# to work. Below, this is converted to a real number for the wavelength calculation itself.
	# This assumes implicitly that the unit type is frequency. This is a safe assumption as this routine
	# is only invoked if the unit-types are compatible.
	#if restunits == 'Hz':
	#	restfrq_astro   =  restvalue * u.Hz
	#	waveval_astro   =  (restfrq_astro).to(u.m, equivalencies=u.spectral())

	#if restunits == 'kHz':
	#	restfrq_astro   =  restvalue * 1000.0 * u.kHz
	#	waveval_astro   =  (restfrq_astro).to(u.m, equivalencies=u.spectral())
	
	#if restunits == 'MHz':
	#	restfrq_astro   =  restvalue * 1E6 * u.MHz
	#	waveval_astro   =  (restfrq_astro).to(u.m, equivalencies=u.spectral())
		
	#if restunits == 'GHz':
	#	restfrq_astro   =  restvalue * 1E9 * u.GHz
	#	waveval_astro   =  (restfrq_astro).to(u.m, equivalencies=u.spectral())

	#if restunits == 'THz':
	#	restfrq_astro   =  restvalue * 1E12 * u.THz
	#	waveval_astro   =  (restfrq_astro).to(u.m, equivalencies=u.spectral())
		
	# For user input of frequency we use the unit boxes as above. When the user inputs wavelength,
	# we have to assume the rest frequency provided here is in Hz.
	#if resttype == 'Wavelength':
	#	restfrq_astro = restfreq #* u.Hz
	#	waveval_astro   =  (restfrq_astro).to(u.m, equivalencies=u.spectral())
		
	waveval  = waveval_astro.value
					
	# Calculate redshifted wavelength
	redwave = (redshift*waveval) + waveval
			
	return redshift, redwave, obsoptvel, obsradvel, obsrelvel



# STREAMLIT STYLE
# Remove the menu button
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

# Remove vertical whitespace padding
st.write('<style>div.block-container{padding-top:0rem;}</style>', unsafe_allow_html=True)
st.write('<style>div.block-container{padding-bottom:0rem;}</style>', unsafe_allow_html=True)

st.write("# Whose Spectral Line Is It Anyway ?")
st.write("### Calculate spectral line frequency, redshift and velocities")
st.write("Calculates the frequency of a spectral line at a given redshit, velocity, or wavelength, or vice-vera. Allows for different units and velocity conventions. Reference information on the different velocities can be found [here](https://science.nrao.edu/facilities/vla/docs/manuals/obsguide/modes/line). Some example values for the HI line are illustrated below.")

st.image('AGESRuler.png')


# Dictionary for line frequencies, all in Hz. Here we set the default dictionary, which assumes the user has chosen frequency with units of Hz.
# Later the dictionary will be updated if the user chooses other unit/types, hence we need to use the st.session_state to preseve the variable,
# rather than just setting its value in the usual way.
if 'linefs' not in st.session_state:
	st.session_state['linefs'] = {'HI':1420.40575E6, 'CO(1-0)':115.27120180E9, 'CO(2-1)':230.53800000E9, 'Custom':0.0, 'Splatalogue':0.0}


# REST VALUES
st.write("#### Rest value of the line")
st.write('Enter the numerical value of the rest frequency or wavelength of the line. You can also use the drop-down menu to choose from some preset lines, or access the Splatalogue database. Note that units must be consistent, e.g. frequency must use Hz, kHz, etc.')

# Define the columns to hold the widgets
left_column, left_mid_column, right_mid_column, right_column = st.columns(4)

with left_column:
	presetlines = st.selectbox('Line', ('HI', 'CO(1-0)', 'CO(2-1)', 'Custom', 'Splatalogue'), key="linepicker", help="Choose a present spectral line, specify a custom value, or access the Splatalogue database. If you alter the units or unit types, reselect the line in this menu to update its rest value.")
	
with left_mid_column:
	restvalue = st.number_input("Rest value", format="%.6f", min_value = 0.0, value=st.session_state['linefs'][presetlines], key="linevalue", step=1.0, help='Specify the numerical value of the rest frequency or wavelength, according to the menus on the right')

with right_mid_column:
	resttype = st.selectbox('Rest unit type', ('Frequency', 'Wavelength'), key="resttype", help='Choose whether the rest value refers to frequency or wavelength')
	
with right_column:
	restunits = st.selectbox('Rest units', ('Hz', 'kHz', 'MHz', 'GHz', 'THz', 'm', 'cm', ), key="restunits", help='Specify the rest value units')
 

# Now we update the line frequencies dictionary according to the user's parameters
if resttype == 'Frequency':
	if restunits == 'kHz':
		st.session_state['linefs'] = {'HI':1420.40575E3, 'CO(1-0)':115.27120180E6, 'CO(2-1)':230.53800000E6, 'Custom':0.0, 'Splatalogue':0.0}

	if restunits == 'MHz':
		st.session_state['linefs'] = {'HI':1420.40575, 'CO(1-0)':115.27120180E3, 'CO(2-1)':230.53800000E3, 'Custom':0.0, 'Splatalogue':0.0}
		
	if restunits == 'GHz':
		st.session_state['linefs'] = {'HI':1420.40575E-3, 'CO(1-0)':115.27120180, 'CO(2-1)':230.53800000, 'Custom':0.0, 'Splatalogue':0.0}
		
	if restunits == 'THz':
		st.session_state['linefs'] = {'HI':1420.40575E-6, 'CO(1-0)':115.27120180E-3, 'CO(2-1)':230.53800000E-3, 'Custom':0.0, 'Splatalogue':0.0}

if resttype == 'Wavelength':
	if restunits == 'm':
		st.session_state['linefs'] = {'HI':0.2110611408043089, 'CO(1-0)':0.0026007576334647012, 'CO(2-1)':0.0013004036557964413, 'Custom':0.0, 'Splatalogue':0.0}

	if restunits == 'cm':
		st.session_state['linefs'] = {'HI':21.10611408043089, 'CO(1-0)':0.26007576334647012, 'CO(2-1)':0.13004036557964413, 'Custom':0.0, 'Splatalogue':0.0}

# If the user chooses Splatogoue as the preset line, open the webpage
if presetlines == 'Splatalogue':
	open_script= """
	<script type="text/javascript">
	window.open('%s', '_blank').focus();
	</script>
	""" % ('https://www.splatalogue.online/#/home')
	html(open_script)

	
# OBSERVED VALUES
st.write("#### Observed value of the line")
st.write('Enter the numerical value of the observed frequency, wavelength, velocity, or redshift of the line. This will then calculate the other values.')

# Define the columns
left_column, mid_column, right_column = st.columns(3)

with left_column:
	obsvalue = st.number_input("Observed value", format="%.6f", min_value = 0.0, value=1420405750.000000, key="lineobsvalue", step=1.0, help='Specify the numerical value of the observed frequency, wavelength, or redshift, according to the menus on the right')

with mid_column:
	obstype = st.selectbox('Observed unit type', ('Frequency', 'Wavelength', 'Redshift', 'Optical velocity', 'Radio velocity', 'Relativistic velocity'), key="obstype", help='Choose whether the observed value refers to frequency, wavelength, or redshift')
	
with right_column:
	obsunits = st.selectbox('Observed units', ('Hz', 'kHz', 'MHz', 'GHz', 'THz', 'm', 'cm', 'None', 'km/s', 'm/s'), key="obsunits", help='Specify the observed value units, or use "None" for redshift')


# Default is to assume units are mistmatched
inpunitmatch = False
outunitmatch = False

# 1) Check INPUT units are consistent
if resttype == 'Frequency':
	if restunits in ['Hz', 'kHz', 'MHz', 'GHz', 'THz']:
		inpunitmatch = True
		
if resttype == 'Wavelength':
	if restunits in ['m', 'cm']:
		inpunitmatch = True
		
# 2) Check OUPTUT units are consistent
if obstype == 'Frequency':
	if obsunits in ['Hz', 'kHz', 'MHz', 'GHz', 'THz']:
		outunitmatch = True
		
if obstype == 'Wavelength':
	if obsunits in ['m', 'cm']:
		outunitmatch = True
		
if obstype == 'Redshift':
	if obsunits == 'None':
		outunitmatch = True
		
if obstype in ['Optical velocity', 'Radio velocity', 'Relativistic velocity']:
	if obsunits in ['km/s', 'm/s']:
		outunitmatch = True
		

# If there is a mismatch in the input units/type, print a warning
if inpunitmatch == False :
	st.write('#### Ensure units match the type !')
	st.write('For example if using frequency, the unit type must be Hz, MHz, etc.; if using wavelength it must be m or cm. Input and output values can be different from each other but must be self-consistent.')
	st.write('Calculations will be printed here automatically when the units are consistent.')

# If the inputs are consistent, do the calculations
if inpunitmatch == True: 
	st.write('#### Standardised rest line values')
	
	# Rest values of wavelength and frequency, in astropy composite units
	wavel = None
	frqvl = None
	
	# 1) First get standardised values for the rest frequency in Hz and the wavelength in m. We do this just so we
	# can print the rest wavelength here, in case that wasn't entered (or vice-versa).
	# A) If the user specifies frequency for the rest value :
	if resttype == 'Frequency':
		
		# Multiply by e.g. "u.MHz" to attach the unit, required for other astropy processing. Note that this does
		# not affect the numerical value ! So if we give it a numerical entry of 100.0, that will become 100 Hz,
		# 100 MHz, etc. However this DOES affect the conversion afterwards, e.g. 100 MHz converted to Hz will
		# indeed be 100 million Hz.
		if restunits == 'Hz':
			frqvl   =  restvalue * u.Hz
			wavel   =  (frqvl).to(u.m, equivalencies=u.spectral())

		if restunits == 'kHz':
			frqvl   =  restvalue * u.kHz
			wavel   =  (frqvl).to(u.m, equivalencies=u.spectral())
	
		if restunits == 'MHz':
			frqvl   =  restvalue * u.MHz
			wavel   =  (frqvl).to(u.m, equivalencies=u.spectral())
		
		if restunits == 'GHz':
			frqvl   =  restvalue * u.GHz
			wavel   =  (frqvl).to(u.m, equivalencies=u.spectral())

		if restunits == 'THz':
			frqvl   =  restvalue * u.THz
			wavel   =  (frqvl).to(u.m, equivalencies=u.spectral())

		# Likely impossible that we can't calculate the wavelength thanks to the unit consistency check, but no
		# harm including this additional safety check in case it couldn't be calculated
		if wavel == None:
			st.write('### Error : rest unit/type mismatch !')
		# If everything is good, we can now just print the values in standardised units
		else:			
			waveln  = wavel.value	
			frqvln  = frqvl.to(u.Hz).value	#		(frqvl.value * u.Hz).value
			
			st.write('Rest wavelength :',str(waveln),'m')
			st.write('Rest frequency  :',str(frqvln),'Hz')
									
	
	# B) As above, but for the case where the user specifies wavelength for the rest value :
	if resttype == 'Wavelength':
		
		if restunits == 'm':
			wavel   =  restvalue * u.m
			frqvl = (wavel).to(u.Hz, equivalencies=u.spectral())
			
		if restunits == 'cm':
			wavel   =  restvalue * u.cm
			frqvl = (wavel).to(u.Hz, equivalencies=u.spectral())			
		
		if wavel == None:
			st.write('### Error : rest unit/type mismatch !')
		else:			
			waveln  = wavel.value	
			frqvln  = (frqvl.value * u.Hz).value
			
			st.write('Rest wavelength :',str(waveln),'m')
			st.write('Rest frequency  :',str(frqvln),'Hz')
			
	
	
	# 2) Now we can convert the redshifted value to all the other units, as long as the units match
	if outunitmatch == False:
		st.write('#### Output units must be self-consistent to calculate redshifted values.')
		
	if wavel != None and outunitmatch == True:
		st.write('###')
		st.write('#### Redshifted values')
		
		# A) Redshifted value is frequency
		if obstype == 'Frequency': #and obsunits in ['Hz', 'kHz', 'MHz', 'GHz', 'THz']:			
			restfreq = frqvln
			
			# We already have the rest frequency (frqvl.value) in Hz. We just need to get the redshifted frequency value,
			# accounting for the user-specified units.
			if obsunits == 'Hz':
				obsfrq = obsvalue * 1.0
			if obsunits == 'kHz':
				obsfrq = obsvalue * 1000.0 	
			if obsunits == 'MHz':
				obsfrq = obsvalue * 1E6	
			if obsunits == 'GHz':
				obsfrq = obsvalue * 1E9 
			if obsunits == 'THz':
				obsfrq = obsvalue * 1E12
			
			# Do the conversions
			redshift, redwave, obsoptvel, obsradvel, obsrelvel = conversion(restfreq, obsfrq)
			
			st.write('Redshifted **optical** velocity :',str(obsoptvel))
			st.write('Redshifted **radio** velocity :',str(obsradvel))
			st.write('Redshifted **relativisitic** velocity :',str(obsrelvel))			
			st.write('Redshift :',str(redshift))			
			st.write('Redshifted wavelength :',str(redwave),'m')
			
	
		# B) Redshifted value is wavelength 
		if obstype == 'Wavelength' and obsunits in ['cm', 'm']:
			# Convert to redshifted frequency
			if obsunits == 'cm':
				redwfrq = (obsvalue * u.cm).to(u.Hz, equivalencies=u.spectral())
			if obsunits == 'm':
				redwfrq = (obsvalue * u.m).to(u.Hz, equivalencies=u.spectral())
							
			# Now we can repeat the case of frequency !		
			redshift, redwave, obsoptvel, obsradvel, obsrelvel = conversion(frqvln, redwfrq.value)
			
			st.write('Redshifted **optical** velocity :',str(obsoptvel))
			st.write('Redshifted **radio** velocity :',str(obsradvel))
			st.write('Redshifted **relativisitic** velocity :',str(obsrelvel))
			st.write('Redshift :',str(redshift))
			st.write('Redshifted wavelength :',str(redwave),'m')
			
			
		# C) Redshifted value is redshift
		if obstype == 'Redshift' and obsunits == 'None':
			redfrq = frqvln / (1.0 + obsvalue)
		
			redshift, redwave, obsoptvel, obsradvel, obsrelvel = conversion(frqvln, redfrq)
			
			st.write('Redshifted **optical** velocity :',str(obsoptvel))
			st.write('Redshifted **radio** velocity :',str(obsradvel))
			st.write('Redshifted **relativisitic** velocity :',str(obsrelvel))
			st.write('Redshift :',str(redshift))
			st.write('Redshifted wavelength :',str(redwave),'m')
		
		
		# D) Redshifted value is optical velocity
		if obstype == 'Optical velocity' and obsunits in ['m/s', 'km/s']:
			if obsunits == 'm/s':
				waveobs = (obsvalue / c)*waveln + waveln
			
			if obsunits == 'km/s':
				waveobs = (obsvalue*1000.0 / c)*waveln + waveln
			
			fobs = (waveobs * u.m).to(u.Hz, equivalencies=u.spectral())
			
			redshift, redwave, obsoptvel, obsradvel, obsrelvel = conversion(frqvln, fobs.value)
			
			st.write('Redshifted **optical** velocity :',str(obsoptvel))
			st.write('Redshifted **radio** velocity :',str(obsradvel))
			st.write('Redshifted **relativisitic** velocity :',str(obsrelvel))
			st.write('Redshift :',str(redshift))
			st.write('Redshifted wavelength :',str(redwave),'m')			
		
		
		# D) Redshifted value is radio velocity
		if obstype == 'Radio velocity' and obsunits in ['m/s', 'km/s']:
			if obsunits == 'm/s':
				fobs = -1.0*((obsvalue / c)*frqvln - frqvln)
			
			if obsunits == 'km/s':
				fobs = -1.0*((obsvalue*1000.0 / c)*frqvln - frqvln)
						
			redshift, redwave, obsoptvel, obsradvel, obsrelvel = conversion(frqvln, fobs)
			
			st.write('Redshifted **optical** velocity :',str(obsoptvel))
			st.write('Redshifted **radio** velocity :',str(obsradvel))
			st.write('Redshifted **relativisitic** velocity :',str(obsrelvel))
			st.write('Redshift :',str(redshift))
			st.write('Redshifted wavelength :',str(redwave),'m')

		
		# E) Redshifted value is relativistic velocity
		if obstype == 'Relativistic velocity' and obsunits in ['m/s', 'km/s']:
			# Let v/c = k for simplicity
			if obsunits == 'm/s':
				k = obsvalue / c
				
			if obsunits == 'km/s':
				k = obsvalue*1000.0 / c	
				
			fobs = math.sqrt( (frqvln**2.0 * (k-1.0)) / (-1.0 - k))
			
			redshift, redwave, obsoptvel, obsradvel, obsrelvel = conversion(frqvln, fobs)
			
			st.write('Redshifted **optical** velocity :',str(obsoptvel))
			st.write('Redshifted **radio** velocity :',str(obsradvel))
			st.write('Redshifted **relativisitic** velocity :',str(obsrelvel))
			st.write('Redshift :',str(redshift))
			st.write('Redshifted wavelength :',str(redwave),'m')				
