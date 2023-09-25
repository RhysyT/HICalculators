# Calculates the HI deficiency parameter for a source, given its observed HI mass and (optionally) morphology. 
# Allows the user to select preset standard values for the a/b morphological parameters, or supply their own for 
# a range of Hubble types.

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


st.write("# Compute HI deficiency")
st.write('Calculates the HI deficiency of a galaxy given its observed HI mass and optical diameter. Calculates the expected HI mass from a variety of preset coeffecients for morphology, or you can set your own. If only the optical diameter is provided, it will just calculate the expected mass and not the deficiency.')
st.write('Expected HI mass is calculated by the equation :')
st.latex(r'''M_{HI} = a + b.log_{10}(d)''')
st.write('Where d is the optical diameter in kpc. HI deficiency is calculated as :')
st.latex(r'''HI_{def} = log_{10}(MHI_{expected}) - log_{10}(MHI_{observed})''')
st.write('Note that the intrinsic scatter on HI deficiency is +/- ~0.3-0.4 so quoting precise values is pointless. Really all you can say is that : <br> If **def < -0.3**, the galaxy is negatively deficient, having more gas than expected <br> If **-0.3 < def < +0.3**, the galaxy is non-deficient, having a typical gas content <br> If **0.3 < def < 0.6** the galaxy is modestly deficient, having lost some gas <br> If **def > 0.6**, the galaxy is strongly deficient.', unsafe_allow_html=True)


left_column, right_column = st.columns(2)

with left_column:
	# HI flux number widget, row 1
	himass = st.number_input("Observed HI mass", format="%.3f", key="mass", help='Enter observed HI mass in the appropriate unit. Since deficiency is a logarithmic parameter, enter a small value for the case of zero HI mass')
	
	# Optical diameter number widget, row 2
	optd25 = st.number_input("Optical diameter", format="%.3f", key="od", help='Optical diameter of the galaxy, usually defined as the Holmberg diameter at which the surface brightness is 26.5 mag per square arcsecond')
		
with right_column:
	# Mass unit widget, row 1 (adjacent to flux widget)
	massunit = st.selectbox('Mass units', ('Linear solar mass', 'Logarithmic solar mass', 'kg'), key="munit")

	# Optical diameter unit widget, row 2 (adjacent to optical diameter widget)
	optdunit = st.selectbox('Optical diameter units', ('m', 'pc', 'kpc', 'Mpc'), index=2, key="odunit")


# Column-independent dropdown for morphology
mtypechoice = st.selectbox('Morphology', ('Early', 'Sa, Sab', 'Sb', 'Sbc', 'Sc', 'Scd', 'Sd', 'Sdm, Sm', 'Im', 'Later (generally >= Scd)', 'General'), index=10, key="htype", help='Choose the morphology of the galaxy. Different groups have derived slightly different coefficients for the different morphologies')



# On the second row we need three columns of unequal width. The first will be the numerical size of the HI, the second the 
# specification of radius or diameter, and the third the unit
# Providing a list of numbers (instead of a single number) sets the size ratio of each column

lcol, mcol, rcol = st.columns([2,1,1])

	
with lcol:
	# Morphology parameter selection box
	mparams = st.selectbox("Use preset or custom parameters", ('Haynes & Giovanelli 1984', 'Solanes et al. 1996', 'Gavazzi et al. 2005', 'Custom'), index=0, key="type", help='Choose whichever set of preset morphology coefficients you like best, or set your own')

# Set the coefficient dictionaries depending on the current choice of parameter catalogue
if mparams == 'Haynes & Giovanelli 1984':
	mvalues = {'Early':[6.88, 0.89*2.0], 'Sa, Sab':[6.88, 0.89*2.0], 'Sb':[7.17, 0.82*2.0], 'Sbc':[7.17, 0.82*2.0], 'Sc':[7.29, 0.83*2.0], 'Scd':[7.27, 0.85*2.0], 'Sd':[6.91, 0.95*2.0], 'Sdm, Sm':[7.0, 0.94*2.0], 'Im':[7.75, 0.66*2.0], 'Later (generally >= Scd)':[7.75, 0.66*2.0], 'General':[7.12, 0.88*2.0]} 
	
