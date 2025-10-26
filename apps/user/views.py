from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import User, PhoneConfirmation
from .serializers import RegisterSerializer, VerifyCodeSerializer, LoginSerializer
from .utils import send_confirmation_code

# 1. Отправка кода
class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone_number']

            # 🔥 Проверяем, не существует ли уже пользователь с таким номером
            if User.objects.filter(phone_number=phone).exists():
                return Response(
                    {"detail": "Пользователь с таким номером уже существует."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            send_confirmation_code(phone)
            request.session['pending_user'] = serializer.validated_data
            return Response({"detail": "Код отправлен на номер телефона."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 2. Подтверждение кода
class VerifyCodeView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone_number']
            code = serializer.validated_data['code']

            try:
                confirmation = PhoneConfirmation.objects.get(phone_number=phone)
            except PhoneConfirmation.DoesNotExist:
                return Response({"detail": "Код не найден."}, status=status.HTTP_400_BAD_REQUEST)

            if confirmation.is_expired():
                confirmation.delete()
                return Response({"detail": "Код истёк."}, status=status.HTTP_400_BAD_REQUEST)

            if confirmation.code != code:
                return Response({"detail": "Неверный код."}, status=status.HTTP_400_BAD_REQUEST)

            data = request.session.get("pending_user")
            if not data or data['phone_number'] != phone:
                return Response({"detail": "Нет данных регистрации."}, status=status.HTTP_400_BAD_REQUEST)

            # ⚠️ Проверяем, не зарегистрирован ли уже пользователь
            if User.objects.filter(phone_number=phone).exists():
                confirmation.delete()
                return Response({"detail": "Пользователь с таким номером уже существует."},
                                status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create_user(
                phone_number=phone,
                first_name=data['first_name'],
                last_name=data['last_name'],
                password=data['password'],
            )
            user.is_confirmed = True
            user.save()

            confirmation.delete()
            del request.session['pending_user']

            return Response({"detail": "Регистрация завершена!"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# 3. Логин
class LoginView(APIView):
    permission_classes = []
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone_number']
            password = serializer.validated_data['password']
            user = authenticate(phone_number=phone, password=password)
            if not user:
                return Response({"detail": "Неверный номер телефона или пароль."}, status=status.HTTP_400_BAD_REQUEST)
            if not user.is_confirmed:
                return Response({"detail": "Аккаунт не подтвержден."}, status=status.HTTP_400_BAD_REQUEST)

            user.is_active = True
            user.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone_number": user.phone_number,
                }
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"detail": "Аккаунт был успешно удалён."}, status=status.HTTP_204_NO_CONTENT)

