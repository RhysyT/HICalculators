import streamlit as st
import imp
import math as maths
import astroquery

from astroquery.irsa_dust import IrsaDust
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.coordinates import Angle

# EXTERNAL SCRIPTS IMPORTED AS FUNCTIONS
# "nicenumber" function returns human-readable versions of numbers, e.g, comma-separated or scientific notation depending
# on size
import NiceNumber
imp.reload(NiceNumber)
from NiceNumber import nicenumber


# Convert net counts to apparent magnitude
def countstomag(counts):
	if counts > 0.0:
		appmag = 22.5 - 2.5*maths.log10(counts)
	if counts <= 0.0:
		appmag = 0.0
	
	return appmag
	

# Convert apparent to absolute magnitude
def absmag(app, dist):
	if app != 0.0 and dist != 0.0:
		absolute_mag = -(5.0*maths.log10(dist*1E6) - 5.0 - app)
	else:
		absolute_mag = 0.0
			
	return absolute_mag
	
	
# Internal extinction calculator
def mag_int_correct(absmag, band, inc):
	# Convert inclination angle to radians
	angle_i = maths.radians(inc)
	
	# Now we can get the axis ratio
	b_over_a = maths.cos(angle_i)
	
	# The other part of this correction depends on waveband, if the absolute magnitude is bright enough. For faint
	# galaxies, no correction is applied
	if absmag >= -17.0:
		gamma = 0.0
		
	if absmag < -17.0:
		if band == 'g':
			gamma = -0.35*absmag - 5.95
		if band == 'i':
			gamma = -0.15*absmag - 2.55
	
	# Calculate the attenutation
	att_band = gamma*maths.log10(b_over_a)
	
	# Finally we get the corrected absolute magnitude
	absmag_intcorr = absmag + att_band

	return absmag_intcorr
	
	
# STELLAR MASS CALCULATIONS
# Absolute solar luminosities taken from : https://mips.as.arizona.edu/~cnaw/sun_2006.html
# All calculations take absolute, fully-corrected magnitudes as input.
# 1) Taylor et al. 2011 relation for g-i (used in Durbala 2020)
def stellarmass_T11(Mag_g, Mag_i):
	# Calculate i-band luminosity
	Mag_solar_i = 4.58
	Lsolar_i = 10.0**((Mag_i - Mag_solar_i)/-2.5)
	
	# Stellar mass
	Mstar = 10.0**( -0.68 + (0.70*(Mag_g - Mag_i)) + maths.log10(Lsolar_i))
	
	return Mstar

# 2) Bell et al. 2003 relation for g-i
def stellarmass_B03gi(Mag_g, Mag_i):
	# Calculate i-band luminosity
	Mag_solar_i = 4.58
	Lsolar_i = 10.0**((Mag_i - Mag_solar_i)/-2.5)
	
	# Stellar mass
	Mstar = 10.0**( -0.379 + (0.914*(Mag_g - Mag_i)) + maths.log10(Lsolar_i))
	
	return Mstar	
	
	
# 3) Bell et al. 2003 relation for g-r
def stellarmass_B03gr(Mag_g, Mag_r):
	# Calculate r-band luminosity
	Mag_solar_r = 4.76
	Lsolar_r = 10.0**((Mag_r - Mag_solar_r)/-2.5)
	
	# Stellar mass
	Mstar = 10.0**( -0.499 + (1.519*(Mag_g - Mag_r)) + maths.log10(Lsolar_r))
	
	return Mstar
	
# 4) Bell et al. 2003 relation for g-z
def stellarmass_B03gz(Mag_g, Mag_z):
	# Calculate z-band luminosity
	Mag_solar_z = 4.51
	Lsolar_z = 10.0**((Mag_z - Mag_solar_z)/-2.5)
	
	# Stellar mass
	Mstar = 10.0**( -0.367 + (0.698*(Mag_g - Mag_z)) + maths.log10(Lsolar_z))
	
	return Mstar
	
