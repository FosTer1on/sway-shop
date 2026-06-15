from rest_framework import serializers

from .models import Cart, CartItem
from apps.product.serializers import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    size = serializers.CharField(source="size.name")
    size_id = serializers.IntegerField(source="size.id")

    base_price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "size",
            "size_id",
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

    class Meta:
        model = Cart
        fields = [
            "items",
            "items_total_price",
            "items_total_quantity",
        ]

    def get_items_total_price(self, obj):
        summary = sum(item.total_price for item in obj.items.all())
        return f"{int(summary):,}".replace(",", " ")

    def get_items_total_quantity(self, obj):
        summary = sum(item.quantity for item in obj.items.all())
        return f"{int(summary):,}".replace(",", " ")