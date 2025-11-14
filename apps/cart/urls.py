from django.urls import path
from .views import *

urlpatterns = [
    path("", CartView.as_view()),
    path("add/", CartAddView.as_view()),
    path("item/update/", CartUpdateQuantityView.as_view()),
    path("item/delete/<int:item_id>/", CartDeleteItemView.as_view()),
]