# 5) Bell et al. 2003 relation for r-i
def stellarmass_B03ri(Mag_r, Mag_i):
	# Calculate i-band luminosity
	Mag_solar_i = 4.58
	Lsolar_i = 10.0**((Mag_i - Mag_solar_i)/-2.5)
	
	# Stellar mass
	Mstar = 10.0**(-0.106 + (1.982*(Mag_r - Mag_i)) + maths.log10(Lsolar_i))
	
	return Mstar	


# 6) Bell et al. 2003 relation for u-g
def stellarmass_B03ug(Mag_u, Mag_g):
	# Calculate g-band luminosity
	Mag_solar_g = 5.45
	Lsolar_g = 10.0**((Mag_g - Mag_solar_g)/-2.5)
	
	# Stellar mass
	Mstar = 10.0**(-0.221 + (0.485*(Mag_u - Mag_g)) + maths.log10(Lsolar_g))
	
	return Mstar
	
	
# 7) Bell et al. 2003 relation for u-r
def stellarmass_B03ur(Mag_u, Mag_r):
	# Calculate r-band luminosity
	Mag_solar_r = 4.76
	Lsolar_r = 10.0**((Mag_r - Mag_solar_r)/-2.5)
	
	# Stellar mass
	Mstar = 10.0**(-0.390 + (0.417*(Mag_u - Mag_r)) + maths.log10(Lsolar_r))
	
	return Mstar	


# 8) Bell et al. 2003 relation for u-i
def stellarmass_B03ui(Mag_u, Mag_i):
	# Calculate i-band luminosity
	Mag_solar_i = 4.58
	Lsolar_i = 10.0**((Mag_i - Mag_solar_i)/-2.5)
	
	# Stellar mass
	Mstar = 10.0**(-0.375 + (0.359*(Mag_u - Mag_i)) + maths.log10(Lsolar_i))
	
	return Mstar


# 8) Bell et al. 2003 relation for u-z
def stellarmass_B03uz(Mag_u, Mag_z):
	# Calculate z-band luminosity
	Mag_solar_z = 4.51
	Lsolar_z = 10.0**((Mag_z - Mag_solar_z)/-2.5)
	
	# Stellar mass
	Mstar = 10.0**(-0.400 + (0.332*(Mag_u - Mag_z)) + maths.log10(Lsolar_z))
	
	return Mstar


# 9) Bell et al. 2003 relation for r-i
def stellarmass_B03ri(Mag_r, Mag_i):
	# Calculate i-band luminosity
	Mag_solar_i = 4.58
	Lsolar_i = 10.0**((Mag_i - Mag_solar_i)/-2.5)
	
	# Stellar mass
	Mstar = 10.0**(-0.106 + (1.982*(Mag_r - Mag_i)) + maths.log10(Lsolar_i))
	
	return Mstar
	

# 9) Bell et al. 2003 relation for r-z
def stellarmass_B03rz(Mag_r, Mag_z):
	# Calculate z-band luminosity
	Mag_solar_z = 4.51
	Lsolar_z = 10.0**((Mag_z - Mag_solar_z)/-2.5)
	
	# Stellar mass
	Mstar = 10.0**(-0.124 + (1.067*(Mag_r - Mag_z)) + maths.log10(Lsolar_z))
	
	return Mstar	
	

# STYLE
# Remove the menu button
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

# Remove vertical whitespace padding
st.write('<style>div.block-container{padding-top:0rem;}</style>', unsafe_allow_html=True)
st.write('<style>div.block-container{padding-bottom:0rem;}</style>', unsafe_allow_html=True)


# Title and Subheading
st.title("Photometry Calculator")
st.subheader("Calculates stellar mass from photometric counts or apparent magnitude")

