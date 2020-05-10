from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from rest_framework import status

from rest_framework.views import APIView

from project.custom_functions import api2_response
from .models import City, GoalOfSupport
from users.models import Support
from .serializers import RegionsAndCitiesSerializers, CitiesSerializers, RegionCitiesSerializers, ReadGoalOfSupport


def get_all_regions_with_cities(request):
    if request.method == "GET":
        regions_cities = City.objects.filter(parent__isnull=True)
        serializer = RegionCitiesSerializers(regions_cities, many=True)
        return JsonResponse(serializer.data, safe=False)


# all regions list
def get_all_reqions(request):
    if request.method == "GET":
        regions = City.objects.filter(parent__isnull=True)
        serializer = RegionsAndCitiesSerializers(regions, many=True)
        return JsonResponse(serializer.data, safe=False)


# get one region by id
def get_regiony(request, pk):
    if request.method == "GET":
        region = City.objects.filter(parent__isnull=True, pk=pk)
        serializer = RegionsAndCitiesSerializers(region, many=True)
        return JsonResponse(serializer.data[0], safe=False)


# get one region by id
def get_city(request, pk):
    if request.method == "GET":
        city = City.objects.filter(parent__isnull=False, pk=pk)
        serializer = CitiesSerializers(city, many=True)
        return JsonResponse(serializer.data[0], safe=False)


# get all cities list
def get_all_cities(request):
    if request.method == "GET":
        cities = City.objects.filter(parent__isnull=False)
        serializer = CitiesSerializers(cities, many=True)
        return JsonResponse(serializer.data, safe=False)


# get all cities of region
def get_all_cities_of_region(request, region_id):
    if request.method == "GET":
        cities = City.objects.filter(parent=region_id)
        serializer = RegionsAndCitiesSerializers(cities, many=True)
        return JsonResponse(serializer.data, safe=False)


#todo get all goals of support
def get_goal_of_support(request):
    goal_of_support = GoalOfSupport.objects.all()
    serializer = ReadGoalOfSupport(goal_of_support, many=True)
    return JsonResponse(serializer.data, safe=False)


class Supports(APIView):
    status_code = status.HTTP_200_OK
    detail = "Сообщение отправлена на поддержку, ответим в течении 1 дня"
    data = {}
    safe = True

    def get(self, request):
        goal_of_support = GoalOfSupport.objects.all()
        serializer = ReadGoalOfSupport(goal_of_support, many=True)
        if request.version == 'v2':
            self.safe = False
            self.detail = "Причины оброщений"
            self.data = serializer.data
            return api2_response(self)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request):
        support = Support.objects.create(user=request.user, goal_of_support_id=request.data['goal'],
                                         title=request.data['title'], description=request.data['description'])
        support.save()
        if request.version == 'v2':
            self.safe = False
            return api2_response(self)
        return JsonResponse({"status": True}, safe=False)


class PromotionsView(APIView):
    status_code = status.HTTP_200_OK
    detail = "Платный рекламный баннер"
    data = {}
    safe = True

    def get(self, request):
        result = {
            "url": "",
            "alt": "Реклама на сайте Kupizalog.kz",
            "link": ""
            }
        url = "https://api.kupizalog.kz/media/images/photo5402448618302057985.jpg"
        # link = 'youtube_shortlink_promo_video_or_learn_how_to_use'
        link = 'registration'
        result['url'] = url
        result['link'] = link
        if request.version == 'v2':
            self.data = result
            self.safe = False
            return api2_response(self)
        return JsonResponse(result, safe=False)


class CitiesView(APIView):
    status_code = status.HTTP_200_OK
    detail = "Города"
    data = {}
    safe = False

    def get(self, request, pk=0):
        if pk:
            city = City.objects.get(pk=pk)
            self.detail = "Город"
            serializer = CitiesSerializers(city)
        else:
            city = City.objects.filter(parent__isnull=False)
            serializer = CitiesSerializers(city, many=True)
        if request.version == 'v2':
            self.data = serializer.data
            return api2_response(self)
        return JsonResponse(serializer.data, safe=self.safe)


class RegionsView(APIView):
    status_code = status.HTTP_200_OK
    detail = "Регионы"
    data = {}
    safe = False

    def get(self, request, pk=0):
        if pk:
            region = City.objects.get(pk=pk)
            serializer = RegionsAndCitiesSerializers(region)
            self.detail = "Регион"
        else:
            regions = City.objects.filter(parent__isnull=True)
            serializer = RegionCitiesSerializers(regions, many=True)
        if request.version == 'v2':
            self.data = serializer.data
            return api2_response(self)
        return JsonResponse(serializer.data, safe=self.safe)