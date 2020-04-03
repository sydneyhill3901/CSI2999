from django.urls import path

from . import views

urlpatterns = [
			path("", views.index, name="index"),
			path("Manufacturer/<str:manufacturer>", views.Manufacturer, name="Manufacturer"),
			path("Review/<str:phoneName>", views.Review, name="Review"),
			path("NotFound/<str:phone>", views.NotFound, name="NotFound"),
			path("Search/", views.Search, name="Search")
				]
