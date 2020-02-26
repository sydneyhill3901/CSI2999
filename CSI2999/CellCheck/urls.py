from django.urls import path

from . import views

urlpatterns = [
			path("", views.index, name="index"),
			path("Manufacturer/", views.Manufacturer, name="Manufacturer"),
			path("Review/", views.Review, name="Review")
				]
