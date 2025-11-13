from django.urls import path
from .views import *

urlpatterns = [
    path("products/", ProductListAPIView.as_view()),
    path("products/<slug:slug>/", ProductDetailAPIView.as_view()),
    path("stores/", StoreListView.as_view()),
    path("brands/", BrandListView.as_view()),
    path("categories/", CategoryListView.as_view()),
    path("categories/<slug:slug>/sizes/", CategorySizesView.as_view()),
]
