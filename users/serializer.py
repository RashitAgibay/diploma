from django.contrib.auth import get_user_model

from rest_framework import serializers

from images.serializers import ImageSerializer

User = get_user_model()


class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'  # ('phone', 'password')
        extra_kwargs = {'password': {'write_only': True}, }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    # validate_password = make_password


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'  # ('id', 'phone', 'first_login')


class UserProfileSerializer(serializers.ModelSerializer):
    image = ImageSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('phone', 'first_name', 'last_name', 'image', 'patronymic', 'email', 'city', 'date_of_birth')


class UserInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'patronymic', 'phone', 'email')


class OwnerSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'patronymic')
