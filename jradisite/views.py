# views.py (remplace ta fonction home par celle-ci)

from django.shortcuts import render
from store.models import Product
from category.models import Category
from django.utils import timezone
from partners.models import Partner , HomeCarousel   # ← Ajoute cette ligne

def home(request):
    # 1. Catégories principales (niveau 0 uniquement)
    main_categories = Category.objects.filter(
        parent__isnull=True,    # équivalent à parent=None mais plus rapide en DB
        is_active=True
    ).prefetch_related('products')  # accélère le .count() dans le template

    # 2. Produits en promotion ACTIFS (avec gestion correcte des dates)
    promo_products = Product.objects.filter(
        is_available=True,
        is_promo=True,
        promo_price__isnull=False,
        promo_start_date__lte=timezone.now(),
        # si promo_end_date est vide → toujours valide, sinon → pas expirée
    ).exclude(
        promo_end_date__lt=timezone.now()
    ).order_by('-modified_date')[:12]  # 12 max sur la page d'accueil
    carousel_images = HomeCarousel.objects.filter(is_active=True).order_by('order')
    # Alternative encore plus propre (recommandée) : utiliser la méthode du modèle
    # promo_products = [p for p in Product.objects.filter(is_promo=True, is_available=True)[:20] if p.is_promo_active()][:12]
    partners = Partner.objects.filter(is_active=True).order_by('order', 'name')
    context = {
        'main_categories': main_categories,   # ← utilisé dans le template
        'promo_products': promo_products, 
        'carousel_images': carousel_images,   # ← nouveau
        'partners': partners,   # ← N’oublie pas    # ← utilisé dans le template
    }

    return render(request, 'home.html', context)