from django.db import models

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
	# A date field so we know when the phone was added to the database
	DataAdded = models.DateField()

class Site(models.Model):
	# Having this as a table means we only have to store foreign keys
	# in rating table entries rather than redundant strings, saving space
	# also more extensible for the "future"
	Name = models.CharField(max_length = 40)

class Rating(models.Model):
	# Need to store reviews as floats b/c some sites scores are to 1st decimal point
	Rating = models.DecimalField(max_digits=2, decimal_places=1) 
	# This is how you make a foreign key in django. Note the cascading delete
	PhoneID = models.ForeignKey(Phone, on_delete=models.CASCADE)
	SiteID = models.ForeignKey(Site, on_delete=models.CASCADE)

class ProList(models.Model):
	PhoneID = models.ForeignKey(Phone, on_delete=models.CASCADE)
	SiteID = models.ForeignKey(Site, on_delete=models.CASCADE)
	Pros = models.CharField(max_length = 200)

class ConList(models.Model):
	PhoneID = models.ForeignKey(Phone, on_delete=models.CASCADE)
	SiteID = models.ForeignKey(Site, on_delete=models.CASCADE)
	Cons = models.CharField(max_length = 200)

class CNETDetailedScore(models.Model):
	phoneID = models.ForeignKey(Phone, on_delete=models.CASCADE)
	Design = models.PositiveSmallIntegerField()
	Features = models.PositiveSmallIntegerField()
	Performance = models.PositiveSmallIntegerField()
	Camera = models.PositiveSmallIntegerField()
	Battery = models.PositiveSmallIntegerField()
	
