from django.urls import path
from .views import *

urlpatterns = [
    path('create/', CreateOrderAPIView.as_view()),
    path("my-orders/", UserOrdersAPIView.as_view()),
    path("my-orders/<int:order_id>/", UserOrderDetailAPIView.as_view()),
]
