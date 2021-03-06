# Returns numbers in a sensible format
def nicenumber(number):
	# Small numbers - return comma-separated thousands rounded to 2 d.p.
	if number < 1E6:
		newnumber = str(f"{number:,.2f}")
	# Large numbers - use scientific notation
	if number >= 1E6:
		newnumber = str("{:.2E}".format(number))
		
	return newnumber
