from rest_framework import serializers
from decimal import Decimal

from .models import Cart, CartItem
from apps.product.serializers import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    size = serializers.CharField(source="size.name")

    base_price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "size",
            "quantity",
            "base_price",
            "total_price",
        ]

    def get_base_price(self, obj):
        return f"{int(obj.product.price):,}".replace(",", " ")

    def get_total_price(self, obj):
        return f"{int(obj.total_price):,}".replace(",", " ")


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)
    items_total_price = serializers.SerializerMethodField()
    items_total_quantity = serializers.SerializerMethodField()
    total_with_service = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "items",
            "items_total_price",
            "items_total_quantity",
            "total_with_service"
        ]

    def get_items_total_price(self, obj):
        return sum(item.total_price for item in obj.items.all())

    def get_items_total_quantity(self, obj):
        return sum(item.quantity for item in obj.items.all())

    def get_total_with_service(self, obj):
        return self.get_items_total_price(obj) * Decimal("0.03") + self.get_items_total_price(obj)
