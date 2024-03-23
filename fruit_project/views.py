from django.http import HttpResponse
from django.shortcuts import render
from store.models import Product, ReviewRating
from category.models import Category

def index(request):
    products=Product.objects.filter(is_available=True)
    bestseller = Product.objects.filter(is_available=True).order_by("sold")
    reviews = ReviewRating.objects.filter(status=True)
    bestseller = bestseller[:5]
    product_count = products.count()
    return render(request, 'index.html', context={'products':products,
                                                  "bestseller":bestseller,
                                                  'count':product_count,
                                                  'reviews':reviews,})