# Description
st.markdown("""
Calculates the stellar mass of a galaxy from supplied photometric data. The user supplies the net counts for the _u_, 
_g_, _r_, _i_, _z_ bands, as computed in SDSS DR8 data and above (earlier data releases are calibrated differently -
don't use those !). Alternatively the apparent magnitudes can be given directly.""")
st.markdown("""
Providing a distance will enable calculation of absolute magnitudes. Stellar mass can then be calculated, which will 
have improved accuracy if the user also provides sky coordinates (to account for Galactic extinction) and inclination 
angle (to estimate internal extinction). Stellar mass is calculated using various recipes depending on which bands
have input data, though internal extinction is only calculated for the _g_ and _i_ bands.
""") 
st.markdown("""More details of the methodology are given below. A crash course on aperture photometry can be found [here](https://astrorhysy.blogspot.com/2017/11/the-dark-side-of-galaxy-evolution-ii.html).""") 


# Hold the variables in the session state. This is so we can update their GUI entries later.
# NET COUNTS
if 'net_counts_u' not in st.session_state:
	st.session_state['net_counts_u'] = 0.0
if 'net_counts_g' not in st.session_state:
	st.session_state['net_counts_g'] = 0.0
if 'net_counts_r' not in st.session_state:
	st.session_state['net_counts_r'] = 0.0
if 'net_counts_i' not in st.session_state:
	st.session_state['net_counts_i'] = 0.0
if 'net_counts_z' not in st.session_state:
	st.session_state['net_counts_z'] = 0.0	

# APPARENT MAGNTIDUES	
if 'app_mag_u' not in st.session_state:
	st.session_state['app_mag_u'] = 0.0
if 'app_mag_g' not in st.session_state:
	st.session_state['app_mag_g'] = 0.0
if 'app_mag_r' not in st.session_state:
	st.session_state['app_mag_r'] = 0.0	
if 'app_mag_i' not in st.session_state:
	st.session_state['app_mag_i'] = 0.0
if 'app_mag_z' not in st.session_state:
	st.session_state['app_mag_z'] = 0.0	
	
# RAW ABSOLUTE MAGNITUDES	
if 'abs_mag_u' not in st.session_state:
	st.session_state['abs_mag_u'] = 0.0
if 'abs_mag_g' not in st.session_state:
	st.session_state['abs_mag_g'] = 0.0
if 'abs_mag_r' not in st.session_state:
	st.session_state['abs_mag_r'] = 0.0
if 'abs_mag_i' not in st.session_state:
	st.session_state['abs_mag_i'] = 0.0
if 'abs_mag_z' not in st.session_state:
	st.session_state['abs_mag_z'] = 0.0
	
# CORRECTED ABSOLUTE MAGNITUDES
if 'corr_abs_mag_u' not in st.session_state:
	st.session_state['corr_abs_mag_u'] = 0.0
if 'corr_abs_mag_g' not in st.session_state:
	st.session_state['corr_abs_mag_g'] = 0.0
if 'corr_abs_mag_r' not in st.session_state:
	st.session_state['corr_abs_mag_r'] = 0.0
if 'corr_abs_mag_i' not in st.session_state:
	st.session_state['corr_abs_mag_i'] = 0.0
if 'corr_abs_mag_z' not in st.session_state:
	st.session_state['corr_abs_mag_z'] = 0.0
	

# Net Counts Input
st.markdown("##### Net Counts")
col1, col2, col3, col4, col5 = st.columns(5)
st.session_state['net_counts_u'] = col1.number_input("u", format="%f", min_value=0.0)
st.session_state['net_counts_g'] = col2.number_input("g", format="%f", min_value=0.0)
st.session_state['net_counts_r'] = col3.number_input("r", format="%f", min_value=0.0)
st.session_state['net_counts_i'] = col4.number_input("i", format="%f", min_value=0.0)
st.session_state['net_counts_z'] = col5.number_input("z", format="%f", min_value=0.0)

# Apparent Magnitudes Input. If each net count is zero, the apparent magnitude
st.markdown("##### Apparent Magnitudes")
col6, col7, col8, col9, col10 = st.columns(5)

