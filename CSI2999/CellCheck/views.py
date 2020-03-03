from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader

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
	template = loader.get_template("CellCheck/index.html")
	return HttpResponse(template.render(context,request)) #render(request, "CellCheck/index.html", context)

def Manufacturer(request):
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

def Review(request):
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
	return render(request, "CellCheck/Review.html", context)
