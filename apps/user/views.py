from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import *
from .serializers import *
from .utils import send_confirmation_code

# 1. Отправка кода
class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        phone = serializer.validated_data["phone_number"]

        if User.objects.filter(phone_number=phone).exists():
            return Response(
                {"detail": "Пользователь с таким номером уже существует"},
                status=400
            )

        # 🔥 сохраняем / обновляем временного пользователя
        PendingUser.objects.update_or_create(
            phone_number=phone,
            defaults=serializer.validated_data_with_hashed_password()
        )

        # 🔥 создаем или обновляем код
        PhoneConfirmation.objects.update_or_create(
            phone_number=phone,
            defaults={"code": PhoneConfirmation.generate_code()}
        )

        send_confirmation_code(phone)

        return Response(
            {"detail": "Код отправлен"},
            status=status.HTTP_200_OK
        )


# 2. Подтверждение кода
class VerifyCodeView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        phone = serializer.validated_data["phone_number"]
        code = serializer.validated_data["code"]

        try:
            confirmation = PhoneConfirmation.objects.get(phone_number=phone)
        except PhoneConfirmation.DoesNotExist:
            return Response({"detail": "Код не найден"}, status=400)

        if confirmation.is_expired():
            confirmation.delete()
            return Response({"detail": "Код истёк"}, status=400)

        if confirmation.code != code:
            return Response({"detail": "Неверный код"}, status=400)

        try:
            pending = PendingUser.objects.get(phone_number=phone)
        except PendingUser.DoesNotExist:
            return Response({"detail": "Нет данных регистрации"}, status=400)

        if pending.is_expired():
            pending.delete()
            return Response({"detail": "Регистрация устарела"}, status=400)

        # 🔥 создаём пользователя
        user = User.objects.create(
            phone_number=phone,
            first_name=pending.first_name,
            last_name=pending.last_name,
            password=pending.password,
            is_active=True,
            is_confirmed=True
        )

        Profile.objects.create(
            user=user,
            phone_number=phone,
            first_name=pending.first_name,
            last_name=pending.last_name
        )

        # 🔐 АВТОЛОГИН — ВЫДАЧА JWT
        refresh = RefreshToken.for_user(user)

        # 🔥 чистим мусор
        pending.delete()
        confirmation.delete()

        return Response(
            {
                "detail": "Регистрация завершена",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone_number": user.phone_number,
                }
            },
            status=status.HTTP_201_CREATED
        )





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


# 6. Получение профиля
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile
