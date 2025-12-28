from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *

class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone_number = serializers.CharField()
    password = serializers.CharField(min_length=6)

    def validate_phone_number(self, value):
        if not value.startswith("+998"):
            raise serializers.ValidationError("Неверный формат номера")
        return value

    def validated_data_with_hashed_password(self):
        data = self.validated_data.copy()
        data["password"] = make_password(data["password"])
        return data

class VerifyCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6)

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'id', 'first_name', 'last_name', 'phone_number', 'avatar',
            'gender', 'address', 'city', 'date_of_birth',
            'created_at', 'updated_at'
        ]