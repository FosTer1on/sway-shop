from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "size", "quantity", "price", "price_with_discount", "final_price")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "full_name",
        "phone_number",
        "payment_method",
        "status",
        "products_total",
        "service_fee_amount",
        "final_total",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_method",
        "created_at",
    )

    search_fields = (
        "id",
        "user__username",
        "full_name",
        "phone_number",
    )

    readonly_fields = (
        "user",
        "products_total",
        "service_fee_amount",
        "final_total",
        "created_at",
    )

    inlines = [OrderItemInline]

    ordering = ("-created_at",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product",
        "size",
        "quantity",
        "price",
        "price_with_discount",
        "final_price",
    )

    list_filter = (
        "product",
        "size",
        "order__status",
    )

    search_fields = (
        "order__id",
        "product__name",
    )

    readonly_fields = (
        "order",
        "product",
        "size",
        "quantity",
        "price",
        "price_with_discount",
        "final_price",
    )

    ordering = ("-id",)
