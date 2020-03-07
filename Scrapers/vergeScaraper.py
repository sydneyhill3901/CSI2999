from grabVergeURLs import getHTML as getHTML # Use the getHTML function already written in grabVergeURLS
import time, csv, json, requests, sys, datetime, sqlite3
from bs4 import BeautifulSoup as BS


# lambda functions which return true is they find a matching Beatiful Soup tag
GETSCORECARDS = lambda aside : aside.name == "aside" and (aside.has_attr("class") and (aside["class"][0] and "c-scorecard" in aside["class"][0]))  #scorecards are Aside tags
GETSCORE = lambda tag : tag.has_attr("class") and ("c-scorecard__score-number" in tag["class"])
GETGOOD = lambda ul : ul.name == "ul" and ( ul.parent.name == "div" and (ul.parent.find("h3") and "good stuff" in ul.parent.text.lower()))
GETBAD =  lambda ul : ul.name == "ul" and ( ul.parent.name == "div" and (ul.parent.find("h3") and "bad stuff" in ul.parent.text.lower()))

def scrapeVerge(ReviewURLs):
	"""
	PArameters: (Dictionary <str:str>) ReviewURLs
	Return: (Dictionary <str>: <Dictionary <str:str>) ReviewData)
	Takes in a dictionary associationg phones to review URLs. For each review, scrapes the pertinent
	information into a dictionary containing the data to save to the db. The returned ReviewData 
	dicitonary has phone names as the keys, and sub-dictionaries of field name strings associated w/
	review data strings. """
	ReviewData = dict()
	count = 1

	for phoneNames,url in ReviewURLs.items():
		try:
			reviewSoup = BS(getHTML(url),"lxml") # create a BS object from review's URL
		except Exception as e: 
			# Print out what phones we failed to scrape and continue scraping
			print(f"Oops, get request failed on review page for {phoneNames} \nusing URL {url}\n {e}")
			continue
		phones = phoneNames.strip().split("|") # get a list of each phone in review
		# get the info divs from the score cards	
		scoreCards = reviewSoup.find_all(GETSCORECARDS)
		# Scrape the score card 
		for phone in phones:
			phone = phone.strip()
			try:
				ReviewData[phone] = scrapeScoreCards(scoreCards,phone,url)
			except AttributeError as e:
				print(f"Failed to find a scorecard for {phone} in {url}")
				continue
		print(f"Scraped {count}/{len(ReviewURLs)}\nSleeping 10 seconds")
		count += 1
		time.sleep(10)
			
	return ReviewData

def scrapeScoreCards(cards,phone,url):
	""" 
	Parameters: (BeautifulSoup object) cards, (string) phone, (string) url
	returns: (dictionary<string:string>) phoneData
	Given a BS4 result set of aside tags and a phone name generates a dicitonary
	mapping data field names to data scrapped from the verge review. 
	"""
	phoneData = dict()
	
	# Loop over the cards, find the card for phone of interest and scrape data into a dictionary
	for card in cards:
		if phone in card.text:
			phoneData["score"] = float(card.find(GETSCORE).get_text().strip().lower().replace(" out of 10",""))
			phoneData["good stuff"] = card.find(GETGOOD).text.strip() 
			phoneData["bad stuff"] = card.find(GETBAD).text.strip()
			phoneData["vergeURL"] = url


	if not phoneData:
		print(f"Something went wrong looking for {phone}")

	return phoneData

def readReviewsJSON(filename):
	"""
	Parameters: (str) filename
	return: (Dictionary <str:str>) Reviews 
	Opens the JSON file containing reivew URLS associated w/ phone names. uses JSON module to 
	read them into a dictionary mapping strings to phone names
	"""
	reviews = dict()
	with open(filename, "r") as f:
		rawString = f.read()
		reviews = json.loads(rawString)
	return reviews

def getConnection(path,attempt=1):
	# Given a path to an sqlite database attempts to get a connection to the database
	# Tries recursively 5 times before it fails. Sleeps for 5 seconds b/w each try.
	# If attempt fails, exits the program
	try:
		return sqlite3.connect(path)
	except Exception as e:
		print(f"Failed to connect to sqlite database at {path}",end=" ")
		if attempt < 6:
			print("Trying again")
			time.sleep(5)
			return getConnection(path,attempt + 1)
		else:
			print(f"Too many failed attempts to connect to {path}, exiting.\n{e}")
			exit()


