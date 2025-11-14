from django.contrib import admin
from .models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "created_at")
    list_filter = ("user", "product")   # ФИЛЬТРЫ по юзерам и товарам
    ordering = ("-created_at",)
