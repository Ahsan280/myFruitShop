from django.urls import path
from . import views

urlpatterns=[
    path('place_order/', views.place_order, name='place_order'),
    path('payments/<order_number>/<transaction_ID>/', views.payments, name='payments'),
    path('order_complete/<order_number>/<transaction_id>/', views.order_complete, name="order_complete"),
    path('payment_failed/', views.payment_failed, name="payment_failed"),
]