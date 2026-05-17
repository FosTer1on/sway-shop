from django.db.models import F, ExpressionWrapper, DecimalField
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny


# ✅ Кастомная пагинация (по 30 товаров)
class ProductPagination(PageNumberPagination):
    page_size = 12


# ✅ 1. Получение всех товаров
class ProductListAPIView(APIView):
    def get(self, request):
        queryset = Product.objects.filter(is_active=True).select_related(
            "brand",
            "store",
            "category",
        ).prefetch_related(
            "images",
            "sizes",
            "sizes__size",
        )

        queryset = queryset.annotate(
            final_price_calc=ExpressionWrapper(
                F("price") - (F("price") * F("discount") / 100),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )

        stores = request.GET.getlist("store")
        brands = request.GET.getlist("brand")
        categories = request.GET.getlist("category")
        sizes = request.GET.getlist("size")

        region = request.GET.get("region")

        min_price = request.GET.get("min_price")
        max_price = request.GET.get("max_price")
        discount_only = request.GET.get("discount")
        status_param = request.GET.get("status")
        order_by = request.GET.get("order_by")

        if stores:
            queryset = queryset.filter(store__slug__in=stores)

        if brands:
            queryset = queryset.filter(brand__slug__in=brands)

        if categories:
            queryset = queryset.filter(category__slug__in=categories)

        if sizes:
            queryset = queryset.filter(
                sizes__size__id__in=sizes,
                sizes__quantity__gt=0
            ).distinct()

        if region:
            queryset = queryset.filter(region__iexact=region)

        if min_price:
            queryset = queryset.filter(final_price_calc__gte=min_price)

        if max_price:
            queryset = queryset.filter(final_price_calc__lte=max_price)

        if str(discount_only).lower() == "true":
            queryset = queryset.filter(discount__gt=0)

        if status_param:
            queryset = queryset.filter(status=status_param)

        has_filters = any([
            stores, brands, categories, sizes,
            region,
            min_price, max_price,
            discount_only, status_param
        ])

        if order_by == "price_asc":
            queryset = queryset.order_by("final_price_calc", "id")
        elif order_by == "price_desc":
            queryset = queryset.order_by("-final_price_calc", "-id")
        else:
            if not has_filters:
                queryset = queryset.order_by("-is_season", "created_at", "id")
            else:
                queryset = queryset.order_by("created_at", "id")

        paginator = ProductPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ProductListSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


# ✅ 2. Получение конкретного товара по slug
class ProductDetailAPIView(APIView):
    def get(self, request, slug):
        try:
            product = Product.objects.select_related(
                "brand",
                "store",
                "category",
            ).prefetch_related(
                "images",
                "sizes",
                "sizes__size",
            ).get(slug=slug, is_active=True)
        except Product.DoesNotExist:
            return Response({"detail": "Товар не найден"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)


class ProductSearchAPIView(APIView):
    def get(self, request):
        query = request.GET.get("q")

        if not query:
            return Response({"results": []})

        queryset = Product.objects.filter(
            is_active=True,
            name__icontains=query
        ).select_related(
            "store",
            "brand",
            "category",
        ).prefetch_related(
            "images",
            "sizes",
            "sizes__size",
        ).annotate(
            final_price_calc=ExpressionWrapper(
                F("price") - (F("price") * F("discount") / 100),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        ).order_by("-created_at")

        paginator = ProductPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ProductListSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class StoreListView(APIView):
    def get(self, request):
        stores = Store.objects.only("id", "name", "slug", "created_at", "updated_at")
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)


class BrandListView(APIView):
    def get(self, request):
        brands = Brand.objects.only("id", "name", "slug", "icon", "created_at", "updated_at")
        serializer = BrandSerializer(brands, many=True)
        return Response(serializer.data)


class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.only("id", "name", "slug", "icon", "created_at", "updated_at")
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class CategorySizesView(APIView):
    def get(self, request, slug):
        try:
            category = Category.objects.select_related(
                "size_type").get(slug=slug)
        except Category.DoesNotExist:
            return Response({"detail": "Категория не найдена"}, status=status.HTTP_404_NOT_FOUND)

        sizes = Size.objects.filter(size_type=category.size_type)
        serializer = SizeSerializer(sizes, many=True)
        return Response(serializer.data)
