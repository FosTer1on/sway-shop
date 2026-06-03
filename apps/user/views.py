from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import *
from .serializers import *

# 1. Отправка кода


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        phone = serializer.validated_data["phone_number"]

        # 🔴 Если пользователь уже существует
        if User.objects.filter(phone_number=phone).exists():
            return Response(
                {"detail": "Пользователь с таким номером уже существует"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🟢 Создаём пользователя
        user = User.objects.create_user(
            phone_number=phone,
            first_name=serializer.validated_data.get("first_name"),
            password=serializer.validated_data.get("password"),
            gender=serializer.validated_data.get("gender"),
        )

        user.is_active = True
        user.save()

        # 🔐 Сразу выдаём токены
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "detail": "Регистрация прошла успешно",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "phone_number": user.phone_number,
                    "gender": user.gender,
                }
            },
            status=status.HTTP_201_CREATED
        )


# Логин
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        phone = serializer.validated_data["phone_number"]
        password = serializer.validated_data["password"]

        user = authenticate(phone_number=phone, password=password)

        if not user:
            return Response(
                {"detail": "Неверный номер телефона или пароль"},
                status=status.HTTP_400_BAD_REQUEST
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "phone_number": user.phone_number,
                "gender": user.gender,
            }
        })


# 4. Выход из аккаунта
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()  # добавляем в чёрный список

            # деактивируем пользователя
            user = request.user
            user.is_active = False
            user.save()

            return Response({"detail": "Вы успешно вышли из аккаунта."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"detail": "Ошибка при выходе."}, status=status.HTTP_400_BAD_REQUEST)


# 5. Удаление аккаунта
class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"detail": "Аккаунт был успешно удалён."}, status=status.HTTP_204_NO_CONTENT)
