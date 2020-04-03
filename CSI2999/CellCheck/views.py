from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.template import loader
from CellCheck.models import Phone, Site, Rating, ProList, ConList, CNETDetailedScore
from CellCheck.modelHelpers import findPhoneID, getSiteIDs
from operator import itemgetter
import functools
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
		manufacPhones = phoneTable.filter(PhoneName__contains = manufacturer.lower()).order_by("PhoneName")
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

	try:
		context["cnetDesign"] = CNETDetailedScore.objects.filter(phone = phoneID).get(phone = phoneID).getDesign()
	except Exception as e:
		context["cnetDesign"] = "No Score"

	try:
		context["cnetFeatures"] = CNETDetailedScore.objects.filter(phone = phoneID).get(phone = phoneID).getFeatures()
	except Exception as e:
		context["cnetFeatures"] = "No Score"

	try:
		context["cnetPerformance"] = CNETDetailedScore.objects.filter(phone = phoneID).get(phone = phoneID).getPerformance()
	except Exception as e:
		context["cnetPerformance"] = "No Score"

	try:
		context["cnetCamera"] = CNETDetailedScore.objects.filter(phone = phoneID).get(phone = phoneID).getCamera()
	except Exception as e:
		context["cnetCamera"] = "No Score"

	try:
		context["cnetBattery"] = CNETDetailedScore.objects.filter(phone = phoneID).get(phone = phoneID).getBattery()
	except Exception as e:
		context["cnetBattery"] = "No Score"

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

def Search(request):
	"""
	Searching for phones or by manufacturer name is handled via post requests sent to this view.
	"""
	searchString = request.POST["searchString"].lower()
	if	"manufacturer" in request.POST.keys():
		return redirect(Manufacturer, manufacturer = searchString)
	elif "phone" in request.POST.keys():
		return redirect(Review, phoneName = searchString)
	else:
		raise Http404("Search type not found")	


	


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Helpers ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def makeNamesList(phoneSet):
	# Given a django phoneSet returns a list of their names as strings
	names =  list()
	for phone in phoneSet:
		names.append(phone.PhoneName)
