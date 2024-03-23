from .models import CartItem, Cart
from accounts.models import Account
from .views import _cart_id
def cart_counter(request):
    if request.user.is_authenticated:
        cart_items=CartItem.objects.filter(user=request.user)
    else:
        try:
            cart=Cart.objects.get(cart=_cart_id(request))
        except Cart.DoesNotExist:
            cart=Cart(cart=_cart_id(request))
            cart.save()
        cart_items=CartItem.objects.filter(cart=cart)

    cart_count=0
    for item in cart_items:
        cart_count+=item.quantity
    return dict(cart_count=cart_count)