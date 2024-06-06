# Program to calculate some simple parameters about source visibility, for observation planning

import numpy
import astropy
from astropy.coordinates import SkyCoord, AltAz, EarthLocation, SkyCoord, Angle
from astropy.time import Time
import astropy.units as ast_u
import datetime
from datetime import date, timedelta
import calendar
import streamlit as st
import math
from math import pi as pi
import imp
from timezonefinder import TimezoneFinder
import pytz

# External script imported as function
# Returns human-readable versions of numbers, e.g, comma-separated or scientific notation depending on size
import NiceNumber
imp.reload(NiceNumber)
from NiceNumber import nicenumber


# Angular separation calculator. Taken from astropy source code (later verison, this since this not included in 3.2.2; modified to assume inputs are radians)
def angular_separation(lon1, lat1, lon2, lat2):
    sdlon = numpy.sin(lon2 - lon1)
    cdlon = numpy.cos(lon2 - lon1)
    slat1 = numpy.sin(lat1)
    slat2 = numpy.sin(lat2)
    clat1 = numpy.cos(lat1)
    clat2 = numpy.cos(lat2)

    num1 = clat2 * sdlon
    num2 = clat1 * slat2 - slat1 * clat2 * cdlon
    denominator = slat1 * slat2 + clat1 * clat2 * cdlon

    return numpy.degrees(numpy.arctan2(numpy.hypot(num1, num2), denominator))


# STREAMLIT STYLE
# Remove the menu button
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

# Remove vertical whitespace padding
st.write('<style>div.block-container{padding-top:0rem;}</style>', unsafe_allow_html=True)
st.write('<style>div.block-container{padding-bottom:0rem;}</style>', unsafe_allow_html=True)


# Dictionaries for parameters preset by location
lativals = {"ALMA": -23.029,  "APEX": -23.003499986, "ASKAP": -26.9833294, "ATCA": -30.307665436, "Cardiff": 51.48, "Custom": 0.0, "Effelsberg": 50.521497914, "GBT": 38.4263699612,  "IRAM 30m": 37.0596964279,  "MeerKAT": -30.83, "NOEMA": 44.633664132, "Prague": 50.073658, "VLA": 38.990276}
longvals = {"ALMA": -67.755,  "APEX": -67.755330312, "ASKAP": 116.5333312, "ATCA": 149.550164466, "Cardiff": -3.18, "Custom": 0.0, "Effelsberg": 6.876329828,  "GBT": -79.8369766521, "IRAM 30m": -3.38896344414, "MeerKAT": 21.33,  "NOEMA": 5.904746381,  "Prague": 14.41854,  "VLA": -89.168335}
altvals  = {"ALMA": 5058.7,   "APEX": 5064.0,        "ASKAP": 361.0,       "ATCA": 237.0,         "Cardiff": 0.0,  "Custom": 0.0, "Effelsberg": 319.0,       "GBT":  807.43,        "IRAM 30m": 2850.0,         "MeerKAT": 1256.0, "NOEMA": 2550.0,       "Prague": 399.0,     "VLA": 2124.0}
mnelvals = {"ALMA": 0.0,      "APEX": 20.0,          "ASKAP": 15.0,        "ATCA": 12.0,         "Cardiff": 0.0,   "Custom": 0.0, "Effelsberg": 7.0,          "GBT":  5.0,           "IRAM 30m": 0.0,            "MeerKAT": 15.0,   "NOEMA": 3.0,          "Prague": 0.0,       "VLA": 8.0}
mxelvals = {"ALMA": 90.0,     "APEX": 80.0,          "ASKAP": 90.0,        "ATCA": 90.0,         "Cardiff": 90.0,  "Custom": 90.0, "Effelsberg": 89.0,         "GBT":  90.0,          "IRAM 30m": 90.0,           "MeerKAT": 89.0,   "NOEMA": 90.0,         "Prague": 90.0,      "VLA": 90.0}


# The preset parameters are fixed, but the source coordinates will vary. To ensure the widgets update the values correctly, store the source coordinate dictionary in
# the special session_state dictionary-like object. Only set it here if it doesn't already exist, to prevent it from overwriting the values set later.
if 'sourcecoords' not in st.session_state:
	st.session_state['sourcecoords'] = {"Galaxy": [0.0, 0.0]}
	


