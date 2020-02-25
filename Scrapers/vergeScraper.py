from grabVergeURLs import getHTML as getHTML # Use the getHTML function already written in grabVergeURLS
import time, csv, json, requests, sys
from bs4 import BeautifulSoup as BS


# lambda functions which return true is they find a matching Beatiful Soup tag
GETSCORECARDS = lambda aside : aside.name == "aside" and (aside.has_attr("class") and (aside["class"][0] and "c-scorecard" in aside["class"][0]))  #scorecards are Aside tags
GETSCORE = lambda tag : tag.has_attr("class") and ("c-scorecard__score-number" in tag["class"])
GETGOOD = lambda ul : ul.name == "ul" and ( ul.parent.name == "div" and (ul.parent.find("h3") and "good stuff" in ul.parent.text.lower()))
GETBAD =  lambda ul : ul.name == "ul" and ( ul.parent.name == "div" and (ul.parent.find("h3") and "bad stuff" in ul.parent.text.lower()))

def scrapeVerge(ReviewURLs):
	"""
	Paramaters: (Dictionary <str:str>) ReviewURLs
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
				ReviewData[phone] = scrapeScoreCards(scoreCards,phone)
			except AttributeError as e:
				print(f"Failed to find a scorecard for {phone} in {url}")
				continue
		print(f"Scraped {count}/{len(ReviewURLs)}\nSleeping 10 seconds")
		count += 1
		time.sleep(10)
			
	return ReviewData

def scrapeScoreCards(cards,phone):
	""" 
	Parameters: (BeautifulSoup object) cards, (string) phone
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


	if not phoneData:
		print(f"Something went wrong looking for {phone}")

	return phoneData

def readReviewsJSON(filename):
	"""
	Paramaters: (str) filename
	return: (Dictionary <str:str>) Reviews 
	Opens the JSON file containing reivew URLS associated w/ phone names. uses JSON module to 
	read them into a dictionary mapping strings to phone names
	"""
	reviews = dict()
	with open(filename, "r") as f:
		rawString = f.read()
		reviews = json.loads(rawString)
	return reviews



def main(argv):
	""" If 't' or 'test' is typed as a console argument, the script is run in test mode
	and the dictionary generated is printend to console. """

	revURLs = readReviewsJSON("VergeReviews.json") # Get a dictionary of the review webpagesA
	vergeData = scrapeVerge(revURLs) # scrape and compile data into a dictionary ready for loading into DB
	# This is just to test that the data has been grabbed 
	if "test" in argv or "t" in argv:
		for k,v in vergeData.items():
			print(f"{k} {v} \n")
	else:
		pass # This would be where data would be fed into the DB



# This condtional just checks if this .py file has been loaded as the main module
# If it's the main module, run the main funciton
if __name__ == "__main__":
	main(sys.argv)

