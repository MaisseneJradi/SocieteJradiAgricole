from django.db import models
from django.urls import reverse
from django.core.cache import cache
from django.db.models import Q
class Category(models.Model):
    """
    Modèle de catégorie hiérarchique.
    Peut représenter une catégorie, sous-catégorie ou sous-sous-catégorie.
    """
    category_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True)
    
    # Relation auto-référentielle pour la hiérarchie
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    
    is_active = models.BooleanField(default=True)
    
    # Champs pour faciliter les requêtes hiérarchiques
    level = models.IntegerField(default=0, editable=False)  # 0=catégorie, 1=sous-catégorie, 2=sous-sous-catégorie, etc.
    
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        unique_together = ('parent', 'category_name')  # Évite les doublons au même niveau
        ordering = ['level', 'category_name']
    
    def save(self, *args, **kwargs):
        """Calcule automatiquement le niveau de la catégorie"""
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 0
        super().save(*args, **kwargs)
        #Invalider le cache de tous les ancêtres + soi-même après sauvegarde
        cache.delete(f"category_total_products_{self.id}")
        current = self.parent
        while current:
            cache.delete(f"category_total_products_{current.id}")
            current = current.parent
    # ===================================================================
    # MÉTHODE MAGIQUE : Comptage TOTAL des produits (récursif + cache)
    # ===================================================================
    def _get_total_products_count(self):
        """
        Retourne le nombre total de produits dans cette catégorie
        ET dans toutes ses sous-catégories (peu importe la profondeur)
        Avec cache automatique (1 heure)
        """
        cache_key = f"category_total_products_{self.id}"
        total = cache.get(cache_key)

        if total is not None:
            return total

        # Compte les produits directs
        total = self.products.filter(is_available=True).count()

        # Ajoute récursivement les produits des enfants
        for child in self.children.filter(is_active=True):
            total += child._get_total_products_count()

        cache.set(cache_key, total, timeout=3600)  # 1 heure de cache
        return total

    # Propriété accessible dans les templates : {{ category.total_products }}
    total_products = property(_get_total_products_count)
    

    # category/models.py → Replace the old get_url() with this one
    def get_url(self):
        """
        Returns the correct URL for ANY category level using our new clean URL pattern:
        - Level 0 (main):           /store/category/bio-stimulants/
        - Level 1 (subcategory):    /store/category/bio-stimulants/engrais-foliaires/
        - Level 2+ (deep):          /store/category/bio-stimulants/engrais-foliaires/niveau3/
        """
        if self.parent is None:
            # Main category → 1 slug
            return reverse('products_by_category', kwargs={'category_slug': self.slug})
        else:
            # Subcategory (level 1 or deeper) → always 2 slugs: parent + self
            # This works for level 1, 2, 3, 4... because we only use the direct parent
            return reverse('category_item', kwargs={
                'category_slug': self.parent.slug,
                'second_slug': self.slug
            })
        
    def get_ancestors(self):
        """Retourne tous les ancêtres (parents, grands-parents, etc.)"""
        ancestors = []
        current = self.parent
        while current:
            ancestors.insert(0, current)
            current = current.parent
        return ancestors
    
    def get_descendants(self):
        """Retourne tous les descendants (enfants, petits-enfants, etc.)"""
        descendants = []
        for child in self.children.all():
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants
    
    def get_root(self):
        """Retourne la catégorie racine (niveau 0)"""
        if self.level == 0:
            return self
        return self.get_ancestors()[0] if self.get_ancestors() else self
    
    def is_root(self):
        """Vérifie si c'est une catégorie racine"""
        return self.parent is None
    
    def is_leaf(self):
        """Vérifie si c'est une catégorie feuille (sans enfants)"""
        return not self.children.exists()
    
    def get_breadcrumb(self):
        """Retourne le fil d'Ariane complet"""
        breadcrumb = self.get_ancestors()
        breadcrumb.append(self)
        return breadcrumb
    
    def __str__(self):
        """Affiche le chemin complet de la catégorie"""
        if self.parent:
            return f"{self.parent} > {self.category_name}"
        return self.category_name
    
    def __repr__(self):
        return f"<Category: {self.category_name} (Level {self.level})>"