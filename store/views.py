from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from .models import Product, ReviewRating, ProductGallery
from category.models import Category
from orders.models import OrderProduct
from carts.views import _cart_id
from carts.models import CartItem
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages
from django.utils import timezone
from django.db import models
from decimal import Decimal
from django.http import HttpResponseBadRequest
# store/views.py

def store(request, category_slug=None, subcategory_slug=None):
    products = None
    current_category = None
    product_count = 0

    if subcategory_slug:
        # Ex: /store/category/engrais/foliaire/
        parent_category = get_object_or_404(Category, slug=category_slug)
        current_category = get_object_or_404(Category, slug=subcategory_slug, parent=parent_category)
    
    elif category_slug:
        current_category = get_object_or_404(Category, slug=category_slug, is_active=True)
        all_categories = [current_category] + list(current_category.get_descendants())
        products = Product.objects.filter(category__in=all_categories, is_available=True).order_by('-created_date')
    if current_category:
        # LA LIGNE MAGIQUE : Récupère TOUS les produits de la catégorie + TOUTES ses sous-catégories
        all_categories = [current_category] + list(current_category.get_descendants())
        products = Product.objects.filter(
            category__in=all_categories,
            is_available=True
        ).order_by('-created_date')
    else:
        # Page générale : tous les produits
        products = Product.objects.filter(is_available=True).order_by('-created_date')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if min_price:
        try:
            min_price = Decimal(min_price)
            products = products.filter(price__gte=min_price)
        except (ValueError, TypeError):
            pass
    
    if max_price:
        try:
            max_price = Decimal(max_price)
            # Si max_price est 2000+, on ne filtre pas le maximum
            if max_price < 2000:
                products = products.filter(price__lte=max_price)
        except (ValueError, TypeError):
            pass
    
    # Tri final
    products = products.order_by('-created_date')
    
    # Pagination
    paginator = Paginator(products, 20)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count,
        'category': current_category,  # Pour le fil d'ariane et le titre
        'min_price': min_price or '',
        'max_price': max_price or '',
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, subcategory_slug, product_slug):
    """Affiche les détails d'un produit AVEC sous-catégorie"""
    
    # Récupérer la catégorie principale
    category = get_object_or_404(Category, slug=category_slug)

    if subcategory_slug:
        subcategory = get_object_or_404(Category, slug=subcategory_slug, parent=category)
        single_product = get_object_or_404(Product, slug=product_slug, category=subcategory, is_available=True)
    else:
        single_product = get_object_or_404(Product, slug=product_slug, category=category, is_available=True)
        subcategory = None
    
    # Vérifier si le produit est dans le panier
    in_cart = CartItem.objects.filter(
        cart__cart_id=_cart_id(request),
        product=single_product
    ).exists()
    
    # Vérifier si l'utilisateur a déjà acheté ce produit
    orderproduct = None
    if request.user.is_authenticated:
        orderproduct = OrderProduct.objects.filter(
            user=request.user,
            product_id=single_product.id
        ).exists()
    
    # Récupérer les avis et la galerie
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
    
    # Récupérer les variations actives
    active_variations = None
    if hasattr(single_product, 'variation_set'):
        variation_method = getattr(single_product.variation_set, 'conditionnement', None)
        if callable(variation_method):
            active_variations = variation_method()
    
    context = {
        'single_product': single_product,
        'category': category,
        'subcategory': subcategory,
        'active_variations': active_variations,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery': product_gallery,
    }
    
    return render(request, 'store/product_detail.html', context)

# store/views.py

def category_item(request, category_slug, second_slug):
    """
    Gère :
    - /category/engrais/foliaire/           → Liste de produits (inclut sous-sous-catégories)
    - /category/engrais/urée-46/            → Détail d’un produit
    """
    # 1. Récupère la catégorie parent (ex: engrais)
    parent_category = get_object_or_404(Category, slug=category_slug, is_active=True)

    # 2. Vérifie si second_slug est une SOUS-CATÉGORIE
    subcategory = Category.objects.filter(parent=parent_category, slug=second_slug, is_active=True).first()

    if subcategory:
        # C'EST UNE SOUS-CATÉGORIE → Affiche TOUS les produits (y compris sous-sous-catégories)
        all_categories = [subcategory] + list(subcategory.get_descendants())
        products = Product.objects.filter(
            category__in=all_categories,
            is_available=True
        ).order_by('-created_date')

        paginator = Paginator(products, 20)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)

        context = {
            'products': paged_products,
            'product_count': products.count(),
            'category': subcategory,  # Pour le fil d'ariane et le titre
        }
        return render(request, 'store/store.html', context)

    else:
        # CE N’EST PAS UNE SOUS-CATÉGORIE → C’est forcément un PRODUIT
        single_product = get_object_or_404(
            Product,
            slug=second_slug,
            category=parent_category,
            is_available=True
        )

        # === Détail du produit ===
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()

        orderproduct = None
        if request.user.is_authenticated:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()

        reviews = ReviewRating.objects.filter(product_id=single_product, status=True)
        product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

        # Variations (si tu en as)
        active_variations = None
        if hasattr(single_product, 'variation_set'):
            try:
                active_variations = single_product.variation_set.conditionnement()
            except:
                pass

        context = {
            'single_product': single_product,
            'category': parent_category,
            'subcategory': None,
            'in_cart': in_cart,
            'orderproduct': orderproduct,
            'reviews': reviews,
            'product_gallery': product_gallery,
            'active_variations': active_variations,
        }
        return render(request, 'store/product_detail.html', context)