# MAIN CODE
# SITE PARAMETERS AND TELESCOPE CONSTRAINTS
st.write("# I Can See My Source From Here")
st.write("## Calculate source visibility during a given time at a given location")
st.write("Gives some simple information about whether a source is visible. Indicates if it's in daylight, close to the Sun, or outside of a specified elevation range. Prints out the source elevation every 15 minutes of the observing schedule in the browser and every minute in a text file. Designed for sources beyond the Solar System at fixed Right Ascension and Declination. **Accuracy unknown, use at own risk !**")

st.write('### Site and telescope parameters')

# Define the columns to hold the widgets
left_column, mid_column, right_column = st.columns(3) #st.columns([1,2,2]) - # List of size ratios of columns if we want them unequal sizes

# Left column : drop-down meny to choose preset site coordinates and telescope angles; site altitude.
with left_column:
	presetlocs = st.selectbox('Location', ('ALMA', 'APEX', 'ASKAP', 'ATCA', 'Cardiff', 'Custom', 'Effelsberg', 'GBT', 'IRAM 30m', 'MeerKAT', 'NOEMA', 'Prague', 'VLA'), key="obsloc", help='Choose from a preloaded list of locations (cities and telescopes) to automatically set observing latitude, longtiude and elevation. For telescopes this also sets the minimum and maximum elevation angles they can observe (when known)')
	sitealtitude = st.number_input("Altitude / m", format="%.2f", value=altvals[presetlocs], key="sitealtitude")

with mid_column:
	longitude = st.number_input("Longitude (+ve is East)", format="%.6f", min_value = -180.0, max_value=180.0, value=longvals[presetlocs], key="longitude", help='Longitude of the observing site in decimal degrees. Enter positive values for east and negative values for west')
	minelvangle = st.number_input("Min. telescope elevation / degrees", format="%.2f", min_value=0.0, max_value=90.0, value=mnelvals[presetlocs], key="minelvangle", help='Lowest angle above the horizon the telescope can point at. This is the hard limit of the telescope; for specific requirements on a particular source, see the "source parameters" section below')
	
with right_column:
	latitude = st.number_input("Latitude (+ve is North)", format="%.6f", min_value = -90.0, max_value=90.0, value=lativals[presetlocs], key="latitude", help='Latitude of the observing site in decimal degrees. Enter positive values for north and negative values for south')
	maxelvangle = st.number_input("Max. telescope elevation / degrees", format="%.2f", min_value=0.0, max_value=90.0, value=mxelvals[presetlocs], key="maxelvangle", help='Maximum angle above the horizon the telescope can point at. This is the hard limit of the telescope; for specific requirements on a particular source, see the "source parameters" section below')
	
	
# CHOOSE THE EXACT TIME AND DATE (LOCAL VALUES) WHEN THE OBSERVATIONS BEGIN AND END
st.write('### Scheduling parameters')

# Two columns. Left for beginning date and time, right for end date and time
left_column3, right_column3 = st.columns(2)

with left_column3:
	# Default start date is today and end date is tommorow 
	date_start = st.date_input("Observations begin (date in YYYY-MM-DD format)", date.today(), min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2100, 12, 31),)
	time_start = st.time_input('Observation start time (type to enter exact value)', value=datetime.time(0, 00), step=300, help='Start of local observing time in 24 hour format. Widget is in 5 minute intervals. For more exact values, type the entry in full')

with right_column3:	
	date_end = st.date_input("Observations finish (date in YYYY-MM-DD format)", date.today() + datetime.timedelta(days=1), min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2100, 12, 31))
	time_end = st.time_input('Observation end time', value=datetime.time(23, 59), step=300, help='End of local observing time in 24 hour format. Widget is in 5 minute intervals. For more exact values, type the entry in full')


# SOURCE COORDINATES AND OBSERVING CONSTRAINTS
st.write('### Source parameters')

left_column4, leftmid_column, rightmid_column, right_column4 = st.columns(4)

