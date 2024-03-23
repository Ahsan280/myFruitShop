from django.contrib import admin
from .models import Product, Variation
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'product_price', 'stock', 'category', 'updated_at']
    prepopulated_fields = {'slug':('product_name',)}

admin.site.register(Product, ProductAdmin)
admin.site.register(Variation)