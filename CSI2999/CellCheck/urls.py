from django.urls import path

from . import views

urlpatterns = [
			path("", views.index, name="index"),
			path("Manufacturer/", views.Manufacturer, name="ManufacturerEmpty"),
			path("Manufacturer/<str:manufacturer>", views.Manufacturer, name="Manufacturer"),
			path("Review/", views.Review, name="ReviewEmpty"),
			path("Review/<str:phoneName>", views.Review, name="Review"),
			path("NotFound/", views.NotFound, name="NotFoundEmpty"),
			path("NotFound/<str:phone>", views.NotFound, name="NotFound"),
			path("Search/", views.Search, name="Search"),
			path("ajax/queryData/<str:phone>", views.queryPriceAPI, name="queryPriceAPI")
				]
