from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Cart, CartItem
from apps.product.models import Product, Size

from .serializers import CartSerializer


def get_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


# 👉 1. Получить корзину
class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = get_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

# 👉 2. Добавить товар
class CartAddView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_slug = request.data.get("product")
        size_id = request.data.get("size")
        quantity = int(request.data.get("quantity", 1))

        if not product_slug or not size_id:
            return Response({"detail": "product и size обязательны"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(slug=product_slug)
            size = Size.objects.get(id=size_id)
        except (Product.DoesNotExist, Size.DoesNotExist):
            return Response({"detail": "Товар или размер не найдены"}, status=status.HTTP_404_NOT_FOUND)

        cart = get_cart(request.user)

        # Если этот же товар + размер уже есть → увеличиваем кол-во
        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, size=size
        )

        if created:
            item.quantity = quantity
        else:
            item.quantity += quantity

        item.save()

        return Response({"detail": "Добавлено"}, status=status.HTTP_201_CREATED)


# 👉 3. Изменить количество
class CartUpdateQuantityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        quantity = request.data.get("quantity")
        item_id = request.data.get("item_id")

        if not quantity:
            return Response({"detail": "quantity обязателен"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({"detail": "Элемент не найден"}, status=status.HTTP_404_NOT_FOUND)

        item.quantity = int(quantity)
        item.save()

        return Response({"detail": "Количество изменено"})


# 👉 4. Удалить товар
class CartDeleteItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({"detail": "Элемент не найден"}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        return Response({"detail": "Удалено"})
