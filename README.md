# HI Calculators
Simple online HI calculations. These are mainly for my own use and for learning Streamlit. They are extremely simple, assuming flat, Euclidian geometry and do not account for any relativistic effects. These are reasonable assumptions when considering environmental-based galaxy evolution, where galaxies are not likely to move more than a few Mpc at most and travel at no (or not much) more than 1% of the speed of light. Maybe I will include some of these effects at some point, but I doubt it.

The calculators are :<br><br>
ObservedHIMass.py<br>
Available through Streamlit at https://share.streamlit.io/rhysyt/hicalculators/main/ObservedHIMass.py<br>
Given the total HI flux and distance to a source, this calculates the HI mass. Flux units can be mJy or Jy, distance units can be pc, kpc, or Mpc. This uses the standard formula MHI = 2.36E5*d^2*SHI. Optionally, it also calculates the integrated S/N of a source according to the criteria established for ALFALFA by Saintonge 2007 (https://ui.adsabs.harvard.edu/abs/2007AJ....133.2087S/abstract). This requires the line width, the velocity resolution, and rms noise level.

TopHatHIMass.py<br>
Available through Streamlit at https://share.streamlit.io/rhysyt/hicalculators/main/TophatHIMass.py<br>
Similar to ObservedHIMass, but calculates the mass of a source with a top-hat profile of the given line width, rms noise level, S/N level, and distance. Useful in estimating the mass sensitivity of a survey. As with ObservedHIMass it can also calculate the integrated S/N criteria. By experience, the faintest source can be readily detected is a 4 sigma, 50 km/s width object at 10 km/s resolution. This has an integrated S/N of 6.3, very close to the established value of 6.5 above which surveys have been found to be both complete and reliable. Note however that this is only an approximation. Both line width and peak S/N matter for detability, influencing the total mass, and line profile shape is not usually a top-hat.

ColumnDensityCal.py<br>
Available through Streamlit at https://share.streamlit.io/rhysyt/hicalculators/main/ColumnDensityCal.py<br>
Given the mass and size of an object (in different units), this calculates the average column density of the material. Returns the result in both atoms cm^-2 and Msolar pc^-2. Although labelled as HI, this will work equally well for anything else. Note HI tends to saturate at ~10 Msolar pc^2 and is rarely found at levels at or below 10^17 cm^-2 (the tendency of to routinely use different units for the same measurement in different contexts is one very good reason such a calculator is needed !).

TravelTime.py<br>
Available through Streamlit at https://share.streamlit.io/rhysyt/hicalculators/main/TravelTime.py
Another useful way to conver between different units. Does simple, linear calculations of either : 1) time taken to travel a given distance at a given speed; 2) the distance travelled in a given time at a given speed; 3) the average speed to travel a given distance in a given time. Very simple, but since we generally use km/s for speed but kpc for distances, the unit conversion is handy to have.