st.session_state['app_mag_u'] = col6.number_input("u ", format="%f", value=countstomag(st.session_state['net_counts_u']))
st.session_state['app_mag_g'] = col7.number_input("g ", format="%f", value=countstomag(st.session_state['net_counts_g']))
st.session_state['app_mag_r'] = col8.number_input("r ", format="%f", value=countstomag(st.session_state['net_counts_r']))
st.session_state['app_mag_i'] = col9.number_input("i ", format="%f", value=countstomag(st.session_state['net_counts_i']))
st.session_state['app_mag_z'] = col10.number_input("z ", format="%f", value=countstomag(st.session_state['net_counts_z']))
	
# Sky Coordinates, Distance and Inclination Angle Input
st.markdown("##### Galaxy Parameters")
st.write('These parameters are optional (except for distance) but will increase the accuracy of the stellar mass calculation.')
col18, col19, col20, col21 = st.columns(4)
sky_coord_ra = col18.text_input("RA [J2000]", help='Right Ascension, used for correcting for Galactic extinction. Enter in the format HH:MM:SS.SS or DD.DDDDDD, i.e. sexigesimal or decimal degrees.')
sky_coord_dec = col19.text_input("Dec [J2000]", help='Reclination, used for correcting for Galactic extinction. Enter in the format DD:MM:SS.SS or DD.DDDDDD, i.e. sexigesimal or decimal degrees.')
distance = col20.number_input("Distance (Mpc)", format="%f", min_value=0.0)
inclination_angle = col21.number_input("Inclination Angle", min_value=0.0, format="%f", help='Inclination angle in degrees, used for internal extinction calculation. Enter zero degrees to disable. By convention, 0 = face-on, 90 = edge-on. NOTE : This should assume a thin circular disc, i.e. such that cos(i) = b/a.')

# Galactic Extinction Model Selection
st.markdown("##### Galactic Extinction Model")
st.write('If the sky coordinates have been provided, the data can be corrected for Galactic extinction. Absolute magnitudes both with and without corrections are given below, but note that the stellar mass calculation ALWAYS uses the corrected values.')
col16, col17 = st.columns([1, 1])
col16.markdown("<div style='padding-top: 30px;'>Choose which Galactic reddening model to use", unsafe_allow_html=True)
galactic_ext_model = col17.selectbox("Model", ["Schlafly & Finkbeiner 2011", "Schlegel, Finkbeiner & Davis 1998"])

# Absolute Magnitudes Input (raw, uncorrected for anything except distance)
st.markdown("##### Raw Absolute Magnitudes")
col11, col12, col13, col14, col15 = st.columns(5)
st.session_state['abs_mag_u'] = col11.number_input("u  ", format="%f", value=absmag(st.session_state['app_mag_u'], distance))
st.session_state['abs_mag_g'] = col12.number_input("g  ", format="%f", value=absmag(st.session_state['app_mag_g'], distance))
st.session_state['abs_mag_r'] = col13.number_input("r  ", format="%f", value=absmag(st.session_state['app_mag_r'], distance))
st.session_state['abs_mag_i'] = col14.number_input("i  ", format="%f", value=absmag(st.session_state['app_mag_i'], distance))
st.session_state['abs_mag_z'] = col15.number_input("z  ", format="%f", value=absmag(st.session_state['app_mag_z'], distance))


# Corrections for Galactic extinction
# First evaluate the input coordinates and convert them if possible. Set some placeholder
# parameters to hold the values we will use for doing the queries. Set these to "Fail" if
# the coordinates cannot be resolved, otherwise use the numerical values (always in decimal
# degrees)
queryra  = None
querydec = None

# Also set values for correcting the extinction, from both Schlafly & Finkbeiner 2011 and
# Schlegel, Finkbeiner & Davis 1998
exu_SF, exu_SFD = 0.0, 0.0
exg_SF, exg_SFD = 0.0, 0.0
exr_SF, exr_SFD = 0.0, 0.0
exi_SF, exi_SFD = 0.0, 0.0
exz_SF, exz_SFD = 0.0, 0.0

