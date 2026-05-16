from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('apps.user.urls')),
    path('api/catalog/', include('apps.product.urls')),
    path('api/favorites/', include('apps.favorite.urls')),
    path('api/cart/', include('apps.cart.urls')),
    path('api/order/', include('apps.order.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )