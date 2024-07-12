# File purely for testing the import of astropy modules. Does nothing else

import numpy
import astropy
from astropy.coordinates import SkyCoord
from astropy.coordinates import AltAz 
from astropy.coordinates import EarthLocation
from astropy.coordinates import Angle
from astropy.time import Time
from astropy import units as ast_u
import datetime
from datetime import date, timedelta
import calendar
import streamlit as st
import math
from math import pi as pi
import imp
from timezonefinder import TimezoneFinder
import pytz

st.write('This app is useless, but if you can see this message, you know it loaded correctly.')
st.write('Numpy :',numpy.__version__)
st.write('Astropy :',astropy.__version__)
