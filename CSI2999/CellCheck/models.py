from django.db import models
import django.core.exceptions
#TODO: Add query methods for use in views 

"""
Notes:
	- Each model class (ie. child class of models.Model) corresponds to one sql table
 	- In python a class is defined as a child of a parent by putting the parent in the
 	  parentheses after the class name is defined
	- by default model classes generate an id column w/ Not Null and Primary Key settings
""" 

class Phone(models.Model):
	PhoneName = models.CharField(max_length = 40)
	# I am gonna set this to 160 for now, might need to make larger
	CnetURL = models.CharField(max_length = 160) 
	WiredURL = models.CharField(max_length = 160) 
	PCMagURL = models.CharField(max_length = 160) 
	VergeURL = models.CharField(max_length = 160) 
	phoneImageURL = models.CharField(max_length = 160)
	Manufacturer = models.CharField(max_length = 160, default="")
	# A date field so we know when the phone was released
	ReleaseDate = models.CharField(max_length = 40)


	def getName(self):
		return self.PhoneName

	def getID(self):
		return self.id
	
	def getImageURL(self):
		return self.phoneImageURL
	
	def __str__(self):
		return self.PhoneName

class Site(models.Model):
	# Having this as a table means we only have to store foreign keys
	# in rating table entries rather than redundant strings, saving space
	# also more extensible for the "future"
	SiteName = models.CharField(max_length = 40)

	def __str__(self):
		return self.SiteName

	def getId(self):
		return self.pk


class Rating(models.Model):
	# Need to store reviews as floats b/c some sites scores are to 1st decimal point
	Rating = models.DecimalField(max_digits=3, decimal_places=1) 
	# This is how you make a foreign key in django. Note the cascading delete
	Phone = models.ForeignKey(Phone, on_delete=models.CASCADE)
	Site = models.ForeignKey(Site, on_delete=models.CASCADE)

	def __str__(self):
			return f"{self.Site}'s rating for the: {self.Phone}"

class ProList(models.Model):
	Phone = models.ForeignKey(Phone, on_delete=models.CASCADE)
	Site = models.ForeignKey(Site, on_delete=models.CASCADE)
	Pros = models.TextField(max_length = 200)

	def __str__(self):
		return f"{self.Site}'s pros for phone {self.Phone}"

class ConList(models.Model):
	Phone = models.ForeignKey(Phone, on_delete=models.CASCADE)
	Site = models.ForeignKey(Site, on_delete=models.CASCADE)
	Cons = models.TextField(max_length = 200)

	def __str__(self):
		return f"{self.Site}'s cons for phone {self.Phone}"

class CNETDetailedScore(models.Model):
	phone = models.ForeignKey(Phone, on_delete=models.CASCADE)
	Design = models.PositiveSmallIntegerField()
	Features = models.PositiveSmallIntegerField()
	Performance = models.PositiveSmallIntegerField()
	Camera = models.PositiveSmallIntegerField()
	Battery = models.PositiveSmallIntegerField()

	def getDesign(self):
		return self.Design

	def getFeatures(self):
		return self.Features

	def getPerformance(self):
		return self.Performance

	def getCamera(self):
		return self.Camera

	def getBattery(self):
		return self.Battery

	def __str__(self):
		return f"CNET Detailed Scores\nDesign: {self.Design}\nFeatures: {self.Features}\nPerformance: {self.Performance}\nCamera: {self.Camera}\nBattery: {self.Battery}"

class UserReview(models.Model):
	# Store user scores for a given 
	Site = models.ForeignKey(Site, on_delete=models.CASCADE)
	Phone = models.ForeignKey(Phone, on_delete=models.CASCADE)
	UsefulCount = models.IntegerField()
	Rating = models.DecimalField(max_digits=3, decimal_places=1)
	IsPositive = models.BooleanField(default = True) # Right now this defaults to true. If we decide to store negative reviews, can be overriden
	Content = models.TextField(max_length=400, default="")
	Title = models.CharField(max_length=100, default="")
	def __str__(self):
		return f"{self.Site}'s {'positive' if self.IsPositive else 'negative'} user review for {self.Phone}"
	
	def createUserReviewDict(self):
		return {
				"revTitle": self.Title,
				"content": '"' + self.Content + '"',
				"rating": self.Rating,
				"usefulCount": self.UsefulCount,
				}


	
class AvgUserScore(models.Model):
	# Average user scores for a given phone on an ecommerce site
	Site = models.ForeignKey(Site, on_delete=models.CASCADE)
	Phone = models.ForeignKey(Phone, on_delete=models.CASCADE)
	AvgScore = models.DecimalField(max_digits=3, decimal_places=1)
	
	def getAvg(self):
		return self.AvgScore

	def __str__(self):
		return f"{self.Site}'s average score for {self.Phone} : {self.AvgScore}"
