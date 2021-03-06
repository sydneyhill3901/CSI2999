from CellCheck.models import *
import re

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Phone table ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def findPhoneID(phoneName, replacements=None):
	"""
	Parameters: (str) phoneName, (list[pairs(str,str)]) replacements
	Return: (int) ID
	Attempts to query the Phone table and return the phone ID. First searches for a phone with
	the string phoneName in its PhoneName column. If this fails, it fuzzes the search term by 
	replacing common characters like the roman numeral x with "10", etc. There are default replacements,
	but these can be overriden by providing a list of (string,string) pairs. The first element 
	in the pair is replaced with the saecond. If these fuzzed searches fail, it returns -1 

	!!! Always check the return for the sentinal invalid key value -1 !!! 
	"""
	# TODO: Refactor this to use sql like via PhoneName__contains first, then if multiple found, return the one appropriate
	# Default pairs of string replacements for fuzzy searching. These can be overriden by providing a replacements parameter
	if replacements == None:
		replacements = [("x","10"),("10","x"),
						("+","plus"),("plus","+"),
						("one","1"),("1","one"),
						("i","1"),("1","i"),
						("ii","2"),("2","ii"),
						("iii","3"),("3","iii"),
						("iv","4"),("4","iv"),
						("v","5"),("5","v"),
						("vi","6"),("6","vi"),
						("vii","7"),("7","vii"),
						]
	# Lambda used to search phone table based on character replacements of 
	fuzz = lambda name, replacePair : Phone.objects.filter(PhoneName__iexact = name.replace(replacePair[0],replacePair[1]))

	resultSet = Phone.objects.filter(PhoneName__iexact = phoneName)
	if len(resultSet) == 1:
		return resultSet[0].id
	else:
		# Time for fuzzy searches
		for pair in replacements:
			resultSet = fuzz(phoneName, pair)
			if len(resultSet) == 1:
				return resultSet[0].id
		# search failed to find a unique phone w/ that name
		return -1 

def intToNumeral(num):
	pass

def numeralToArabic(romanNumeral):
	# Takes in a roman numeral as a string, parses it, returns a the integer corresponding to the
	# numeral
	# Return None on failure
	romanNumeral = romanNumeral.lower() # Just in case it's not already
	charToInt = {"i":1,"v":5,"x":10,"l":50,"c":100,"d":500,"m":1000}
	if len(romanNumeral) == 1 and romanNumeral in charToInt.keys():
		return charToInt[romanNumeral]
	elif romanNumeral:
		Sum = 0
		charList = list(romanNumeral)
		i = 0
		length = len(charList)
		while i < length:
			try:
				if i < length -1 and charToInt[charList[i]] < charToInt[charList[i+1]]:	
					Sum += (charToInt[charList[i+1]] - charToInt[charList[i]])
					i += 2 
				else:
					Sum += charToInt[charList[i]]
					i += 1	
			except KeyError: # invalid chars mean invalid numeral
				return None
		return Sum
	else:
		return None


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Site Table ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`
def getSiteIDs():
	"""
	Paramaters: None
	Return: (dict{str:int}) dictionary mapping site names to integer key values
	"""
	sites = Site.objects.all()
	return {site.SiteName : site.id for site in sites}


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Rating Table ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ CNETDetailed Table ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ConList Table ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ProList Table ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`


