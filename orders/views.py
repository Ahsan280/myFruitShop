import datetime
import json

from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from carts.models import CartItem
from orders.models import Order, Payment, OrderedProduct
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid
from django.urls import reverse

# Create your views here.
@csrf_exempt
def payments(request, order_number, transaction_ID):
    order=Order.objects.get(user=request.user, is_ordered=False, order_number=order_number)
    payment=Payment(
        user=request.user,
        payment_id=transaction_ID,
        method='Paypal',
        amount=order.order_total,
        status="Completed"
    )
    payment.save()
    order.payment=payment
    order.is_ordered=True
    order.save()

    cart_items=CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderedproduct=OrderedProduct()
        orderedproduct.user=request.user
        orderedproduct.order=order
        orderedproduct.payment=payment
        orderedproduct.product=item.product
        orderedproduct.quantity=item.quantity
        orderedproduct.price=item.product.product_price
        orderedproduct.ordered=True
        orderedproduct.save()
        variation=item.variation.all()
        orderedproduct.variation.set(variation)
        orderedproduct.save()

    # clear the cart
    CartItem.objects.filter(user=request.user).delete()
    # send order received email to customer

    # Send order number and transaction id back to SendData method via JsonResponse
    mail_subject = "Thank you for your order!"
    message = render_to_string('orders/order_receive_email.html', {
        'user': request.user,
        'order': order

    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()
    kwargs={'order_number':order_number, "transaction_id":transaction_ID}
    return redirect('order_complete', **kwargs)

def order_complete(request, order_number, transaction_id):
    order=Order.objects.get(order_number=order_number, is_ordered=True)
    ordered_products=OrderedProduct.objects.filter(order=order)
    subtotal=0
    for i in ordered_products:
        subtotal+=i.price*i.quantity
    grand_total=subtotal+order.tax
    payment=Payment.objects.get(payment_id=transaction_id)
    return render(request, "orders/order_complete.html", context={'order': order,
                                                                  'ordered_products': ordered_products,
                                                                  'order_number':order.order_number,
                                                                  'transID':payment.payment_id,
                                                                  'payment':payment,
                                                                  'subtotal':subtotal,
                                                                  'grand_total':grand_total
                                                                  })

def place_order(request):
    if request.method == "POST":
        cart_items=CartItem.objects.filter(user=request.user)
        total=0
        for cart_item in cart_items:
            total+=cart_item.product.product_price*cart_item.quantity
        tax_perc=0.1
        tax=total*tax_perc
        grand_total=total+tax

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address_line_1 = request.POST.get('address_line_1')
        address_line_2 = request.POST.get('address_line_2')
        country = request.POST.get('country')
        city = request.POST.get('city')
        state = request.POST.get('state')
        order_note = request.POST.get('order_note')
        order=Order(user=request.user, first_name=first_name, last_name=last_name,
                    phone=phone, email=email, address_line_1=address_line_1, address_line_2=address_line_2,
                    country=country,
                    city=city, state=state, order_note=order_note, ip=request.META.get('REMOTE_ADDR'), order_total=total, tax=tax)
        order.save()


        # generate order number
        yr = int(datetime.datetime.today().strftime('%Y'))
        dt = int(datetime.datetime.today().strftime('%d'))
        mt = int(datetime.datetime.today().strftime('%m'))

        d = datetime.datetime(yr, mt, dt)
        current_date = d.strftime("%Y%m%d")
        order_number = current_date + str(order.id)
        order.order_number=order_number
        order.save()
        host = request.get_host()
        paypal_checkout={
            "business":settings.PAYPAL_RECEIVER_EMAIL,
            "amount":grand_total,
            "item_name":order_number,
            "invoice":uuid.uuid4(),
            "curreny_code": "USD",
            "notify_url": f"https://{host}{reverse('paypal-ipn')}",
            "return_url": f"http://{host}{reverse('payments', kwargs={'order_number':order_number, 'transaction_ID':uuid.uuid4()})}",
            "cancel_url": f"http://{host}{reverse('payment_failed')}",
        }
        paypal_paypemnt=PayPalPaymentsForm(initial=paypal_checkout)
        my_order=Order.objects.get(user=request.user, order_number=order_number, is_ordered=False)

        return render(request, 'orders/payments.html', context={'order':order,
                                                                'total':total,
                                                                'grand_total':grand_total,
                                                                'cart_items':cart_items,
                                                                'paypal':paypal_paypemnt})
    else:

        return redirect('checkout')


def payment_failed(request):
    return redirect("index")