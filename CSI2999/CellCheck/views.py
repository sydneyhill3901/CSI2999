from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.urls import reverse
from django.template import loader
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from CellCheck.models import Phone, Site, Rating, ProList, ConList, CNETDetailedScore, UserReview, AvgUserScore
from CellCheck.modelHelpers import findPhoneID, getSiteIDs
from operator import itemgetter
import CellCheck.priceApiInterface as priceAPI #Functions for querying priceAPI TODO: move key to env variables
import random

# Create your views here.

def index(request):	
	# Manufacturer names as strings, associated links to phone images as well. 
	context = {
				"Manufacturer1":"Nokia",
				"Manufacturer2":"LG",
				"Manufacturer3":"Apple",
				"Manufacturer4":"Samsung",
				"phone1URL":"",
				"phone2URL":"",
				"phone3URL":"",
				"phone4URL":"",
				}	

	popularManufacturers = ["samsung","lg","apple","huawei","nokia","motorola","sony","htc"]
	phones = Phone.objects
	# grab 4 manufacturers from the popular list
	for i in range(4):
		end = len(popularManufacturers) - 1
		context[f"Manufacturer{i+1}"] = popularManufacturers.pop(random.randint(0,end))
		# TODO: Once Sydney's scraper online, change PhoneName_icontains to Manufacturer_icontains
		phoneList = phones.filter(PhoneName__icontains = context[f"Manufacturer{i+1}"]).order_by("ReleaseDate")
		if phoneList:
			j = 0
			while not context[f"phone{i+1}URL"]	and j < len(phoneList):
				context[f"phone{i+1}URL"] = phoneList[j].getImageURL() 
				j += 1
		else:
			context[f"phone{i+1}URL"] = ""
		
	return render(request, "CellCheck/index.html", context)

def Manufacturer(request, manufacturer = None):
	# Phone# phone names, phone#URL urls to images, phoneList: list of strings containing the remaining phones from the manufacturer
	context = {
				"manufacturer":str(),
				"phone1":str(),
				"phone1URL":str(),
				"phone2":str(),
				"phone2URL":str(),
				"phone3":str(),
				"phone3URL":str(),
				"phone4":str(),
				"phone4URL":str(),
				"phoneList":[],
                                "expandedPhoneList":[],
				}
	if manufacturer:
		context["manufacturer"] = manufacturer
		phoneTable = Phone.objects
		# Get an alphabetically sorted list of the phones with manufacturer name in their name
		# Once Sydney has release date scraped, I can edit this to sort on release date instead
		manufacPhones = phoneTable.filter(PhoneName__contains = manufacturer.lower()).order_by("ReleaseDate")
		# Top 4 phones get image cards, load the context w/ that data
		for i in range(len(manufacPhones)):
			if i > 3: # Only get 1st 4 phones
				break
			context[f"phone{i+1}"] = manufacPhones[i].getName()
			context[f"phone{i+1}URL"] = manufacPhones[i].getImageURL() 
		# phoneList is remaining phones
		if len(manufacPhones) > 4:
			context["phoneList"] = list(map(lambda phone: phone.getName(),manufacPhones[4:9]))
		if len(manufacPhones) > 6:
                   context["expandedPhoneList"] = list(map(lambda phone: phone.getName(),manufacPhones[9:]))

	return render(request, "CellCheck/Manufacturer.html", context)