# Evaluate the coordinates
if sky_coord_ra != '' and sky_coord_dec != '':
	# If the user enters colons in the RA box, assume they're inputing HH:MM:SS.SS
	if ':' in sky_coord_ra:
		try:
			queryra = Angle(sky_coord_ra+' hours').value*15.0
		except:
			queryra = 'Fail'
		

	# If they don't, assumme they've entered decimal degrees
	else:
		try:
			queryra = Angle(sky_coord_ra+' degrees')
		except:
			queryra = 'Fail'


	# If the user enters colons in the Dec box, assume they're inputing DD:MM:SS.SS
	if ':' in sky_coord_dec:
		try:
			querydec = Angle(sky_coord_dec+' degrees')
		except:
			querydec = 'Fail'
		

	# If they don't, assumme they've entered decimal degrees
	else:
		try:
			querydec = Angle(sky_coord_dec+' degrees')
		except:
			querydec = 'Fail'

# If the coordinates have been successfully resolved, we can do the query			
if queryra != None and queryra != 'Fail' and querydec != None and querydec != 'Fail':
	# Create a SkyCoord object
	coords = SkyCoord(queryra, querydec, frame='icrs', unit=(u.deg, u.deg))
	
	# Query the IRSA dust service
	table = IrsaDust.get_extinction_table(coords)

	# Get rows corresponding to SDSS bands
	sdss_u_band_row = table[table['Filter_name'] == 'SDSS u']
	sdss_g_band_row = table[table['Filter_name'] == 'SDSS g']
	sdss_r_band_row = table[table['Filter_name'] == 'SDSS r']
	sdss_i_band_row = table[table['Filter_name'] == 'SDSS i']
	sdss_z_band_row = table[table['Filter_name'] == 'SDSS z']

	# Retrieve the extinction values from the A_SandFmag (Schlafly & Finkbeiner 2011) column
	exu_SF = sdss_u_band_row['A_SandF'][0]
	exg_SF = sdss_g_band_row['A_SandF'][0]
	exr_SF = sdss_r_band_row['A_SandF'][0]
	exi_SF = sdss_i_band_row['A_SandF'][0]
	exz_SF = sdss_z_band_row['A_SandF'][0]

	# Also the A_SFD (Schlegel, Finkbeiner & Davis 1998) values
	exu_SFD = sdss_u_band_row['A_SFD'][0]
	exg_SFD = sdss_g_band_row['A_SFD'][0]
	exr_SFD = sdss_r_band_row['A_SFD'][0]
	exi_SFD = sdss_i_band_row['A_SFD'][0]
	exz_SFD = sdss_z_band_row['A_SFD'][0]


	# Now we apply the corrections, depending on which model the user selected. Apply the
	# corrections to the apparent magnitudes, then convert to absolute
	if galactic_ext_model == 'Schlafly & Finkbeiner 2011':
		u_GalCorrected = st.session_state['app_mag_u'] - exu_SF
		g_GalCorrected = st.session_state['app_mag_g'] - exg_SF
		r_GalCorrected = st.session_state['app_mag_r'] - exr_SF
		i_GalCorrected = st.session_state['app_mag_i'] - exi_SF
		z_GalCorrected = st.session_state['app_mag_z'] - exz_SF
	
	if galactic_ext_model =='Schlegel, Finkbeiner & Davis 1998':
		u_GalCorrected = st.session_state['app_mag_u'] - exu_SFD
		g_GalCorrected = st.session_state['app_mag_g'] - exg_SFD
		r_GalCorrected = st.session_state['app_mag_r'] - exr_SFD
		i_GalCorrected = st.session_state['app_mag_i'] - exi_SFD
		z_GalCorrected = st.session_state['app_mag_z'] - exz_SFD
	
	# Now convert to absolute magnitudes
	abs_u_GalCorrected  = absmag(u_GalCorrected, distance)
	abs_g_GalCorrected  = absmag(g_GalCorrected, distance)
	abs_r_GalCorrected  = absmag(r_GalCorrected, distance)
	abs_i_GalCorrected  = absmag(i_GalCorrected, distance)
	abs_z_GalCorrected  = absmag(z_GalCorrected, distance)	


	# Correct for internal extinction - ONLY APPLIED FOR G AND I BANDS ! u,r,z all use only the Galactic
	# extinction correction
	u_mag_int_correct = abs_u_GalCorrected
	if st.session_state['abs_mag_g'] != 0.0 and inclination_angle >= 0.0:
		g_mag_int_correct = mag_int_correct(abs_g_GalCorrected, 'g', inclination_angle)
	else:
		g_mag_int_correct = abs_g_GalCorrected
	r_mag_int_correct = abs_r_GalCorrected
	if st.session_state['abs_mag_i'] != 0.0 and inclination_angle >= 0.0:
		i_mag_int_correct = mag_int_correct(abs_i_GalCorrected, 'i', inclination_angle)
	else:
		i_mag_int_correct = abs_i_GalCorrected
	z_mag_int_correct = abs_z_GalCorrected


	# Corrected Absolute Magnitudes
	st.markdown("##### Extinction-Corrected Absolute Magnitudes")
	st.write('These values are corrected for both internal and Galactic extinction.')
	col22, col23, col24, col25, col26 = st.columns(5)
	# Only do the correction if the uncorrected value was not zero
	if st.session_state['abs_mag_u'] != 0.0:
		st.session_state['corr_abs_mag_u'] = col22.number_input("u   ", format="%f", value=u_mag_int_correct)
	if st.session_state['abs_mag_g'] != 0.0:
		st.session_state['corr_abs_mag_g'] = col23.number_input("g   ", format="%f", value=g_mag_int_correct)
	if st.session_state['abs_mag_r'] != 0.0:
		st.session_state['corr_abs_mag_r'] = col24.number_input("r   ", format="%f", value=r_mag_int_correct)
	if st.session_state['abs_mag_i'] != 0.0:
		st.session_state['corr_abs_mag_i'] = col25.number_input("i   ", format="%f", value=i_mag_int_correct)
	if st.session_state['abs_mag_z'] != 0.0:
		st.session_state['corr_abs_mag_z'] = col26.number_input("z   ", format="%f", value=z_mag_int_correct)


