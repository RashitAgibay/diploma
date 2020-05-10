from rest_framework import serializers
from .models import City, GoalOfSupport


# todo
class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


# todo write description
class RegionsAndCitiesSerializers(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'slug', 'title']


# todo write descriptio
class RegionCitiesSerializers(serializers.ModelSerializer):

    children = RecursiveSerializer(many=True, read_only=True)

    class Meta:
        model = City
        fields = ['id', 'slug', 'title', 'children']


# todo write description
class CitiesSerializers(serializers.ModelSerializer):
    parent = RegionsAndCitiesSerializers(read_only=True)

    class Meta:
        model = City
        fields = ['id', 'slug', 'title', 'parent']


class ReturnCityTitleSerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ['title']


# todo goals of support
class ReadGoalOfSupport(serializers.ModelSerializer):

    class Meta:
        model = GoalOfSupport
        fields = '__all__'