def Review(request, phoneName = None):
	# scores: List of ("name",fltScore) pairs
	if None == phoneName:
		return redirect(NotFound)

	context = { 
				"imageURL":str(),
				"phoneName":str(),
				"scores":[],
				"vergePros":list(str()),
				"vergeCons":list(str()),
				"cnetPros":list(str()),
				"wiredPros":list(str()),
				"wiredCons":list(str()),
				"pcMagPros":list(str()),
				"pcMagCons":list(str()),
				"cnetSubScores":dict(),
				"cnetDesign":str(),
				"cnetFeatures":str(),
				"cnetPerformance":str(),
				"cnetCamera":str(),
				"cnetBattery":str()
				}
	phoneName = phoneName.replace("-"," ").capitalize()
	context["phoneName"] = phoneName
	phoneID = findPhoneID(phoneName)
	siteIDMap = getSiteIDs()
	if phoneID != -1:
		for site,siteID in siteIDMap.items():
			# Add review scores to context
			try:
				context["scores"].append((site, Rating.objects.filter(Phone = phoneID).get(Site = siteID).Rating))
			except Exception as e:
				# nothing db yet
				continue
			# Add the Pros
			try:
				#TODO: Temporary change, sydney will format these to split on new-lines
				if site.lower() == "pcmag":
					context[site.lower()+"Pros"] = ProList.objects.filter(Phone = phoneID).get(Site = siteID).Pros.split(". ")
				else:
					context[site.lower()+"Pros"] = ProList.objects.filter(Phone = phoneID).get(Site = siteID).Pros.split("\n")
			except Exception as e:
				continue
			# Add the Cons
			try:
				#TODO: Ditto above
				if site.lower() == "pcmag":
					context[site.lower()+"Cons"] = ConList.objects.filter(Phone = phoneID).get(Site = siteID).Cons.split(". ")		
				else:
					context[site.lower()+"Cons"] = ConList.objects.filter(Phone = phoneID).get(Site = siteID).Cons.split("\n")		
			except Exception as e:
				continue
			try:
				context["imageURL"] = Phone.objects.get(pk = phoneID).getImageURL()
			except Exception as e:
				continue
	# Adding CNET Score Breakdown
	try:
		context["cnetDesign"] = CNETDetailedScore.objects.filter(phone = phoneID).get(phone = phoneID).getDesign()
		context["cnetFeatures"] = CNETDetailedScore.objects.filter(phone = phoneID).get(phone = phoneID).getFeatures()
		context["cnetPerformance"] = CNETDetailedScore.objects.filter(phone = phoneID).get(phone = phoneID).getPerformance()
		context["cnetCamera"] = CNETDetailedScore.objects.filter(phone = phoneID).get(phone = phoneID).getCamera()
		context["cnetBattery"] = CNETDetailedScore.objects.filter(phone = phoneID).get(phone = phoneID).getBattery()
	except ObjectDoesNotExist as e:
		pass

	# Adding USer Review Data
	bestBuyDict = getUserReviewDictionary(phoneID,"Best Buy")		
	sprintDict = getUserReviewDictionary(phoneID,"Sprint")
	if bestBuyDict:
		context["BestBuy"] = bestBuyDict
	if sprintDict:
		context["Sprint"] = sprintDict
	# Add average to context, render that sucker
	if context["scores"]:
		context["scores"].append(("Average",sum(list(map(itemgetter(1),context["scores"])))/len(context["scores"])))
		return render(request, "CellCheck/Review.html", context)
	else:
		return redirect(NotFound, phone = phoneName.lower().replace(" ","-"))


def NotFound(request, phone = None):
	context = {
				"phoneName":str(),
				"candidates":list(),
				"topCandidateImages":list(str()), # list w/ image URLs from 1st 3 phones in possible phones
				"topCandidates":list(dict())
				}		
	if phone:
		context["phoneName"] = phone.replace("-"," ")
		words = phone.split("-")
		candidates = list()
		if len(words) > 1: # Phone series name usually second word
			candidates = Phone.objects.filter(PhoneName__contains = words[1])
		else: # If only 1 word entered, just do a select where like word
			candidates = Phone.objects.filter(PhoneName__contains = words[0])
		if candidates: # if we got some candidate phones, put names in context, also get 1st 3 phone images
			if len(candidates) > 3:
				context["candidates"] = list(map(lambda phone : phone.PhoneName,candidates[3:]))
			# TODO: Edit imageURLS in context to be tuples of (phoneName,imageURL). Maybe rename this context to topCandiates or soemthing
			for i in range(len(candidates)):
				if i > 2:
					break
				context["topCandidates"].append({"name":candidates[i].getName(),"imgURL":candidates[i].getImageURL()})
				#context["topCandidateImages"].append(candidates[i].getImageURL()) 
				
	return render(request, "CellCheck/phonenotfound.html", context)

def Search(request):
	"""
		Searching for phones or by manufacturer name is handled via post requests sent to this view.
	"""

	searchString = request.POST["searchString"].lower()
	if	"manufacture" in request.POST.keys():
		if searchString:
			return redirect(Manufacturer, manufacturer = searchString)
		else:
			return redirect(Manufacturer)

	elif "phone" in request.POST.keys():
		if searchString:
			return redirect(Review, phoneName = searchString)
		else:
			return redirect(Review)
	else:
		raise Http404("Search type not found")	

