from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "id",
        "phone_number",
        "first_name",
        "gender",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    list_filter = (
        "gender",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    search_fields = (
        "phone_number",
        "first_name",
    )

    ordering = ("id",)

    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("Personal info", {"fields": ("first_name", "gender")}),
        ("Permissions", {"fields": ("is_active", "is_staff",
         "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone_number", "first_name", "gender", "password1", "password2"),
        }),
    )
