from django.urls import path
from . import views

urlpatterns = [
    path('', views.shop_page, name='shop'),  # ← теперь это /shop/
    path('<slug:slug>/', views.product_detail, name='product_detail'),  # ← /shop/iphone13/
]