if mparams == 'Solanes et al. 1996':
	mvalues = {'Early':[0.0, 0.0], 'Sa, Sab':[7.75, 1.19], 'Sb':[7.82, 1.25], 'Sbc':[7.84, 1.22], 'Sc':[7.16, 1.74], 'Scd':[7.16, 1.74], 'Sd':[7.16, 1.74], 'Sdm, Sm':[7.16, 1.74], 'Im':[7.16, 1.74], 'Later (generally >= Scd)':[7.16, 1.74], 'General':[7.51, 1.46]} 
	
if mparams == 'Gavazzi et al. 2005':
	mvalues = {'Early':[0.0, 0.0], 'Sa, Sab':[7.29, 1.66], 'Sb':[7.27, 1.70], 'Sbc':[6.91, 1.90], 'Sc':[7.00, 1.88], 'Scd':[7.00, 1.88], 'Sd':[7.00, 1.88], 'Sdm, Sm':[7.00, 1.88], 'Im':[7.00, 1.88], 'Later (generally >= Scd)':[7.00, 1.88], 'General':[7.16, 1.64]} 

if mparams == 'Custom':
	mvalues = {'Early':[0.0, 0.0], 'Sa, Sab':[0.0, 0.0], 'Sb':[0.0, 0.0], 'Sbc':[0.0, 0.0], 'Sc':[0.0, 0.0], 'Scd':[0.0, 0.0], 'Sd':[0.0, 0.0], 'Sdm, Sm':[0.0, 0.0], 'Im':[0.0, 0.0], 'Later (generally >= Scd)':[0.0, 0.0], 'General':[0.0, 0.0]} 	


with mcol:
	# A parameter number widger
	aparam = st.number_input("a", format="%.3f", value=mvalues[mtypechoice][0], key="keya", help='Coefficient "a" used in the predicted HI mass equation')	
	
with rcol:
	# B parameter number widger
	bparam = st.number_input("b", format="%.3f", value=mvalues[mtypechoice][1], key="keyb", help='Coefficient "b" used in the predicted HI mass equation')



# First convert the mass into linear solar units :
if massunit == 'Linear solar mass':
	hisolarmasses = himass
	
if massunit == 'Logarithmic solar mass':
	hisolarmasses = 10.0**himass
	
if massunit == 'kg':
	hisolarmasses = himass/solarmass
	
# We'll also need that in logarithmic units for the deficiency calculation :
if hisolarmasses > 0.0:
	loghimass = math.log10(hisolarmasses)
	

# Next convert the optical diameter into kpc
if optdunit == 'm':
	optd = optd25 / (1000.0*pc)
	
if optdunit == 'pc':
	optd = optd25 / 1000.0
	
if optdunit == 'kpc':
	optd = optd25
	
if optdunit == 'Mpc':
	optd = optd25 / 1000000.0
	

# As long as a and b are defined, we can now calculate the expected HI mass and so get the deficiency
# (Parameters are always defined, this is a throwback to an earlier version but no harm in it)
if aparam is not None and bparam is not None and optd is not None:
	# As long as the optical diameter is set, we can predict the HI mass
	if optd > 0.0:
		MHI_exp = aparam + bparam*math.log10(optd)
		st.write("#### Expected HI mass = "+nicenumber(10.0**MHI_exp)+'&thinsp;M<sub style="font-size:60%">&#9737;</sub>, or '+nicenumber(MHI_exp), "in logarithmic units", unsafe_allow_html=True)
	
	# To give the HI deficiency requires the observed HI mass was also set, to the positive finite value
	if hisolarmasses > 0.0 and optd > 0.0:	
		HIdef = MHI_exp - loghimass
		st.write("#### HI deficiency =",nicenumber(HIdef))
		if mparams == 'Custom':
			st.write('Used the custom parameter values a='+str(aparam)+' and b='+str(bparam))
		if mparams != 'Custom':
			st.write('Used the preset parameter values a='+str(aparam)+' and b='+str(bparam))


	
