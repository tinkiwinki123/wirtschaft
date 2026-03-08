from django.shortcuts import render, get_object_or_404
from .models import Product

def shop_page(request):
    products = Product.objects.all()
    return render(request, 'shop/shop.html', {'products': products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'shop/product_detail.html', {'product': product})
