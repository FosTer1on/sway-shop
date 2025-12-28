from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Sum, F
from decimal import Decimal

from .models import Order, OrderItem
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
)
from django.db import transaction


class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        data = serializer.validated_data

        cart = getattr(user, "cart", None)
        if not cart or cart.items.count() == 0:
            return Response({"detail": "Корзина пуста"}, status=status.HTTP_400_BAD_REQUEST)

        # авто-подстановка ФИО и телефона
        full_name = data.get("full_name") or user.full_name
        phone = data.get("phone_number") or user.phone_number
        address = data["address"]

        # считаем суммы
        products_total = sum([item.total_price for item in cart.items.all()])

        service_fee_amount = products_total * Decimal("0.05")
        final_total = products_total + service_fee_amount

        # создаем заказ
        order = Order.objects.create(
            user=user,
            full_name=full_name,
            phone_number=phone,
            address=address,
            payment_method=data["payment_method"],
            products_total=products_total,
            service_fee_amount=service_fee_amount,
            final_total=final_total,
        )

        # копируем товары в заказ
        order_items = [
            OrderItem(
                order=order,
                product=item.product,
                size=item.size,
                quantity=item.quantity,
                price=item.product.price,
                price_with_discount=item.product.final_price,
                final_price=item.total_price,
            )
            for item in cart.items.all()
        ]
        OrderItem.objects.bulk_create(order_items)

        # сохраняем адрес пользователя, если пустой
        profile = getattr(user, "profile", None)
        if profile and not profile.address:
            profile.address = address
            profile.save()

        # чистим корзину
        cart.items.all().delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class UserOrdersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = (
            Order.objects
            .filter(user=request.user)
            .select_related("user")
            .prefetch_related("items")
            .order_by("-created_at")
        )

        return Response(OrderListSerializer(orders, many=True).data)


class UserOrderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(
            Order.objects.select_related("user").prefetch_related("items__product"),
            id=order_id,
            user=request.user
        )

        return Response(OrderDetailSerializer(order).data)
