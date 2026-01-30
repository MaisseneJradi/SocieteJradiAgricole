"""
Sitemaps pour le référencement Google - Agrishop.tn
Placez ce fichier dans : store/sitemaps.py
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product
from category.models import Category


class ProductSitemap(Sitemap):
    """Sitemap pour tous les produits disponibles"""
    changefreq = "daily"
    priority = 0.9
    
    def items(self):
        # Retourne tous les produits disponibles
        return Product.objects.filter(is_available=True).select_related('category')
    
    def lastmod(self, obj):
        # Date de dernière modification
        return obj.modified_date
    
    def location(self, obj):
        # Utilise la méthode get_url() déjà définie dans votre modèle Product
        return obj.get_url()


class CategorySitemap(Sitemap):
    """Sitemap pour toutes les catégories et sous-catégories"""
    changefreq = "weekly"
    priority = 0.7
    
    def items(self):
        # Retourne toutes les catégories actives
        return Category.objects.filter(is_active=True)
    
    def location(self, obj):
        # Pour les catégories principales (sans parent)
        if not obj.parent:
            return f'/store/category/{obj.slug}/'
        # Pour les sous-catégories
        else:
            return f'/store/category/{obj.parent.slug}/{obj.slug}/'


class PromotionsSitemap(Sitemap):
    """Sitemap pour la page des promotions"""
    changefreq = "daily"
    priority = 0.8
    
    def items(self):
        return ['promotions']
    
    def location(self, item):
        return '/store/promotions/'


class StaticViewSitemap(Sitemap):
    """Sitemap pour les pages statiques importantes"""
    changefreq = "monthly"
    priority = 0.8
    
    def items(self):
        # Liste des pages statiques (ajustez selon vos URLs)
        return ['home']  # Ajoutez d'autres pages si nécessaire : 'about', 'contact', etc.
    
    def location(self, item):
        return reverse(item) if item == 'home' else f'/{item}/'