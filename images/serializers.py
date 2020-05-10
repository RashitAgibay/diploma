from rest_framework import serializers
from .models import Image


class ImageSerializer(serializers.ModelSerializer):
    path = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ['path']

    def get_path(self, Image)->str:
        return Image.path.url