# We can now calculate the stellar mass ! Use many different prescriptions. Check which wavebands are available for a viable
# calculation
goodu = st.session_state['corr_abs_mag_u']
goodg = st.session_state['corr_abs_mag_g']
goodr = st.session_state['corr_abs_mag_r']
goodi = st.session_state['corr_abs_mag_i']
goodz = st.session_state['corr_abs_mag_z']

# Convert to booleans
goodu = True if goodu < 0.0 else False
goodg = True if goodg < 0.0 else False
goodr = True if goodr < 0.0 else False
goodi = True if goodi < 0.0 else False
goodz = True if goodz < 0.0 else False


# Work out which stellar masses we can compute : optical colours, UV/optical, UV/NIR, optical/NIR
opticalstellarmass = False
uvoptclstellarmass = False
uvnifrdstellarmass = False
opnifrdstellarmass = False

if (goodg == True and goodi == True) or (goodg == True and goodr == True) or (goodr == True and goodi == True):
	opticalstellarmass = True
if (goodu == True and goodg == True) or (goodu == True and goodr == True) or (goodu == True and goodi == True):
	uvoptclstellarmass = True
if (goodu == True and goodz == True):
	uvnifrdstellarmass = True
if (goodr == True and goodz == True):
	opnifrdstellarmass = True

