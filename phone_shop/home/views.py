from django.shortcuts import render
from shop.models import Product

def home(request):
    products = Product.objects.all()
    return render(request, 'home/index.html', context={'products': products})