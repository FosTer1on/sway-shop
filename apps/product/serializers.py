from rest_framework import serializers
from .models import *


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ["id", "name", "slug", "created_at", "updated_at"]


class BrandSerializer(serializers.ModelSerializer):
    icon = serializers.ImageField(read_only=True)

    class Meta:
        model = Brand
        fields = ["id", "name", "slug", "icon", "created_at", "updated_at"]


class CategorySerializer(serializers.ModelSerializer):
    icon = serializers.ImageField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "icon", "created_at", "updated_at"]


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ["id", "name"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image"]


class ProductListSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    final_price = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "price", "final_price",
            "discount", "status", "is_season", "brand", "store", "images"
        ]

    def get_price(self, obj):
        return f"{int(obj.price):,}".replace(",", " ")

    def get_final_price(self, obj):
        final = obj.price - (obj.price * obj.discount / 100)
        return f"{int(final):,}".replace(",", " ")


class ProductSizeSerializer(serializers.ModelSerializer):
    size = serializers.CharField(source="size.name")

    class Meta:
        model = ProductSize
        fields = ["size_id", "size", "quantity"]


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    sizes = ProductSizeSerializer(many=True, read_only=True)
    brand = BrandSerializer(read_only=True)
    store = StoreSerializer(read_only=True)
    final_price = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"

    def get_price(self, obj):
        return f"{int(obj.price):,}".replace(",", " ")

    def get_final_price(self, obj):
        final = obj.price - (obj.price * obj.discount / 100)
        return f"{int(final):,}".replace(",", " ")