# If we can compute any stellar masses at all, print the title	
if True in [opticalstellarmass, uvoptclstellarmass, uvnifrdstellarmass, opnifrdstellarmass]:
	st.write('### Stellar masses from available colours')


# OPTICAL COLOURS
if opticalstellarmass == True:
	st.write('#### Optical stellar masses :')
	
	# 1) (g-i) from Taylor+11 and Bell+03
	if st.session_state['corr_abs_mag_g'] != 0.0 and st.session_state['corr_abs_mag_i'] != 0.0:
		galaxy_stellar_mass_1 = stellarmass_T11(st.session_state['corr_abs_mag_g'], st.session_state['corr_abs_mag_i'])
		galaxy_stellar_mass_2 = stellarmass_B03gi(st.session_state['corr_abs_mag_g'], st.session_state['corr_abs_mag_i'])
	
		st.write('##### Stellar mass (g-i) Taylor+2011 = ', nicenumber(galaxy_stellar_mass_1),'&thinsp;M<sub style="font-size:80%">&#9737;</sub>', unsafe_allow_html=True)
		st.write('##### Stellar mass (g-i) Bell+2003   = ', nicenumber(galaxy_stellar_mass_2),'&thinsp;M<sub style="font-size:80%">&#9737;</sub>', unsafe_allow_html=True)
		st.write('(g-i) =',nicenumber(st.session_state['corr_abs_mag_g'] - st.session_state['corr_abs_mag_i']))

	# 2) (g-r) from Bell+03	
	if st.session_state['corr_abs_mag_g'] != 0.0 and st.session_state['corr_abs_mag_r'] != 0.0:
		galaxy_stellar_mass = stellarmass_B03gr(st.session_state['corr_abs_mag_g'], st.session_state['corr_abs_mag_r'])
	
		st.write('##### Stellar mass (g-r) Bell+2003   = ', nicenumber(galaxy_stellar_mass),'&thinsp;M<sub style="font-size:80%">&#9737;</sub>', unsafe_allow_html=True)
		st.write('(g-r) =',nicenumber(st.session_state['corr_abs_mag_g'] - st.session_state['corr_abs_mag_r']))
	
	# 3) (r-i) from Bell+03
	if st.session_state['corr_abs_mag_r'] != 0.0 and st.session_state['corr_abs_mag_i'] != 0.0:
		galaxy_stellar_mass = stellarmass_B03ri(st.session_state['corr_abs_mag_r'], st.session_state['corr_abs_mag_i'])
	
		st.write('##### Stellar mass (r-i) Bell+2003   = ', nicenumber(galaxy_stellar_mass),'&thinsp;M<sub style="font-size:80%">&#9737;</sub>', unsafe_allow_html=True)
		st.write('(r-i) =',nicenumber(st.session_state['corr_abs_mag_r'] - st.session_state['corr_abs_mag_i']))

#  UV/OPTICAL COLOURS
if uvoptclstellarmass == True:
	st.write('#### UV/Optical stellar masses :')
	# 1) (u-g) from Bell+03	
	if st.session_state['corr_abs_mag_u'] != 0.0 and st.session_state['corr_abs_mag_g'] != 0.0:
		galaxy_stellar_mass = stellarmass_B03ug(st.session_state['corr_abs_mag_u'], st.session_state['corr_abs_mag_g'])
	
		st.write('##### Stellar mass (u-g) Bell+2003   = ', nicenumber(galaxy_stellar_mass),'&thinsp;M<sub style="font-size:80%">&#9737;</sub>', unsafe_allow_html=True)
		st.write('(u-g) =',nicenumber(st.session_state['corr_abs_mag_u'] - st.session_state['corr_abs_mag_g']))

	# 2) (u-r) from Bell+03	
	if st.session_state['corr_abs_mag_u'] != 0.0 and st.session_state['corr_abs_mag_r'] != 0.0:
		galaxy_stellar_mass = stellarmass_B03ur(st.session_state['corr_abs_mag_u'], st.session_state['corr_abs_mag_r'])
	
		st.write('##### Stellar mass (u-r) Bell+2003   = ', nicenumber(galaxy_stellar_mass),'&thinsp;M<sub style="font-size:80%">&#9737;</sub>', unsafe_allow_html=True)
		st.write('(u-r) =',nicenumber(st.session_state['corr_abs_mag_u'] - st.session_state['corr_abs_mag_r']))

	# 3) (u-i) from Bell+03	
	if st.session_state['corr_abs_mag_u'] != 0.0 and st.session_state['corr_abs_mag_i'] != 0.0:
		galaxy_stellar_mass = stellarmass_B03ui(st.session_state['corr_abs_mag_u'], st.session_state['corr_abs_mag_i'])
	
		st.write('##### Stellar mass (u-i) Bell+2003   = ', nicenumber(galaxy_stellar_mass),'&thinsp;M<sub style="font-size:80%">&#9737;</sub>', unsafe_allow_html=True)
		st.write('(u-i) =',nicenumber(st.session_state['corr_abs_mag_u'] - st.session_state['corr_abs_mag_i']))

