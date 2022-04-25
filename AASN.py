import math

# Calculate the total integrated S/N according to ALFALFA (Saintonge 2007)
def aasn(totflux, w50, vres, rms):
	# rms input in Jy, here convert to mJy
	thisrms = rms * 1000.0
	
	if w50 < 400.0:
		wsmo = w50 / (2.0*vres)
	if w50 >= 400.0:
		wsmo = 400.0 / (2.0*vres)
			
	intsn = (1000.0*totflux / w50) * (math.sqrt(wsmo) / thisrms)
	
	return intsn