with left_column4:
	sourcename = st.text_input('Source name', 'E.g. M33', help='If the source is found in major catalogues, enter its name here and use the "resolve" button to retrieve its coordinates')
	minsangle  = st.number_input("Min. elevation / deg", format="%.2f", min_value=0.0, max_value=90.0, key="minsangle", help='Here you can specify the minimum elevation angle of the source above the horizon to be observable, independent of the telescope limits')
	
with leftmid_column:
	st.write('######')	# Empty padding so the button appears level
	nameresolve = st.button("Resolve", type="primary", help='Try and resolve the sky coordinates of the source', use_container_width=True)
	
	# We have to do the operation of the name resolve button here (or at least before the coordinate boxes are drawn) to update the dictionary properly
	if nameresolve == True:
		try:
			coords = SkyCoord.from_name(sourcename)
			st.session_state['sourcecoords']['Galaxy'] = [coords.ra.deg, coords.dec.deg]
		except:
			pass
				
	maxsangle  = st.number_input("Max. elevation / deg", format="%.2f", min_value=0.0, max_value=90.0, value=90.0, key="maxsangle", help='Here you can specify the maximum elevation angle of the source above the horizon to be observable, independent of the telescope limits')
		
with rightmid_column:
	sourceracoord  = st.number_input("Source RA / J2000", format="%.6f", min_value=0.0, max_value=360.0, value=st.session_state['sourcecoords']['Galaxy'][0], key="sourceracoord")
	maxsunang = st.number_input("Max. Sun angle / deg", format="%.2f", min_value=0.0, max_value=180.0, key="maxsunangle", help='Maximum safe angular separation of the source and the Sun (in degrees)')	
	
with right_column4:
	sourcedeccoord = st.number_input("Source Dec / J2000", format="%.6f", min_value=-90.0, max_value=90.0, value=st.session_state['sourcecoords']['Galaxy'][1], key="sourcedeccoord")
	#st.write('######')	# Empty padding so the button appears level
	docalc = st.button("Calculate", type="primary", help='Find out if you can see your source from here !', use_container_width=True)


# Additional functionality when the name resolve button pressed. Write the error message if a source couldn't be resolved - do this here to avoid messing up the
# GUI arrangement	
if nameresolve == True:
	try:
		coords = SkyCoord.from_name(sourcename)
	except:
		st.write('Sorry, couldn\'t find that source !')		



