from django.shortcuts import render, get_object_or_404
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
				context["imageURL"] = Phone.objects.get(pk = phoneID).PhoneImageURL
			except Exception as e:
				continue

		# Add average to context
		if context["scores"]:
			context["scores"].append(("Average",sum(list(map(itemgetter(1),context["scores"])))/len(context["scores"])))
	else:
		pass

	return render(request, "CellCheck/Review.html", context)
