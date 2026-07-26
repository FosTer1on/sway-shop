from rest_framework import serializers
from .models import *
from utils.storage import build_public_url


# class StoreSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Store
#         fields = ["id", "name", "slug", "created_at", "updated_at"]


class BrandSerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ["id", "name", "slug", "icon_url", "sort_order",
            "is_active", "created_at", "updated_at"]

    def get_icon_url(self, obj):
        if not obj.icon:
            return None
        return build_public_url(obj.icon.name)


class CategorySerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "icon_url", "sort_order",
            "is_active", "created_at", "updated_at"]

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


class ProductColorVariantSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "color_name",
            "color_hex",
            "image_url",
        ]

    def get_image_url(self, obj):
        image = obj.images.first()
        if not image or not image.image:
            return None
        return build_public_url(image.image.name)


class ProductListSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    region = serializers.CharField(source="get_region_display")
    gender_display = serializers.CharField(source="get_gender_display")

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
            # "store",
            "region",
            "gender",
            "gender_display",
            "image_url",
            "delivery_time",
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
    
    def get_image_url(self, obj):
        image = obj.images.first()
        if not image or not image.image:
            return None
        return build_public_url(image.image.name)


class ProductSizeSerializer(serializers.ModelSerializer):
    size = serializers.CharField(source="size.name", read_only=True)
    size_id = serializers.IntegerField(source="size.id", read_only=True)

    class Meta:
        model = ProductSize
        fields = ["size_id", "size", "quantity"]


class SizeChartSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeChart
        fields = ["id", "name", "title", "note", "columns", "rows"]


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    sizes = ProductSizeSerializer(many=True, read_only=True)
    brand = BrandSerializer(read_only=True)
    # store = StoreSerializer(read_only=True)
    final_price = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    gender_display = serializers.CharField(source="get_gender_display")
    size_chart = SizeChartSerializer(read_only=True)
    color_variants = serializers.SerializerMethodField()

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
            # "store",
            "category",
            "region",
            "delivery_time",
            "gender",
            "gender_display",
            "size_chart",
            "images",
            "sizes",
            "variant_group",
            "color_name",
            "color_hex",
            "color_variants",
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

    def get_color_variants(self, obj):
        if not obj.variant_group_id:
            return []

        variants = (
            Product.objects
            .filter(
                variant_group_id=obj.variant_group_id,
                is_active=True,
            )
            .prefetch_related("images")
            .order_by("id")
        )   

        return ProductColorVariantSerializer(variants, many=True).data


class OutfitImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = OutfitImage
        fields = [
            "id",
            "image_url",
            "order",
        ]

    def get_image_url(self, obj):
        if not obj.image:
            return None

        return build_public_url(obj.image.name)


class OutfitListSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)
    price = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    gender_display = serializers.CharField(source="get_gender_display")
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Outfit
        fields = [
            "id",
            "title",
            "slug",
            "image_url",
            "description",
            "price",
            "final_price",
            "discount",
            "gender",
            "gender_display",
            "products_count",
            "delivery_time",
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

    def get_image_url(self, obj):
        image = obj.images.first()

        if not image or not image.image:
            return None

        return build_public_url(image.image.name)


class OutfitItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer()

    class Meta:
        model = OutfitItem
        fields = ["id", "product", "order"]


class OutfitSerializer(serializers.ModelSerializer):
    items = OutfitItemSerializer(many=True)

    price = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    gender_display = serializers.CharField(source="get_gender_display")
    images = OutfitImageSerializer(many=True, read_only=True)

    class Meta:
        model = Outfit
        fields = [
            "id",
            "title",
            "slug",
            "images",
            "description",
            "price",
            "final_price",
            "discount",
            "gender",
            "gender_display",
            "items",
            "delivery_time",
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


class UserEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEvent
        fields = [
            "id",
            "event_type",
            "product_slug",
            "search_query",
            "page_url",
            "session_id",
            "metadata",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
