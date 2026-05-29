from rest_framework import serializers
from .models import *
from utils.storage import build_public_url


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ["id", "name", "slug", "created_at", "updated_at"]


class BrandSerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ["id", "name", "slug", "icon_url", "created_at", "updated_at"]

    def get_icon_url(self, obj):
        if not obj.icon:
            return None
        return build_public_url(obj.icon.name)


class CategorySerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "icon_url", "created_at", "updated_at"]

    def get_icon_url(self, obj):
        if not obj.icon:
            return None
        return build_public_url(obj.icon.name)


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ["id", "name"]


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["image_url"]

    def get_image_url(self, obj):
        if not obj.image:
            return None
        return build_public_url(obj.image.name)


class ProductListSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    final_price = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    region = serializers.CharField(source="get_region_display")

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "price",
            "final_price",
            "discount",
            "status",
            "is_season",
            "brand",
            "store",
            "region",
            "images",
        ]

    def get_price(self, obj):
        return f"{int(obj.price):,}".replace(",", " ")

    def get_final_price(self, obj):
        final = getattr(
            obj,
            "final_price_calc",
            obj.price - (obj.price * obj.discount / 100)
        )
        return f"{int(final):,}".replace(",", " ")


class ProductSizeSerializer(serializers.ModelSerializer):
    size = serializers.CharField(source="size.name", read_only=True)
    size_id = serializers.IntegerField(source="size.id", read_only=True)

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
    region = serializers.CharField(source="get_region_display")

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "price",
            "final_price",
            "discount",
            "quantity",
            "is_active",
            "is_season",
            "status",
            "brand",
            "store",
            "category",
            "region",
            "images",
            "sizes",
            "created_at",
            "updated_at",
        ]

    def get_price(self, obj):
        return f"{int(obj.price):,}".replace(",", " ")

    def get_final_price(self, obj):
        final = getattr(
            obj,
            "final_price_calc",
            obj.price - (obj.price * obj.discount / 100)
        )
        return f"{int(final):,}".replace(",", " ")



class OutfitListSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)
    price = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = Outfit
        fields = [
            "id",
            "title",
            "slug",
            "image",
            "description",
            "price",
            "final_price",
            "discount",
            "products_count",
        ]

    def get_price(self, obj):
        return f"{int(obj.price):,}".replace(",", " ")

    def get_final_price(self, obj):
        final = getattr(
            obj,
            "final_price_calc",
            obj.price - (obj.price * obj.discount / 100)
        )
        return f"{int(final):,}".replace(",", " ")


class OutfitItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer()

    class Meta:
        model = OutfitItem
        fields = ["id", "product", "order"]


class OutfitSerializer(serializers.ModelSerializer):
    items = OutfitItemSerializer(many=True)

    price = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = Outfit
        fields = [
            "id",
            "title",
            "slug",
            "image",
            "description",
            "price",
            "final_price",
            "discount",
            "items",
        ]

    def get_price(self, obj):
        return f"{int(obj.price):,}".replace(",", " ")

    def get_final_price(self, obj):
        final = getattr(
            obj,
            "final_price_calc",
            obj.price - (obj.price * obj.discount / 100)
        )

        return f"{int(final):,}".replace(",", " ")
