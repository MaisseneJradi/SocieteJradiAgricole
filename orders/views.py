from django.shortcuts import render , redirect
from carts.models import CartItem
from store.models import Product
from .forms import OrderForm
from .models import Order , Payment , OrderProduct
import datetime
import json 
from django.http import JsonResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
def payments(request):
    body = json.loads(request.body)
    try:
        order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Commande introuvable'}, status=404)

    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order = order
        orderproduct.payment = None
        orderproduct.user = request.user
        orderproduct.product = item.product
        orderproduct.quantity = item.quantity

        if item.variations.exists():
            variation = item.variations.first()
            orderproduct.product_price = variation.variation_price
        else:
            orderproduct.product_price = item.product.price

        orderproduct.ordered = True
        orderproduct.save()

        # ✅ Important : assigner les variations *après* le save()
        if item.variations.exists():
            orderproduct.variations.set(item.variations.all())
        # ✅ Réduire le stock du produit
        product = item.product
        product.stock -= item.quantity
        product.save()
    #clear cart
    CartItem.objects.filter(user=request.user).delete()
    #send order recieved email to customer 
    mail_subject = 'Merci pour votre commande ! '
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order':order,
        })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject , message , to=[to_email])
    send_email.send()
    #send order number back to the sendData method via jsonResponse
    data = {
        'order_number': order.order_number,

    }
    # ✅ Marquer la commande comme passée
    order.is_ordered = True
    order.save()

    # (Optionnel) Nettoyer le panier ici si tu veux

    print(f"✅ Commande {order.order_number} confirmée.")

    return JsonResponse(data)


def place_order(request, total = 0 , quantity = 0):
    current_user = request.user

    #if the cart count is less or equal to zeo then redirect back to shopping
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    grand_total = 0
    livraison = 10
    for cart_item in cart_items:
        if cart_item.variations.exists():
                # On suppose qu’un seul variation par cart_item (tu peux adapter sinon)
                variation = cart_item.variations.first()
                item_price = variation.variation_price
        else:
            item_price = cart_item.product.price
        total += item_price * cart_item.quantity
        quantity += cart_item.quantity
    grand_total = total + livraison  # frais de livraison ou autre

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            #store all the billig infos inside order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.city = form.cleaned_data['city']
            data.region = form.cleaned_data['region']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.livraison = livraison
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d  = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date +str(data.id)
            data.order_number = order_number
            data.save()


            order = Order.objects.get(user=current_user , is_ordered= False , order_number=order_number)
            context={
                 'order' : order,
                 'cart_items' : cart_items ,
                 'total' : total ,
                 'livraison' : livraison,
                 'grand_total' : grand_total,
            }
            return render(request , 'orders/payments.html' , context)
    else:
        return redirect('checkout')

   
def order_complete(request):
    order_number = request.GET.get('order_number')
    try:
        order = Order.objects.get(order_number=order_number , is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id= order.id)
        subtotal = 0
        
        for i in ordered_products:
            subtotal += i.product_price * i.quantity
        context={
            'order': order,
            'ordered_products':ordered_products,
            'order_number':order.order_number,
            'subtotal': subtotal,
            

        }
        return render(request , 'orders/order_complete.html' , context)
    except(Order.DoesNotExist):
        return redirect('home')