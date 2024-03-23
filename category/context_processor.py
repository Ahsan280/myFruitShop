from .models import Category
from store.models import Product
def menu_links(request):
    links=Category.objects.all()
    return dict(links=links)

def category_products(request):
    cat=Category.objects.all()
    product_in_cat={}
    for category in cat:
        products=Product.objects.filter(category=category)
        product_in_cat[category.category_name]=products.count()

    return dict(product_in_cat=product_in_cat)