from django.shortcuts import render ,redirect , get_object_or_404
from store.models import Product , Variation
from .models import Cart,CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart    


def add_cart(request , product_id):
    current_user = request.user
    product = Product.objects.get(id = product_id) 
    #if the user is authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except:    
                    pass

        is_cart_item_exists = CartItem.objects.filter(product=product , user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product = product  ,user=current_user)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)   
            if product_variation in ex_var_list:
                #increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product , id = item_id)
                item.quantity +=1
                item.save()
            else:
                item= CartItem.objects.create(product=product , quantity=1 , user=current_user)
                #create e new cartitem
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user=current_user,
            )   
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        
        return redirect('cart')  
    #if the user is not authenticated 
    else :   
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                except:    
                    pass
        
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart=Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save() 

        is_cart_item_exists = CartItem.objects.filter(product=product , cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product = product  ,cart = cart)
            #existing variations ->database
            #current variation
            #item id 
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            print(ex_var_list)    
            if product_variation in ex_var_list:
                #increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product , id = item_id)
                item.quantity +=1
                item.save()
            else:
                item= CartItem.objects.create(product=product , quantity=1 , cart=cart)
                #create e new cartitem
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart=cart,
            )   
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        
        return redirect('cart')    
def remove_cart(request , product_id , cart_item_id):
    
    product = get_object_or_404(Product , id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product , user=request.user , id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_item = CartItem.objects.get(product=product , cart=cart , id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -=1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass        
    return redirect('cart')        


def remove_cart_item(request , product_id , cart_item_id):
    product = get_object_or_404(Product , id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product , user= request.user , id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_item = CartItem.objects.get(product=product , cart= cart , id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

from django.core.exceptions import ObjectDoesNotExist

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        grand_total = 0

        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            # 1️⃣ S'il y a une variation, on vérifie d'abord sa promo
            if cart_item.variations.exists():
                variation = cart_item.variations.first()

                if getattr(variation, 'is_promo', False) and getattr(variation, 'promo_price', None):
                    item_price = variation.promo_price
                else:
                    item_price = variation.variation_price

            # 2️⃣ Sinon, on prend les infos du produit
            else:
                if getattr(cart_item.product, 'is_promo', False) and getattr(cart_item.product, 'promo_price', None):
                    item_price = cart_item.product.promo_price
                else:
                    item_price = cart_item.product.price

            total += item_price * cart_item.quantity
            quantity += cart_item.quantity

        grand_total = total + 10  # frais de livraison ou autre

    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)



@login_required(login_url='login')
def checkout(request,total=0, quantity=0, cart_items=None):
    try:
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        
        for cart_item in cart_items:
            # Vérifie s'il y a des variations et prend leur prix si disponible
            if cart_item.variations.exists():
                # On suppose qu’un seul variation par cart_item (tu peux adapter sinon)
                variation = cart_item.variations.first()
                item_price = variation.variation_price
            else:
                item_price = cart_item.product.price

            total += item_price * cart_item.quantity
            quantity += cart_item.quantity

        grand_total = total + 10  # frais de livraison ou autre
        # --- Pré-remplir le formulaire avec infos utilisateur ---
        user = request.user
        initial_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }

        # Si tu as un profil étendu pour stocker téléphone, adresse, ville, région
        if hasattr(user, 'profile'):
            profile = user.profile
            initial_data.update({
                'phone': profile.phone,
                'address_line_1': profile.address_line_1,
                'address_line_2': profile.address_line_2,
                'city': profile.city,
                'region': profile.region,
            })

    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'grand_total': grand_total,
        'initial_data': initial_data,
    }
    return render(request , 'store/checkout.html', context)