# CALCULATE VISIBILITIES !
if docalc == True:
	# Convert the observatory coordinates into an astropy location
	astropy_loc = EarthLocation(lat=latitude*ast_u.deg, lon=longitude*ast_u.deg, height=sitealtitude*ast_u.m)
	
	# Convert the RA/Dec into an astropy SkyCoord object
	OurSource = SkyCoord(ra=sourceracoord*ast_u.deg, dec=sourcedeccoord*ast_u.deg)
	
	# Get its RA and Dec in radians for the angular separation calculation
	OurSourceRArad  = numpy.radians(OurSource.ra.deg)
	OurSourceDecrad = numpy.radians(OurSource.dec.deg)


	# Time/data conversions so we can have both local and universal times. First get the initial and final dates and times as datetime objects :
	initialdatetime = datetime.datetime.combine(date_start, time_start)
	finaldatetime   = datetime.datetime.combine(date_end, time_end)
	
	# Set a variable we can advance
	currentdatetime = initialdatetime
	
	# Now get the time zone so we can convert local times to UST
	tf = TimezoneFinder()
	timezone_str = tf.timezone_at(lng=longitude, lat=latitude)

	# Create a timezone object from the region/city name
	timezone_obj = pytz.timezone(timezone_str)
	
	# Counter to tell if we should output to the GUI or not. GUI output enabled whenever zero. Reset to zero every 15 minutes.
	# Text file is output every minute so doesn't need its own counter.
	minutecount = 0
	
	
	# Check for errors before doing any calculations
	okaytoproceed = True
	
	# First ensure the end is after the beginning :
	if finaldatetime <= currentdatetime:
		okaytoproceed = False
		st.write('### Observations must end after they begin !')
	
	# Also ensure the angles are compatible
	if minelvangle >= maxelvangle:
		okaytoproceed = False
		st.write('### Telescope maximum elevation angle must be above the minimum !')	
	if minsangle >= maxsangle:
		okaytoproceed = False
		st.write('### User maximum elevation angle must be above the minimum !')		
	
	
	# If no errors, proceed
	if okaytoproceed == True:
		# Print out a header to the screen
		st.write('## Calculation Results')
		st.write('### Scroll to end to download ASCII version')
		st.write('Times and dates are LOCAL and all angles are in decimal degrees. Dates are in YYYY-MM-DD format.')
		st.markdown(f"**Source Altitude : {':red['}RED]** means below the horizon or outside the telescope viewing angles. <br> **{':orange['}ORANGE]** means within the telescope capabilities but outside the user specifications. <br> **{':green['}GREEN]** means the source is within both the telescope and user specifications.", unsafe_allow_html=True)
		st.markdown(f"**Sun Altitude : {':orange['}ORANGE]** means the Sun is above the horizon. <br> **{':violet['}PURPLE]** means astronomical twilight. <br> **{':green['}GREEN]** means full astronomical dark.", unsafe_allow_html=True)
		st.markdown(f"**Sun Separation : {':red['}RED]** means the Sun is closer than the user-specified threshold. <br> **{':green['}GREEN]** means the Sun is further away than the user-specified threshold.", unsafe_allow_html=True)
	
		st.markdown(f"#### {currentdatetime.date()} {calendar.day_name[currentdatetime.weekday()]}")
		st.markdown('##### Time $~~$ Source Altitude $~~$ Sun Altitude $~~$ Sun Ang. Separation')

		# More compact Header for  text file	
		ObsFileString = '#Source='+sourcename+', RA='+str(OurSource.ra.deg)+', Dec='+str(OurSource.dec.deg)+', MinAltAllowed='+str(minsangle)+', MaxAltAllowed='+str(maxsangle)+'\n'
		ObsFileString = ObsFileString+'#Telescope : MinAngle='+str(minelvangle)+', MaxAngle='+str(maxelvangle)+', SunMaxAngle='+str(maxsunang)+'\n'
		ObsFileString = ObsFileString+'#Date-Time Day SourceAltitude SunAltitude SunAng.Separation Errors/Problems'+'\n'
		
		
	# Start at the beginning, incrementing in steps of one minute until we go beyond the end point
	while currentdatetime <= finaldatetime and okaytoproceed == True:
		# First we need to convert the current local to universal date and time. Localise :
		dt_local = timezone_obj.localize(currentdatetime)

		# Now we can find the UTC offset	
		offset = dt_local.utcoffset()
	
		# Convert it into hours
		offset_hours = offset.total_seconds() / 3600.0
		
		# Convert the current date and time into an astropy universal datet-time format
		universaltime = currentdatetime - timedelta(hours=offset_hours)
		observingtime = Time(universaltime)
		
		
		# Now we can find the alt/az of our source !
		SourceAltAz = OurSource.transform_to(AltAz(obstime=observingtime,location=astropy_loc))
		
		
		# Also get the coordinates of the Sun
		SunCoords = astropy.coordinates.get_sun(observingtime)
	
		# Extract the numerical values, get into radians for calculating angular separation
		SunRA =  numpy.radians(SunCoords.ra.deg)
		SunDec = numpy.radians(SunCoords.dec.deg)	
	
	
		# Get the sky separation of the source and Sun (source coordinates were found earlier)
		skysep = angular_separation(OurSourceRArad, OurSourceDecrad, SunRA, SunDec)
	
		# Get the solar altitude
		SunCoordsAltAz = SunCoords.transform_to(AltAz(obstime=observingtime,location=astropy_loc))		
		
		
		# Evaluate the parameters to set colours. Available colours are blue, green, orange, red, and violet.	
		# First set the default colours, assume everything's fine
		sourcecolour = ':green['
		suncolour   = ':green['
		sunsepcolor = ':green['
		
		# 1) Source altitude
		SourceAlt = SourceAltAz.alt.deg
		
		# Source below horizon : totally unobservable
		if SourceAlt < 0.0:
			sourcecolour = ':red['
			
		# Source below telescope minimum angle : totally unobservable
		if SourceAlt < minelvangle:
			sourcecolour = ':red['
		
		# Source above telescope minimum angle but below user's minimum angle : might be possible
		if SourceAlt >= minelvangle and SourceAlt < minsangle:
			sourcecolour = ':orange['
			
		# Source above user's maximim angle but below telescope's maximum angle : might be possible
		if SourceAlt >= maxsangle and SourceAlt < maxelvangle:
			sourcecolour = ':orange['
			
		# Source above telescope's maximum angle : totally unobservable
		if SourceAlt > maxelvangle:
			sourcecolour = ':red['
		
		
		# 2) Solar altitude
		SunCoordsAlt = SunCoordsAltAz.alt.deg
		
		# Sun less than 18 degrees below the horizon, astronomical twilight
		if SunCoordsAlt <= 0.0 and SunCoordsAlt > -18.0:
			suncolour   = ':violet['
		
		# Sun above horizon, might be possible to observe. No need to set if below the horizon as green by default
		if SunCoordsAlt > 0.0:
			suncolour   = ':orange['
			
			
		# 3) Solar separation less than the maximum angle, unobservable
		if skysep < maxsunang:
			sunsepcolor = ':red['
		
		
		# Need to report the worse problem as a comment in the text file, if any
		problems = '\"\"'
		# First consider the red cases for the source : either below the horizon or outside the telscope's viewing range
		if SourceAlt < 0.0:
			problems = '\"ERROR : Source below horizon\"'
		elif SourceAlt < minelvangle or SourceAlt > maxelvangle:
			problems = '\"ERROR : Source outside telescope viewing angles\"'
		
		# Next consider the red case for the Sun : closer than the specified viewing range. Only need to bother with this if the source had no major issues.
		if problems == '\"\"' and skysep < maxsunang:
			problems = '"ERROR : Source too close to the Sun"'
			
		# Now if we still haven't had any major problems, consider the orange/violet cases
		if problems == '\"\"' and sourcecolour == ':orange[':
			problems = '"WARNING : Source visible to telescope but outside user-specified angles"'
			
		if problems == '\"\"' and suncolour == ':violet[':
			problems = '"WARNING : Astronomical twilight"'

				
					
		# Only output to the screen every 15 minutes
		if minutecount == 0 or minutecount == 15:
			st.markdown(f":blue[{str(currentdatetime.time())}] $~~~~~~~~~$ {sourcecolour}{str(nicenumber(SourceAltAz.alt.deg)).zfill(6)}] $~~~~~~~~~~~~~~~~~~$ {suncolour}{str(nicenumber(SunCoordsAlt)).zfill(6)}] $~~~~~~~~~~~~~~~~~~~$ {sunsepcolor}{str(nicenumber(skysep)).zfill(6)}]")
		
		# Store similar information in the text file string		
		ObsFileString = ObsFileString+str(currentdatetime)+' '+str(calendar.day_name[currentdatetime.weekday()])+' '+str(nicenumber(SourceAltAz.alt.deg))+' '+str(nicenumber(SunCoordsAlt))+' '+str(nicenumber(skysep))+' '+problems+'\n'
		
		
		# Advance the time by one minute in a test variable
		nextdatetime = currentdatetime + timedelta(minutes=1)
		
		# If the day changes, print the new day and date to the screen
		if nextdatetime.date() != currentdatetime.date():
			st.markdown(f"### {nextdatetime.date()} {calendar.day_name[nextdatetime.weekday()]}")
			
		# Now advance the "actual" current time variable by one minute
		currentdatetime = currentdatetime + timedelta(minutes=1)
		
		# Increment the minute counter, reset every 15 minutes (this causes the screen printout above to work)
		minutecount = minutecount + 1
		
		if minutecount == 15:
			minutecount = 0
		
		
	# Only allow the download of the file contents if it was produced
	if okaytoproceed == True:
		st.download_button('Download ASCII text file', ObsFileString, file_name='MyObservations.txt')
