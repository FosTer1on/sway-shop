from django.db.models import Q, F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import *
from .serializers import *


# ✅ Кастомная пагинация (по 30 товаров)
class ProductPagination(PageNumberPagination):
    page_size = 30


# ✅ 1. Получение всех товаров
class ProductListAPIView(APIView):
    def get(self, request):
        queryset = Product.objects.filter(is_active=True)

        # --- 🔹 Фильтры ---
        store = request.GET.get("store")
        brand = request.GET.get("brand")
        category = request.GET.get("category")
        min_price = request.GET.get("min_price")
        max_price = request.GET.get("max_price")
        discount_only = request.GET.get("discount")
        status_param = request.GET.get("status")
        order_by = request.GET.get("order_by")  # 'price_asc' или 'price_desc'

        if store:
            queryset = queryset.filter(store__slug=store)
        if brand:
            queryset = queryset.filter(brand__slug=brand)
        if category:
            queryset = queryset.filter(category__slug=category)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if discount_only == "true":
            queryset = queryset.filter(discount__gt=0)
        if status_param:
            queryset = queryset.filter(status=status_param)

        # --- 🔹 Если фильтров нет — сортируем с приоритетом сезонных ---
        has_filters = any([store, brand, category, min_price, max_price, discount_only, status_param])
        if not has_filters:
            queryset = queryset.order_by("-is_season", "-created_at")
        else:
            queryset = queryset.order_by("-created_at")

        # --- 🔹 Сортировка по цене ---
        if order_by == "price_asc":
            queryset = queryset.order_by(F("final_price").asc(nulls_last=True))
        elif order_by == "price_desc":
            queryset = queryset.order_by(F("final_price").desc(nulls_last=True))

        # --- 🔹 Пагинация ---
        paginator = ProductPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ProductListSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


# ✅ 2. Получение конкретного товара по slug
class ProductDetailAPIView(APIView):
    def get(self, request, slug):
        try:
            product = Product.objects.prefetch_related("images", "sizes").get(slug=slug, is_active=True)
        except Product.DoesNotExist:
            return Response({"detail": "Товар не найден"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)


class StoreListView(APIView):
    def get(self, request):
        stores = Store.objects.all()
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)


class BrandListView(APIView):
    def get(self, request):
        brands = Brand.objects.all()
        serializer = BrandSerializer(brands, many=True)
        return Response(serializer.data)


class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class CategorySizesView(APIView):
    def get(self, request, slug):
        try:
            category = Category.objects.select_related("size_type").get(slug=slug)
        except Category.DoesNotExist:
            return Response({"detail": "Категория не найдена"}, status=status.HTTP_404_NOT_FOUND)

        sizes = Size.objects.filter(size_type=category.size_type)
        serializer = SizeSerializer(sizes, many=True)
        return Response(serializer.data)