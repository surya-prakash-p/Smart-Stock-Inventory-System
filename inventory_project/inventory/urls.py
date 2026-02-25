from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add-to-cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('confirm/', views.confirm_payment, name='confirm'),
    path('dashboard/', views.dashboard, name='dashboard'),
]