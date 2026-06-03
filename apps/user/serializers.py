from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=50)
    phone_number = serializers.CharField(max_length=15)
    password = serializers.CharField(min_length=6, write_only=True)

    gender = serializers.ChoiceField(
        choices=["male", "female"],
        required=True
    )

    def validate_phone_number(self, value):
        if not value.startswith("+998"):
            raise serializers.ValidationError("Неверный формат номера")
        return value

    def validate(self, attrs):
        if User.objects.filter(phone_number=attrs["phone_number"]).exists():
            raise serializers.ValidationError(
                {"phone_number": "Пользователь с таким номером уже существует"}
            )
        return attrs


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()