def writeData(dataDictionary,filename="../CSI2999/db.sqlite3"):
	"""
	Parameters: (dictionary <str:dictionary>) dataDicitonary, (string) filename
	Attempts to write the data for each phone in the review data scraped into
	the database specified by filename. filename is overridable, but defaults to a 
	sqlite3 file in the sibling CSI2999 folder
	"""
	connection = getConnection(filename)
	cursor = connection.cursor()
    # Get the siteID for later writes
	cursor.execute("SELECT id FROM CellCheck_Site WHERE SiteName='Verge'")
	siteID = cursor.fetchone()[0]
	if type(siteID) != int:
		print("Something went VERY wrong with the sites table :(")
		exit()
	
	failures = 0 # Count how many times my script fell short :'(
	for name,data in dataDictionary.items():
		try:
			writePhoneData(name.strip().lower(),data,siteID,connection)
			connection.commit() # Commit after each insertion
		except Exception as e:
			print(f"{e}")
			failures += 1
			continue
	
	print(f"Finished writing to db with {failures} failed writes")

def writePhoneData(phoneName,phoneData,siteID,connection):
	"""
	Parameters: (string) phoneName (dictionary <str:data>) phoneData, (int)siteID, (sqlite3 connection)
	return: None
	Given a Cursor and a dictionary containing scraped phone data writes the data scraped for one Verge
	phone review into the data to the sqlite database. 
	"""
	c = connection.cursor()	
	# check if phone in DB
	c.execute("SELECT id FROM CellCheck_Phone WHERE PhoneName=?",(phoneName,))
	# Phone is in database already, just update verge's columns
	phoneID = c.fetchone()

	if phoneID:
		c.execute("UPDATE CellCheck_Phone SET VergeURL = ? WHERE PhoneName=?",(phoneData["vergeURL"],phoneName,))
	# Phone isn't in database yet  	
	else:
		c.execute("INSERT INTO CellCheck_Phone (PhoneName,CnetURL,WiredURL,PCMagURL,VergeURL,ReleaseDate) VALUES (?,?,?,?,?,?)",(phoneName,"","","",phoneData["vergeURL"],""))
	
	# Next 4 linkes commit the insertion and get the phone's id so it can be used as a foreign key in other tables
	connection.commit()
	c.execute("SELECT id FROM CellCheck_Phone WHERE PhoneName=?",(phoneName,))
	phoneID = c.fetchone()[0]
	c.execute("INSERT INTO CellCheck_Rating (Rating,Phone_id,Site_id) VALUES (?,?,?) ",(phoneData["score"],phoneID,siteID))	
	c.execute("INSERT INTO CellCheck_ProList (Phone_id, Site_id, Pros) VALUES (?,?,?)",(phoneID,siteID,phoneData["good stuff"],))
	c.execute("INSERT INTO CellCheck_ConList (Phone_id, Site_id, Cons) VALUES (?,?,?)",(phoneID,siteID,phoneData["bad stuff"],))

def main(argv):
	""" If 't' or 'test' is typed as a console argument, the script is run in test mode
	and the dictionary generated is printend to console. """

	revURLs = readReviewsJSON("VergeReviews.json") # Get a dictionary of the review webpagesA
	# This is just to test that the data has been grabbed 
	if "test" in argv or "t" in argv:
		vergeData = scrapeVerge(revURLs) # scrape and compile data into a dictionary ready for loading into DB
		for k,v in vergeData.items():
			print(f"{k} {v} \n")
	# run with command line argument 'dbTest' to test writing to database with only 5 phones
	elif "dbTest" in argv:
		keys = list(revURLs.keys())[10:15]	
		sampleURLs = {}
		for key in keys:
			sampleURLs[key] = revURLs[key]
		vergeData = scrapeVerge(sampleURLs)
		writeData(vergeData)
	else:
		writeData(vergeData)
	

# This condtional just checks if this .py file has been loaded as the main module
# If it's the main module, run the main funciton
if __name__ == "__main__":
	main(sys.argv)