def queryPriceAPI(request,phone=None):	
	"""
		View which returns the true nature of your soul 
	"""
	print("phone name being searched is",phone)
	if phone:
		#phone = phone.replace("%20"," ")
		try:
			queryData = priceAPI.phoneQuery(phone, priceAPI.KEY, priceAPI.JOBS_URL) 
		except Exception as e:
			# Idk why we failed this bad, but the important thing is to return eventually
			queryData = {"amazon":None,"google":None}
	else:
		queryData = {"amazon":None,"google":None}
	# Apply the filters to remove cruft (wrong phones, biddable items, etc)
	for key in queryData.keys():
		if "success" in queryData[key] and (queryData[key]["success"] and queryData[key]["results"]):
			queryData[key]["results"] = priceAPI.filterResultList(phone.lower(),queryData[key]["results"])
			queryData[key]["results"] =	list(map(cleanPriceData(phone),queryData[key]["results"])) if queryData[key]["results"] else None
			if queryData[key]["results"] and len(queryData[key]["results"]) > 3:
				queryData[key]["results"] = queryData[key]["results"][:3]
	return JsonResponse(queryData)	

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Helpers ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getUserReviewDictionary(phoneId,site):
	siteId = None	
	try:
		siteId = Site.objects.get(SiteName=site)
	except MultipleObjectsReturned as e:
		print(f"Oh no! some duplicate items {e}")
		return {}
	except ObjectDoesNotExist as e:
		print(f"Oh no! No item found in database. {e}")
		return {}
	if siteId and phoneId:
		try:
			results = UserReview.objects.filter(Site=siteId).filter(Phone=phoneId).order_by("UsefulCount")
			if len(results) == 0:
				return {}
			userRevDict = results[0].createUserReviewDict()
			userRevDict["avg"] = AvgUserScore.objects.get(Site=siteId, Phone=phoneId).getAvg()
			return userRevDict
		except Exception as e:
			print(e)
			return {}

def makeNamesList(phoneSet):
	# Given a django phoneSet returns a list of their names as strings
	names =  list()
	for phone in phoneSet:
		names.append(phone.PhoneName)

def cleanPriceData(phoneName):
	# higher order function for use in a Map. Returns a functioon designed to 
	# process the product name of a priceAPI search result
	def helper(data):
	# Given a dictionary of priceAPI data, returns a "cleaned" dicitonary
		cleaned = {"url":data["url"]}
		cleaned["name"] = processPhoneName(data["name"],phoneName,",-.")
		# If we couldn't get a clean result via processPhoneName, then get the first 
		# n + 1 words where n is the original phone name.
		if not cleaned["name"]:
			nameLength = len(phoneName.split(" "))
			cleaned["name"] = " ".join(data["name"].split(" ")[0:nameLength]).strip(",")
		if "shipping_costs" in data:
			cleaned["shipping_costs"] = data["shipping_costs"]
		if "price" in data:
			cleaned["price"] = data["price"]
		else:
			cleaned["price"] = data["min_price"]
		return cleaned
	return helper

def processPhoneName(nameString,phoneName,seperators):
	"""
	Breaks the nameString up into "chunks" spliit on the spacers provided in the spacers string
	Attempts to return a string structured as (phoneName) (storage capacity). Note, this function
	uses '|' as its final seperator to split the nameString on, so it will always split the pipe
	character. 
	"""
	phoneSuffixes = ["ultra", "+", "plus", "max"]
	charSuffixes = ["e","s"]
	nameString = nameString.lower()

	# First, check that the phone is in the name string
	if not phoneName in nameString:
		print(f"Expected {phoneName} in : {nameString}")
		return ""
	# First replace all the spacers with a | character
	for c in seperators:
		nameString = nameString.replace(c,"|")
	# Get the chunks, in lower case w/o whitespace
	chunks = list(map(lambda s : s.strip().lower(),nameString.split("|")))
	result = phoneName.capitalize()
	# For now, better to add the suffix for "10e, xs" etc on when the phone returned is one of those models
	for char in charSuffixes:
		if phoneName[-1] != char and (phoneName + c) in nameString:
			result += suffix
	# Ditto for word suffixes
	for suffix in phoneSuffixes:
		if not suffix in phoneName and suffix in nameString:
			result += " " + suffix

	# Now try to see if storage capacity is avaiable 
	try:
		print("nameString",nameString)
		chunks = list(map(lambda s : s.strip().strip("|").lower(),nameString.split(" ")))
		result += " " + list(filter(lambda s : "gb" in s, chunks))[0]
		return result
	except IndexError as e:
		return result

		
