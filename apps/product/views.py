from django.db.models import F, ExpressionWrapper, DecimalField, Count, Q, CharField, Value
from django.db.models.functions import MD5, Cast, Concat
from datetime import date
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny


# Кастомная пагинация товаров (по 30 товаров)
class ProductPagination(PageNumberPagination):
    page_size = 30


# Кастомная пагинация аутфитов (по 30 товаров)
class OutfitPagination(PageNumberPagination):
    page_size = 30


# Получение всех товаров + фильтрация
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
        gender = request.GET.get("gender")

        search = request.GET.get("search", "").strip()

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

        if search:
            search_variants = {
                search,
                search.lower(),
                search.upper(),
                search.capitalize(),
                search.title(),
            }

            query = Q()

            for value in search_variants:
                query |= Q(name__icontains=value)
                query |= Q(name_ru__icontains=value)
                query |= Q(name_uz__icontains=value)
                query |= Q(brand__name__icontains=value)

            queryset = queryset.filter(query).distinct()

        if region:
            queryset = queryset.filter(region__iexact=region)

        if gender in ["male", "female"]:
            queryset = queryset.filter(
                gender__in=[gender, Product.Gender.UNISEX])
        elif gender == "all":
            pass
        else:
            user_gender = getattr(request.user, "gender", None)

            if request.user.is_authenticated and user_gender in ["male", "female"]:
                queryset = queryset.filter(
                    gender__in=[user_gender, Product.Gender.UNISEX])

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
            region, gender!= "all", search,
            min_price, max_price,
            discount_only, status_param
        ])

        if order_by == "price_asc":
            queryset = queryset.order_by("final_price_calc", "id")
        elif order_by == "price_desc":
            queryset = queryset.order_by("-final_price_calc", "-id")
        else:
            if not has_filters:
                daily_seed = date.today().strftime("%Y%m%d")

                queryset = queryset.annotate(
                    daily_random=MD5(
                        Concat(
                            Value(daily_seed),
                            Cast("id", output_field=CharField()),
                            output_field=CharField(),
                        )
                    )
                ).order_by("-is_season", "daily_random")
            else:
                queryset = queryset.order_by("created_at", "id")

        paginator = ProductPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = ProductListSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


# Получение конкретного товара по slug
class ProductDetailAPIView(APIView):
    def get(self, request, slug):
        try:
            product = Product.objects.select_related(
                "brand",
                "store",
                "category",
                "size_chart",
            ).prefetch_related(
                "images",
                "sizes",
                "sizes__size",
            ).get(slug=slug, is_active=True)
        except Product.DoesNotExist:
            return Response({"detail": "Товар не найден"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)


# Получение всех магазинов
class StoreListView(APIView):
    def get(self, request):
        stores = Store.objects.only(
            "id", "name", "slug", "created_at", "updated_at")
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)


# Получение всех брендов
class BrandListView(APIView):
    def get(self, request):
        brands = Brand.objects.only(
            "id", "name", "slug", "icon", "created_at", "updated_at")
        serializer = BrandSerializer(brands, many=True)
        return Response(serializer.data)


# Получение всех категорий
class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.only(
            "id", "name", "slug", "icon", "created_at", "updated_at")
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


# Получение всех размеров категории
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


# Получение всех аутфитов
class OutfitListAPIView(APIView):
    def get(self, request):
        queryset = Outfit.objects.filter(is_active=True)

        queryset = queryset.annotate(
            final_price_calc=ExpressionWrapper(
                F("price") - (F("price") * F("discount") / 100),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            ),
            products_count=Count("items")
        )

        min_price = request.GET.get("min_price")
        max_price = request.GET.get("max_price")
        order_by = request.GET.get("order_by")

        gender = request.GET.get("gender")

        if gender in ["male", "female"]:
            queryset = queryset.filter(
                gender__in=[gender, Outfit.Gender.UNISEX])
        elif gender == "all":
            pass
        else:
            user_gender = getattr(request.user, "gender", None)

            if request.user.is_authenticated and user_gender in ["male", "female"]:
                queryset = queryset.filter(
                    gender__in=[user_gender, Outfit.Gender.UNISEX])

        if min_price:
            queryset = queryset.filter(final_price_calc__gte=min_price)

        if max_price:
            queryset = queryset.filter(final_price_calc__lte=max_price)

        has_filters = any([
            gender != "all",
            min_price,
            max_price,
        ])

        if order_by == "price_asc":
            queryset = queryset.order_by("final_price_calc", "id")
        elif order_by == "price_desc":
            queryset = queryset.order_by("-final_price_calc", "-id")
        else:
            if not has_filters:
                daily_seed = date.today().strftime("%Y%m%d")

                queryset = queryset.annotate(
                    daily_random=MD5(
                        Concat(
                            Value(daily_seed),
                            Cast("id", output_field=CharField()),
                            output_field=CharField(),
                        )
                    )
                ).order_by("daily_random")
            else:
                queryset = queryset.order_by("-id")

        paginator = OutfitPagination()
        page = paginator.paginate_queryset(queryset, request)

        serializer = OutfitListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


# Получение аутфита по slug
class OutfitDetailAPIView(APIView):
    def get(self, request, slug):
        outfit = get_object_or_404(
            Outfit.objects.prefetch_related(
                "items",
                "items__product",
                "items__product__images",
            ),
            slug=slug,
            is_active=True
        )

        serializer = OutfitSerializer(outfit)
        return Response(serializer.data)
