from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.shop, name='shop'),
    path('category/<slug:category_slug>', views.product_by_category, name="product_by_category"),
    path('search/', views.search, name='search'),
    path('<slug:category_slug>/<slug:product_slug>/', views.product_details, name='product_details'),
    path('submit_review/<int:product_id>', views.submit_review, name="submit_review"),
]