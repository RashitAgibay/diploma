from django.urls import path
from unique import views
from .views import *

urlpatterns = [
    path('regions/cities', views.get_all_regions_with_cities),
    path('regions', views.get_all_reqions),
    path('region', RegionsView.as_view()),
    path('region/<int:pk>', RegionsView.as_view()),
    path('city/<int:pk>', CitiesView.as_view()),
    path('cities', CitiesView.as_view()),
    path('region-cites/<int:region_id>', views.get_all_cities_of_region),
    path('support', Supports.as_view()),
    path('goal-support', Supports.as_view()),
    path('promotion-ads/', PromotionsView.as_view())
]