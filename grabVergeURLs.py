#TODO: 
#	- refactor/clean up
#	- use reg ex to try to find scorecard for reviews w/ nonstandard scorecards
from bs4 import BeautifulSoup as BS
from functools import reduce
import requests, csv, time, json

ROOT = "https://www.theverge.com/phone-review/archives"

def getHTML(URL):
	try:
		return requests.get(URL).text 
	except Exception as e:
		print(f"Ooops, Something went wrong requestiong {URL}.\n{e}")

def getPages(rootURL):
	"""
	Input: (String)rootURL
	Return : (list<String>)Documents
	verge's URL to their review archives, returns a list of the
	HTML documents as strings
	"""
	documents = []
	documents.append(getHTML(rootURL)) # prime w/ first HTML document
	pageNum = 1
	while(1):
		# Find nextLink if it exists, increment pageNumber
		print(f"Getting page #{pageNum}")
		nextLink = BS(documents[len(documents)-1],"lxml").find(lambda tag : tag.name == "a" and tag.text.lower() == "next")
		pageNum += 1
		# Break once we hit a page w/o a "next" link
		if not nextLink:
			break
        # Be polite
		print("Sleeping 15 seconds")
		time.sleep(15)	
		# Grab the next page
		documents.append(getHTML(rootURL + f"/{pageNum}"))
	return documents

def getPhoneNames(URL):
	"""
	Input: URL (String)
	Return: phones (string)
	Given a Verge review URL finds all n number of phones reviewed in the article
	and returns a string containing each phone name
	"""
	# Sorry for the gnarly lambda, basically does the tag have "product" in it's hyperlink and an h2 parent
	links = BS(getHTML(URL),"lxml").find_all(lambda tag : 
					tag.parent.name == "h2" and (tag.has_attr("href") and "product" in tag["href"]))
	# List comprehension to get the links from the BS tag objects
	names =  [link.text for link in links]
	# Return a string w/ all the phone seperated by the pipe symbol
	return reduce((lambda phoneA, phoneB : phoneA + " | " + phoneB),names) if len(names) > 1 else names[0]

def build_URL_Dictionary(reviews):
	"""
	Input: reviews (list<BS4 Tag Elements>)
	Return: revDictionary (Dictionary {tuple<String>:string})
	Takes in a list of BS4 link tag elements to verge phone reviews. Extracts names of phones in reviews
	from each links, builds a dictionary w/ string tuples of the phone names as keys, and the links as values.
	"""
	revDictionary = {}
	count = 1
	for reviewLink in reviews:
		try:
			revDictionary[getPhoneNames(reviewLink["href"])] = reviewLink["href"]
		except IndexError as ie:
			print(f"Review {count}/{len(reviews)} has no scorecard")
		except TypeError as te:
			print("Encountered names list w/ 0 elements. May be due to a request failure")
		print(f"Sleeping after adding review {count}/{len(reviews)}")
		count += 1
		time.sleep(10)

	return revDictionary
        

def getReviewLinks(HTML):
	"""
	Input (String): HTML
	Output (BS4 elementSet): review 
	Given the HTML of the page returns a BS4 element set containing BS4 hyperlink elements to reviews
	"""
	vergeStew = BS(HTML, "lxml")   
	return vergeStew.find_all(lambda tag : tag.has_attr("data-analytics-link") and tag["data-analytics-link"] == "review")

def writeJSON(reviewDictionary, prettyPrint=False):
	"""
	Input: ReviewDictionary (Dictionary {tuple<String>:string})
    output: None
    Given a dictionary of review links w/ string of phone names as the keys,
	and URLs to reviews as values, creates a json file w/ the phone name strings 
	paired to the link to their review URL.	
	"""
	with open("VergeReviews.json","w") as f:
		if prettyPrint:
			f.write(json.dumps(reviewDictionary,indent=4, sort_keys=True))
		else:
			f.write(json.dumps(reviewDictionary,separators=(",",":")))

            

def writeCSV(reviewDictionary):
	"""
	Input: ReviewDictionary (Dictionary {tuple<String>:string})
    output: None
    Given a dictionary of review links w/ string of phone names as the keys,
	and URLs to reviews as values, creates a CSV w/ the phone name strings 
	paired to the link to their review URL.	
	"""
	# The easiest way I could figure to make a CSV via a dictionary is a bit clunky
	with open("VergeReviews.csv","w", newline="") as f: 
		fields = ["Phone Name(s)", "URL"] # Field names for the csv
		writer = csv.DictWriter(f, fieldnames=fields) 
		writer.writeheader() 
		# For dictwriter, rows are entire dictionaries. 
		# So I turn each key/value pair into its own dictionary w/ the CSV fields as keys
		for k,v in reviewDictionary.items(): 
			writer.writerow({fields[0] : k, fields[1] : v}) 
               
def main():
	docs = getPages(ROOT)
	reviews = []

	for doc in docs:
		reviews.extend(getReviewLinks(doc))

	print(f"reviews is a {type(reviews)} and it's size is {len(reviews)}")
	revMap = build_URL_Dictionary(reviews)   

	writeJSON(revMap,prettyPrint=True) #Make a json file and make it pretty
	writeCSV(revMap)

	print("Finished")


    

if __name__ == "__main__":
    main()

