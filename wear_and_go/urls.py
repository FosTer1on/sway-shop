from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('apps.user.urls')),
    path('api/catalog/', include('apps.product.urls')),
    path('api/favorites/', include('apps.favorite.urls')),
]
