from django.contrib import admin
from .models import Phone, Site, Rating, ConList, ProList, CNETDetailedScore

# Register your models here.

admin.site.register(Phone)
admin.site.register(Site)
admin.site.register(Rating)
admin.site.register(ConList)
admin.site.register(ProList)
admin.site.register(CNETDetailedScore)

