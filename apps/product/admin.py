from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TranslationAdmin
from .models import *
from utils.storage import build_public_url

# ==========================
# 🔹 CATEGORY (с переводом)
# ==========================


@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ("name", "slug", "created_at", "updated_at")
    readonly_fields = ("slug",)

    def get_fields(self, request, obj=None):
        fields = ["name", "size_type", "icon"]
        if obj:
            fields.insert(1, "slug")
        return fields

    # fieldsets = (
    #     ("Основная информация", {
    #         "fields": ("name", "size_type", "icon")
    #     }),
    # )

    # def get_readonly_fields(self, request, obj=None):
    #     if obj:
    #         return self.readonly_fields
    #     return ()


# ==========================
# 🔹 BRAND (без перевода)
# ==========================
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at", "updated_at")
    readonly_fields = ("slug",)

    def get_fields(self, request, obj=None):
        fields = ["name", "icon"]
        if obj:
            fields.insert(1, "slug")
        return fields


# ==========================
# 🔹 STORE (без перевода)
# ==========================
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at", "updated_at")
    readonly_fields = ("slug",)

    def get_fields(self, request, obj=None):
        fields = ["name"]
        if obj:
            fields.insert(1, "slug")
        return fields


# ==========================
# 🔹 INLINE для фото продукта
# ==========================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "preview")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.image and getattr(obj.image, "name", None):
            url = build_public_url(obj.image.name)  # ✅ name, а не url
            return format_html('<img src="{}" width="80" style="border-radius:6px"/>', url)
        return "—"
    preview.short_description = "Превью"


# ==========================
# 🔹 INLINE для размеров товара
# ==========================
class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1
    fields = ("size", "quantity")
    autocomplete_fields = ("size",)
    verbose_name = "Размер"
    verbose_name_plural = "Размеры и количество"

    # 🔹 фильтрация размеров по SizeType категории продукта
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "size":
            # Получаем ID продукта из URL (для inline)
            product_id = request.resolver_match.kwargs.get("object_id")
            if product_id:
                from .models import Product
                try:
                    product = Product.objects.select_related(
                        "category__size_type").get(pk=product_id)
                    size_type = getattr(product.category, "size_type", None)
                    if size_type:
                        field.queryset = field.queryset.filter(
                            size_type=size_type)
                except Product.DoesNotExist:
                    pass
        return field


# ==========================
# 🔹 PRODUCT (с переводом)
# ==========================
@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    list_display = (
        "admin_image_preview",
        "name",
        "store",
        "price",
        "discount",
        "final_price",
        "is_season",
        "is_active",
        "status",
        "created_at",
        "updated_at",
    )
    list_display_links = ("name",)
    readonly_fields = ("slug",)
    inlines = [ProductImageInline, ProductSizeInline]

    # 🔹 Фильтры
    list_filter = ("is_season", "is_active", "status")

    fieldsets = (
        ("Основная информация", {
            "fields": (
                "name",
                "slug",
                "store", "category", "brand", "region",
                "description",
            )
        }),
        ("Цены и скидки", {
            "fields": ("price", "discount")
        }),
        ("Статус и активность", {
            "fields": ("status", "is_season", "is_active")
        }),
    )

    def admin_image_preview(self, obj):
        img = obj.images.first()
        if img and img.image and getattr(img.image, "name", None):
            url = build_public_url(img.image.name)  # ✅ name, а не url
            return format_html('<img src="{}" width="55" style="border-radius:5px"/>', url)
        return "—"
    admin_image_preview.short_description = "Фото"


# ==========================
# 🔹 SIZE TYPE (например: одежда, обувь)
# ==========================
@admin.register(SizeType)
class SizeTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


# ==========================
# 🔹 SIZE (например: S, M, L или 40, 41)
# ==========================
@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("name", "size_type")
    list_filter = ("size_type",)
    search_fields = ("name",)


# ==========================
# 🔹 PRODUCT SIZE (таблица связки)
# ==========================
@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ("product", "size", "quantity")
    list_filter = ("size__size_type", "product__store")
    search_fields = ("product__name", "size__name")

@admin.register(Outfit)
class Outfit(admin.ModelAdmin):
    list_display = ("image", "title")

@admin.register(OutfitItem)
class OutfitItem(admin.ModelAdmin):
    list_display = ("product__name",)