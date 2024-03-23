from django.db import models
from store.models import Product, Variation
from accounts.models import Account

# Create your models here.
class Cart(models.Model):
    cart=models.CharField(max_length=200, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cart

class CartItem(models.Model):
    cart=models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    user=models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity=models.IntegerField()
    variation=models.ManyToManyField(Variation, blank=True)

    def get_CartItem_price(self):
        return self.quantity*self.product.product_price

    def __unicode__(self):
        return self.product