# Version ultra-simple et sûre (recommandée)
def promotions(request):
    products = Product.objects.promo_active().filter(is_available=True).order_by('-created_date')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if min_price:
        try:
            min_price = Decimal(min_price)
            products = products.filter(price__gte=min_price)
        except (ValueError, TypeError):
            pass
    
    if max_price:
        try:
            max_price = Decimal(max_price)
            if max_price < 2000:
                products = products.filter(price__lte=max_price)
        except (ValueError, TypeError):
            pass
    
    products = products.order_by('-created_date')
    paginator = Paginator(products, 20)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    context = {
        'products': paged_products,
        'product_count': products.count(),
        'links': Category.objects.filter(parent=None, is_active=True),
        'min_price': min_price or '',
        'max_price': max_price or '',
    }
    return render(request, 'store/promotions.html', context)

def product_detail_simple(request, category_slug, product_slug):
    """Affiche les détails d'un produit SANS sous-catégorie"""
    
    # Récupérer la catégorie
    category = get_object_or_404(Category, slug=category_slug)
    
    # D'abord, vérifier si product_slug est un produit
    try:
        single_product = Product.objects.get(
            slug=product_slug,
            category=category,
            is_available=True
        )
    except Product.DoesNotExist:
        # Si ce n'est pas un produit, vérifier si c'est une sous-catégorie
        try:
            subcategory = Category.objects.get(slug=product_slug, parent=category)
            # C'est une sous-catégorie, rediriger vers la liste de produits
            return redirect('products_by_subcategory', 
                          category_slug=category_slug, 
                          subcategory_slug=product_slug)
        except Category.DoesNotExist:
            # Ni produit ni sous-catégorie
            raise Http404("Produit ou sous-catégorie introuvable")
    
    # Si on arrive ici, c'est bien un produit
    in_cart = CartItem.objects.filter(
        cart__cart_id=_cart_id(request),
        product=single_product
    ).exists()
    
    orderproduct = None
    if request.user.is_authenticated:
        orderproduct = OrderProduct.objects.filter(
            user=request.user,
            product_id=single_product.id
        ).exists()
    
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
    
    active_variations = None
    if hasattr(single_product, 'variation_set'):
        variation_method = getattr(single_product.variation_set, 'conditionnement', None)
        if callable(variation_method):
            active_variations = variation_method()
    
    context = {
        'single_product': single_product,
        'category': category,
        'subcategory': None,
        'active_variations': active_variations,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery': product_gallery,
    }
    
    return render(request, 'store/product_detail.html', context)
def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword'].strip()
        if not keyword:
            return redirect(request.META.get('HTTP_REFERER', '/'))

        products = Product.objects.order_by('-created_date').filter(
            Q(description__icontains=keyword) |
            Q(product_name__icontains=keyword) |
            Q(category__category_name__icontains=keyword),
            is_available=True
        )
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        
        if min_price:
            try:
                min_price = Decimal(min_price)
                products = products.filter(price__gte=min_price)
            except (ValueError, TypeError):
                pass
        
        if max_price:
            try:
                max_price = Decimal(max_price)
                if max_price < 2000:
                    products = products.filter(price__lte=max_price)
            except (ValueError, TypeError):
                pass
        product_count = products.count()
    else:
        return redirect(request.META.get('HTTP_REFERER', '/'))

    context = {'products': products,
               'product_count': product_count, 
               'keyword': keyword,
               'min_price': min_price or '',
               'max_price': max_price or '',}
    return render(request, 'store/store.html', context)

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER', '/')

    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method")

    if not request.user.is_authenticated:
        messages.error(request, "Vous devez être connecté pour laisser un avis.")
        return redirect(url)

    try:
        reviews = ReviewRating.objects.get(
            user__id=request.user.id,
            product__id=product_id
        )
        form = ReviewForm(request.POST, instance=reviews)
        if form.is_valid():
            form.save()
            messages.success(request, 'Merci, votre avis a été mis à jour.')
            return redirect(url)
        else:
            messages.error(request, "Formulaire invalide.")
            return redirect(url)

    except ReviewRating.DoesNotExist:
        form = ReviewForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.ip = request.META.get('REMOTE_ADDR')
            data.product_id = product_id
            data.user_id = request.user.id
            data.save()
            messages.success(request, 'Merci, votre avis a bien été soumis.')
            return redirect(url)
        else:
            messages.error(request, "Formulaire invalide.")
            return redirect(url)


