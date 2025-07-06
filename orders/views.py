from django.shortcuts import render , redirect
from carts.models import CartItem
from .forms import OrderForm
from .models import Order
import datetime




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
            return redirect('checkout')
    else:
        return redirect('checkout')

   
