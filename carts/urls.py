from django.urls import path
from . import views

urlpatterns=[
    path('', views.cart, name='cart'),
    path('add_cart/<int:product_id>', views.add_cart, name="add_cart"),
    path('minus/<int:cart_item_id>', views.minus, name="minus"),
    path('remove/<int:cart_item_id>', views.remove, name="remove"),
    path('checkout/', views.checkout, name="checkout")
]