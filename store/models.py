from django.db import models
from django.db.models import Count, Avg

from accounts.models import Account
from category.models import Category
# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=150, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=150, unique=True)
    description = models.TextField(max_length=300, blank=True)
    product_price = models.FloatField()
    stock = models.IntegerField(default=100)
    sold = models.IntegerField(default=0)
    image = models.ImageField(upload_to='photos/products')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name

    def averageReview(self):
        reviews=ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg=0
        if reviews['average'] is not None:
            avg=float(reviews['average'])
        return avg
    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count=0
        if reviews['count'] is not None:
            count=int(reviews['count'])

        return count

class ReviewRating(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    user=models.ForeignKey(Account, on_delete=models.CASCADE)
    subject=models.CharField(max_length=100, blank=True)
    review=models.TextField(max_length=500, blank=True)
    rating=models.FloatField()
    ip=models.CharField(max_length=20, blank=True)
    status=models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
class Variation(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category=models.CharField(max_length=200)
    variation_value=models.CharField(max_length=200)

    def __str__(self):
        return self.variation_value