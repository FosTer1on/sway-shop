from rest_framework import serializers
from apps.product.serializers import ProductListSerializer
from .models import Order, OrderItem

def format_price(value):
    return f"{value:,.0f}".replace(",", " ")


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_image = serializers.ImageField(source="product.image", read_only=True)

    price = serializers.SerializerMethodField()
    price_with_discount = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_name",
            "product_image",
            "size",
            "quantity",
            "price",
            "price_with_discount",
            "final_price",
        ]

    def get_price(self, obj):
        return format_price(obj.price)

    def get_price_with_discount(self, obj):
        return format_price(obj.price_with_discount)

    def get_final_price(self, obj):
        return format_price(obj.final_price)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "full_name",
            "phone_number",
            "address",
            "payment_method",
            "status",
            "products_total",
            "final_total",
            "items",
            "created_at",
        ]


class OrderCreateSerializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_METHODS)
    address = serializers.CharField(required=True)
    full_name = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)


class OrderListSerializer(serializers.ModelSerializer):
    items_count = serializers.IntegerField(source="items.count", read_only=True)

    products_total = serializers.SerializerMethodField()
    final_total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "items_count",
            "payment_method",
            "status",
            "products_total",
            "final_total",
            "created_at",
        ]

    def get_products_total(self, obj):
        return format_price(obj.products_total)

    def get_final_total(self, obj):
        return format_price(obj.final_total)


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    products_total = serializers.SerializerMethodField()
    final_total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "full_name",
            "phone_number",
            "address",
            "payment_method",
            "status",
            "products_total",
            "final_total",
            "created_at",
            "items",
        ]

    def get_products_total(self, obj):
        return format_price(obj.products_total)

    def get_final_total(self, obj):
        return format_price(obj.final_total)
