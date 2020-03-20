from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from CellCheck.models import Phone, Site, Rating, ProList, ConList, CNETDetailedScore
from CellCheck.modelHelpers import findPhoneID, getSiteIDs
from operator import itemgetter
import functools


# Create your views here.

def index(request):	
	# Manufacturer names as strings, associated links to phone images as well. 
	context = {
				"Manufacturer1":str(),
				"Manufacturer2":str(),
				"Manufacturer3":str(),
				"Manufacturer4":str(),
				"phone1URL":str(),
				"phone2URL":str(),
				"phone3URL":str(),
				"phone4URL":str(),
				}	
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
				}
	if manufacturer:
		context["manufacturer"] = manufacturer
		phoneTable = Phone.objects
		# Get an alphabetically sorted list of the phones with manufacturer name in their name
		# Once Sydney has release date scraped, I can edit this to sort on release date instead
		manufacPhones = phoneTable.filter(PhoneName__contains = manufacturer.lower()).order_by("PhoneName")
		# Top 4 phones get image cards, load the context w/ that data
		for i in range(len(manufacPhones)):
			if i > 3: # Only get 1st 4 phones
				break
			context[f"phone{i+1}"] = manufacPhones[i].getName()
			context[f"phone{i+1}URL"] = manufacPhones[i].getImageURL() 
		# phoneList is remaining phones
		if len(manufacPhones) > 4:
			context["phoneList"] = list(map(lambda phone: phone.getName(),manufacPhones[4:]))

		


	return render(request, "CellCheck/Manufacturer.html", context)

def Review(request, phoneName = None):
	# scores: List of ("name",fltScore) pairs
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
				"cnetSubScores":dict()
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
				context[site.lower()+"Pros"] = ProList.objects.filter(Phone = phoneID).get(Site = siteID).Pros.split("\n")
			except Exception as e:
				continue
			# Add the Cons
			try:
					context[site.lower()+"Cons"] = ConList.objects.filter(Phone = phoneID).get(Site = siteID).Cons.split("\n")		
			except Exception as e:
				continue
			try:
				context["imageURL"] = Phone.objects.get(pk = phoneID).getImageURL()
			except Exception as e:
				continue

		# Add average to context
		if context["scores"]:
			context["scores"].append(("Average",sum(list(map(itemgetter(1),context["scores"])))/len(context["scores"])))

		return render(request, "CellCheck/Review.html", context)
	else:
		return redirect(NotFound, phone = phoneName.lower().replace(" ","-"))





def NotFound(request, phone = None):
	# TODO: Run this idea by Kemal, rather than All Brands, it's phones with similar names/names searched phone IN name
	# 		First 3 results can have their images rendered into the 3 picture cards
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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Helpers ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def makeNamesList(phoneSet):
	# Given a django phoneSet returns a list of their names as strings
	names =  list()
	for phone in phoneSet:
		names.append(phone.PhoneName)
