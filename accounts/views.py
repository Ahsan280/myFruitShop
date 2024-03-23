from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from accounts.models import Account
from carts.models import Cart, CartItem
from carts.views import _cart_id
import requests

from orders.models import Order, OrderedProduct


# Create your views here.
def register(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = email.split('@')[0]
        phone_number = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password != confirm_password:
            messages.error(request, "Passwords don't match!")
            return redirect('register')

        if Account.objects.filter(email=email).exists():
            messages.error(request, "Email already exists. Please use a different email.")
            return redirect('register')

        user = Account.objects.create_user(first_name=first_name,
                                           last_name=last_name,
                                           username=username,
                                           password=password,
                                           email=email)
        user.phone_number = phone_number
        user.save()
        # User Activation
        current_site = get_current_site(request)
        mail_subject = "Please activate your account"
        message = render_to_string('accounts/account_verification_email.html', {
            'user': user,
            'domain': current_site,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user)
        })
        to_email = email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()

        return redirect("/accounts/login/?command=verification&email=," + email)
    else:
        return render(request, 'accounts/register.html', context={})

def activate(request, uidb64, token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active=True
        user.save()
        messages.success(request, 'Your account has been activated')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')

def login(request):
    if request.method=="POST":
        try:
            email=request.POST.get('email')
            password=request.POST.get('password')
            user=auth.authenticate(email=email, password=password)

            if user is not None:
                cart=Cart.objects.get(cart=_cart_id(request))
                cart_items=CartItem.objects.filter(cart=cart)
                user_items=CartItem.objects.filter(user=user)
                for cart_item in cart_items:
                    cart_item_var = []

                    for variation in cart_item.variation.all():
                        cart_item_var.append(variation.variation_value)
                        for item in user_items:
                            user_item_var=[]
                            for var in item.variation.all():
                                user_item_var.append(var.variation_value)
                            if set(cart_item_var)==set(user_item_var) and user_items.exists():
                                item.quantity+=cart_item.quantity
                                item.save()
                                cart_item.delete()
                                break
                            else:
                                cart_item.user = user
                                cart_item.cart = None
                                cart_item.save()
                        if not user_items.exists():
                            cart_item.user = user
                            cart_item.cart = None
                            cart_item.save()
                    if len(cart_item.variation.all())==0:
                        cart_item.user=user
                        cart_item.cart=None
                        cart_item.save()

                messages.success(request, "You have been logged in")
                auth.login(request, user)

                url = request.META.get('HTTP_REFERER')
                try:
                    query = requests.utils.urlparse(url).query
                    key_value_pairs=query.split('&')
                    params={}
                    for pair in key_value_pairs:
                        key, value = pair.split('=')
                        params[key]=value
                    if "next" in params:
                        nextPage=params['next']
                        return redirect(nextPage)
                except:
                    messages.success(request, "You have been logged in")
                    return redirect('index')
            else:
                messages.error(request, "Invalid credentials")
                return redirect('login')

        except Exception as e:
            raise e

    return render(request, 'accounts/login.html')

def forgot_password(request):
    if request.method=="POST":
        email=request.POST.get('email')
        if  Account.objects.filter(email=email, is_active=True).exists():
            user=Account.objects.get(email__exact=email, is_active=True)
            current_site = get_current_site(request)
            mail_subject = "Please reset your password"
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, "Password Reset link has been sent to your email")
            return redirect('login')
        else:
            messages.error(request, "Account does not exist")
            return redirect('forgotPassword')
    return render(request, "accounts/forgot_password.html")

def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']=uid
        return redirect("reset_password")
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('forgotPassword')

def reset_password(request):
    if request.method == "POST":
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password == confirm_password:
            try:
                uid = request.session.get('uid')
                print('uid-->',uid)
                user = Account.objects.get(pk=uid)
                user.set_password(password)
                user.save()
                messages.success(request, "Password has been reset successfully")
                return redirect('login')
            except Exception as e:
                print(e)
                return redirect('reset_password')
        else:
            messages.error(request, "Passwords donot match")
            return redirect('reset_password')
    else:
        return render(request, "accounts/reset_password.html")

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, "You have been logged out")
    return redirect('login')

def dashboard(request):
    user = request.user
    orders = Order.objects.filter(user=user, is_ordered=True)
    orders_count = orders.count()
    return render(request, 'accounts/dashboard.html', context={'orders_count':orders_count})

def my_orders(request):
    user=request.user
    orders=Order.objects.filter(user=user, is_ordered=True)

    return render(request, 'accounts/my_orders.html', context={'orders':orders,})

def order_details(request, order_number):
    order=Order.objects.get(order_number=order_number)
    ordered_products=OrderedProduct.objects.filter(order=order)
    tax=order.tax
    grand_total=order.order_total+tax
    return render(request, 'accounts/order_details.html', context={'order':order,
                                                                    'ordered_products':ordered_products,
                                                                   'grand_total':grand_total})

def change_password(request):
    if request.method=='POST':
        user=Account.objects.get(username__exact=request.user.username)
        current_password=request.POST.get('current_password')
        new_password=request.POST.get('new_password')
        confirm_password=request.POST.get('confirm_password')
        if new_password==confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password has been changed successfully")
                return redirect('login')
            else:
                messages.error(request, "Your current password is not the same")
                return redirect('change_password')
        else:
            messages.error(request, "New Password and Confirm password donot match")
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')