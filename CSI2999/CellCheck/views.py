from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader

# Create your views here.

def index(request):	
	context = {}
	template = loader.get_template("CellCheck/index.html")
	return HttpResponse(template.render(context,request)) #render(request, "CellCheck/index.html", context)

def Manufacturer(request):
	context = {}

	return render(request, "CellCheck/Manufacturer.html", context)

def Review(request):
		context = { "imageURL":str(),"phoneName":str(),"scores":[],	"vergePros":list(str()),	"vergeCons":list(str()),	"cnetPros":list(str()),"wiredPros":list(str()),	"wiredCons":list(str()),	"pcMagPros":list(str()),	"pcMagCons":list(str()),	"cnetSubScores":dict()} # scores: List of ("name",fltScore) tuples, 
		return render(request, "CellCheck/Review.html", context)
