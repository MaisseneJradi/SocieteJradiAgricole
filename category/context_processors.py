# category/context_processors.py
from .models import Category

def menu_links(request):
    """
    Context processor pour afficher les catégories dans tous les templates
    Optimisé pour charger uniquement les catégories racines avec leurs enfants
    """
    # Méthode 1: Charger seulement les catégories racines
    # Les enfants seront chargés récursivement dans les templates
    links = Category.objects.filter(
        parent=None,  # Seulement les catégories de niveau 0
        is_active=True
    ).prefetch_related(
        'children',  # Précharge les enfants directs
        'children__children',  # Précharge les petits-enfants
        'children__children__children'  # Précharge jusqu'à 3 niveaux
    ).order_by('category_name')
    
    return {'links': links}


# ALTERNATIVE: Si vous voulez charger toutes les catégories d'un coup
def menu_links_all(request):
    """
    Charge toutes les catégories actives, triées par niveau
    Utilisez cette méthode si vous préférez tout charger en une fois
    """
    all_categories = Category.objects.filter(
        is_active=True
    ).select_related('parent').prefetch_related('children').order_by('level', 'category_name')
    
    # Filtre uniquement les catégories racines pour l'affichage initial
    root_categories = [cat for cat in all_categories if cat.is_root()]
    
    return {
        'links': root_categories,
        'all_categories': all_categories
    }


# MÉTHODE OPTIMISÉE: Avec cache pour éviter les requêtes répétées
from django.core.cache import cache

def menu_links_cached(request):
    """
    Version avec cache pour améliorer les performances
    Le cache expire après 15 minutes
    """
    cache_key = 'category_menu_links'
    links = cache.get(cache_key)
    
    if links is None:
        links = list(Category.objects.filter(
            parent=None,
            is_active=True
        ).prefetch_related(
            'children',
            'children__children',
            'children__children__children'
        ).order_by('category_name'))
        
        # Met en cache pour 15 minutes
        cache.set(cache_key, links, 60 * 15)
    
    return {'links': links}


# MÉTHODE AVEC STRUCTURE ARBORESCENTE COMPLÈTE
def menu_links_tree(request):
    """
    Construit une structure arborescente complète
    Utile si vous voulez un contrôle total sur l'affichage
    """
    def build_tree(parent=None):
        categories = Category.objects.filter(
            parent=parent,
            is_active=True
        ).order_by('category_name')
        
        tree = []
        for category in categories:
            node = {
                'category': category,
                'children': build_tree(category)
            }
            tree.append(node)
        return tree
    
    category_tree = build_tree()
    
    return {'category_tree': category_tree}


# ============================================
# Dans settings.py, ajoutez le context processor:
# ============================================
"""
TEMPLATES = [
    {
        ...
        'OPTIONS': {
            'context_processors': [
                ...
                'category.context_processors.menu_links',  # Ajoutez cette ligne
            ],
        },
    },
]
"""

# ============================================
# Pour invalider le cache quand une catégorie change
# ============================================
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver([post_save, post_delete], sender=Category)
def invalidate_category_cache(sender, **kwargs):
    """Invalide le cache des catégories quand elles changent"""
    cache.delete('category_menu_links')


# ============================================
# Si vous utilisez les signals, ajoutez dans apps.py:
# ============================================
"""
# category/apps.py
from django.apps import AppConfig

class CategoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'category'

    def ready(self):
        import category.context_processors  # Importe les signals
"""