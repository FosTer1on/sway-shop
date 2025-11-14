from django.urls import path
from .views import *

urlpatterns = [
    path("", FavoriteListAPIView.as_view()),
    path("add/<slug:slug>/", AddFavoriteAPIView.as_view()),
    path("remove/<slug:slug>/", RemoveFavoriteAPIView.as_view()),
]