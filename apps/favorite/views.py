from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import Favorite, Product
from .serializers import FavoriteSerializer


class FavoriteListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        favorites = Favorite.objects.filter(user=request.user)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddFavoriteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        try:
            product = Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            return Response({"detail": "Товар не найден"}, status=status.HTTP_404_NOT_FOUND)

        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            return Response({"detail": "Товар уже в избранном"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Добавлено в избранное"}, status=status.HTTP_201_CREATED)


class RemoveFavoriteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, slug):
        try:
            favorite = Favorite.objects.get(
                user=request.user,
                product__slug=slug
            )
        except Favorite.DoesNotExist:
            return Response({"detail": "Этого товара нет в избранном"}, status=status.HTTP_404_NOT_FOUND)

        favorite.delete()
        return Response({"detail": "Удалено из избранного"})
