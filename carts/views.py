from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect

from carts.models import CartItem, Cart
from store.models import Product, Variation


# Create your views here.
def cart(request):
    try:
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user)
        else:
            cart=Cart.objects.get(cart=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart)
        total=0
        tax_percent=0.10
        grand_total=0
        for cart_item in cart_items:
            total+=cart_item.product.product_price*cart_item.quantity
        tax=tax_percent*total
        grand_total=tax+total
    except ObjectDoesNotExist:
        cart_items=None
        total=0
        tax=0
        grand_total=0

    return render(request, 'carts/cart.html', context={'cart_items':cart_items,
                                                       'total':total,
                                                       'tax':tax,
                                                       'grand_total':grand_total})

def add_cart(request, product_id):
    if request.method=='POST':
        quantity=int(request.POST.get('quantity'))
        if request.user.is_authenticated:
            var_exists = False

            product = Product.objects.get(id=product_id)
            variation = Variation.objects.filter(product=product)
            var_cat_list = []
            for var in variation:
                var_cat_list.append(var.variation_category)
            var_cat = set(var_cat_list)
            variation_dict = {}
            for var in var_cat:
                variation = request.POST.get(var)
                variation_dict[var] = variation
            cart_item_exists = CartItem.objects.filter(product=product, user=request.user).exists()
            if cart_item_exists:
                cart_items = CartItem.objects.filter(product=product, user=request.user)
                for cart_item in cart_items:
                    item_var_list = []
                    for variation in cart_item.variation.all():
                        item_var_list.append(variation.variation_value)

                    if set(item_var_list) == set(variation_dict.values()):
                        var_exists = True
                        cart_item.quantity += quantity
                        cart_item.save()
                if not var_exists:
                    new_cart_item = CartItem(user=request.user,
                                             product=product,
                                             quantity=quantity)
                    new_cart_item.save()
                    for category, value in variation_dict.items():
                        variation = Variation.objects.get(product=product, variation_category=category,
                                                          variation_value=value)
                        new_cart_item.variation.add(variation)
                        new_cart_item.save()

            else:
                cart_item = CartItem(user=request.user,
                                     product=product,
                                     quantity=quantity)
                cart_item.save()
                for category, value in variation_dict.items():
                    variation = Variation.objects.get(product=product, variation_category=category,
                                                      variation_value=value)
                    cart_item.variation.add(variation)
                    cart_item.save()
            return redirect('cart')
        else:
            var_exists=False
            try:
                cart=Cart.objects.get(cart=_cart_id(request))
            except Cart.DoesNotExist:
                cart=Cart(cart=_cart_id(request))
                cart.save()
            product=Product.objects.get(id=product_id)
            variation=Variation.objects.filter(product=product)
            var_cat_list=[]
            for var in variation:
                var_cat_list.append(var.variation_category)
            var_cat=set(var_cat_list)
            variation_dict={}
            for var in var_cat:
                variation=request.POST.get(var)
                variation_dict[var]=variation
            cart_item_exists=CartItem.objects.filter(product=product, cart=cart).exists()
            if cart_item_exists:
                cart_items=CartItem.objects.filter(product=product, cart=cart)
                for cart_item in cart_items:
                    item_var_list=[]
                    for variation in cart_item.variation.all():
                        item_var_list.append(variation.variation_value)

                    if set(item_var_list) == set(variation_dict.values()):
                        var_exists=True
                        cart_item.quantity+=quantity
                        cart_item.save()
                if not var_exists:
                    new_cart_item = CartItem(cart=cart,
                                             product=product,
                                             quantity=quantity)
                    new_cart_item.save()
                    for category, value in variation_dict.items():
                        variation = Variation.objects.get(product=product, variation_category=category,
                                                              variation_value=value)
                        new_cart_item.variation.add(variation)
                        new_cart_item.save()

            else:
                cart_item=CartItem(cart=cart,
                                   product=product,
                                   quantity=quantity)
                cart_item.save()
                for category, value in variation_dict.items():
                    variation=Variation.objects.get(product=product, variation_category=category, variation_value=value)
                    cart_item.variation.add(variation)
                    cart_item.save()
            return redirect('cart')

def minus(request, cart_item_id):
    if request.user.is_authenticated:
        cart_item=CartItem.objects.get(user=request.user, id=cart_item_id)
    else:
        cart_item=CartItem.objects.get(cart__cart=_cart_id(request), id=cart_item_id)
    cart_item.quantity-=1
    cart_item.save()
    if cart_item.quantity<=0:
        cart_item.delete()
    return redirect('cart')

def remove(request, cart_item_id):
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(user=request.user, id=cart_item_id)
    else:
        cart_item = CartItem.objects.get(cart__cart=_cart_id(request), id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

@login_required(login_url='login')
def checkout(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
    else:
        cart=Cart.objects.get(cart=_cart_id(request))
        cart_items=CartItem.objects.filter(cart=cart)
    total=0
    tax_perc=0.1
    for cart_item in cart_items:
        total+=cart_item.quantity*cart_item.product.product_price
    tax=total*tax_perc
    grand_total=total+tax

    return render(request, 'carts/checkout.html', context={'cart_items':cart_items,
                                                           'tax':tax,
                                                           'grand_total':grand_total})
@login_required(login_url='login')
def checkout(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
    else:
        cart = Cart.objects.get(cart=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart)
    total = 0
    tax_perc = 0.1
    for cart_item in cart_items:
        total += cart_item.quantity * cart_item.product.product_price
    tax = total * tax_perc
    grand_total = total + tax

    return render(request, 'carts/checkout.html', context={'cart_items': cart_items,
                                                           'tax': tax,
                                                           'subtotal':total,
                                                           'grand_total': grand_total})
def _cart_id(request):
    cart=request.session.session_key
    if not cart:
            cart=request.session.create()
    return cart