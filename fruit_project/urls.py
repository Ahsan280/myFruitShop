
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from . import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('shop/', include("store.urls")),
    path('cart/', include("carts.urls")),
    path('accounts/', include("accounts.urls")),
    path('orders/', include("orders.urls")),
    path('', include('paypal.standard.ipn.urls')),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns+=static(settings.STATIC_URL, document_root=settings.MEDIA_ROOT)