# UV/NIR COLOURS
if uvnifrdstellarmass == True:
	st.write('#### UV/NIR stellar masses :')
	# (u-z) from Bell+03
	galaxy_stellar_mass = stellarmass_B03uz(st.session_state['corr_abs_mag_u'], st.session_state['corr_abs_mag_z'])
	
	st.write('##### Stellar mass (u-z) Bell+2003   = ', nicenumber(galaxy_stellar_mass),'&thinsp;M<sub style="font-size:80%">&#9737;</sub>', unsafe_allow_html=True)
	st.write('(u-z) =',nicenumber(st.session_state['corr_abs_mag_u'] - st.session_state['corr_abs_mag_z']))

# OPTICAL/NIR COLOURS
if opnifrdstellarmass == True:
	st.write('#### Optical/NIR stellar masses :')
	# (r-z) from Bell+03
	galaxy_stellar_mass = stellarmass_B03rz(st.session_state['corr_abs_mag_r'], st.session_state['corr_abs_mag_z'])
	
	st.write('##### Stellar mass (r-z) Bell+2003   = ', nicenumber(galaxy_stellar_mass),'&thinsp;M<sub style="font-size:80%">&#9737;</sub>', unsafe_allow_html=True)
	st.write('(r-z) =',nicenumber(st.session_state['corr_abs_mag_r'] - st.session_state['corr_abs_mag_z']))


# Print additional information if any stellar mass calculation was done
if True in [opticalstellarmass, uvoptclstellarmass, uvnifrdstellarmass, opnifrdstellarmass]:
	st.write('### Reference Information')
	st.write('The stellar mass calculations here follow the methods outlined in [Taylor et al. 2022](https://ui.adsabs.harvard.edu/abs/2022AJ....164..233T/abstract) and [Durbala et al. 2020](https://ui.adsabs.harvard.edu/abs/2020AJ....160..271D/abstract). The (g-i) method comes from [Taylor et al. 2011](https://ui.adsabs.harvard.edu/abs/2011MNRAS.418.1587T/abstract) while all the others are taken from [Bell et al. 2003](https://ui.adsabs.harvard.edu/abs/2003ApJS..149..289B/abstract) (table 7). The absolute magnitude of the Sun in the different bands was taken from [here](https://mips.as.arizona.edu/~cnaw/sun_2006.html).')
	st.write('These methods are designed for normal, star-forming galaxies. They may break down for extreme objects.')
	st.write('The Galactic extinction corrections use the models from [Schlegel, Finkbeiner & Davis 1998](https://ui.adsabs.harvard.edu/abs/1998ApJ...500..525S/abstract) and [Schlafly & Finkbeiner 2011](https://ui.adsabs.harvard.edu/abs/2011ApJ...737..103S/abstract), the standard corrections used in [NED](https://ned.ipac.caltech.edu/classic).')
