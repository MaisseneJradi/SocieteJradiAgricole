from django.db import models
from category.models import Category
from django.urls import reverse
from accounts.models import Account
from django.db.models import Avg, Count
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q
from decimal import Decimal

class ProductManager(models.Manager):
    def promo_active(self):
        now = timezone.now()
        return self.filter(
            (
                Q(
                    is_promo=True,
                    promo_price__isnull=False,
                    promo_price__gt=0,
                )
                &
                (Q(promo_start_date__lte=now) | Q(promo_start_date__isnull=True))
                &
                (Q(promo_end_date__gte=now) | Q(promo_end_date__isnull=True))
            )
            |
            (
                Q(
                    variation__is_promo=True,
                    variation__promo_price__isnull=False,
                    variation__promo_price__gt=0,
                    variation__is_active=True,
                )
                &
                (Q(variation__promo_start_date__lte=now) | Q(variation__promo_start_date__isnull=True))
                &
                (Q(variation__promo_end_date__gte=now) | Q(variation__promo_end_date__isnull=True))
            )
        ).distinct()

    

# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=5000, blank=True)
    price = models.FloatField()
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    objects = ProductManager()
    # Champs pour promotion
    is_promo = models.BooleanField(default=False, verbose_name="En promotion")
    promo_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Prix promotionnel"
    )    
    promo_start_date = models.DateTimeField(blank=True, null=True, verbose_name="Début de la promotion")
    promo_end_date = models.DateTimeField(blank=True, null=True, verbose_name="Fin de la promotion")
    
    
    
    def get_url(self):
        if self.category.parent:
            # Le produit est dans une sous-catégorie
            return reverse('product_detail_with_subcategory', kwargs={
                'category_slug': self.category.parent.slug,
                'subcategory_slug': self.category.slug,
                'product_slug': self.slug
            })
        else:
            # Le produit est directement dans une catégorie
            return reverse('category_item', kwargs={
                'category_slug': self.category.slug,
                'second_slug': self.slug  # Use 'second_slug' as the param name
            })
        
    def get_category_breadcrumb(self):
        """Retourne le fil d'Ariane de la catégorie"""
        if self.category:
            return self.category.get_breadcrumb()
        return []
    
    def get_main_category(self):
        """Retourne la catégorie principale (niveau 0)"""
        if self.category:
            return self.category.get_root()
        return None
        
    def has_variations(self):
        """Vérifie si le produit a des variations actives"""
        return self.variation_set.filter(is_active=True).exists()
    
    def __str__(self):
        return self.product_name

    def averageReview(self):
        """Calcule la moyenne des avis"""
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def countReview(self):
        """Compte le nombre d'avis"""
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count
    
    def has_promo_variation(self):
        return self.variation_set.filter(
            is_promo=True,
            is_active=True,
            promo_price__isnull=False
        ).exists()

    # ===== Gestion promotion =====
    def is_promo_active(self):
        """Vérifie si la promotion est active"""
        now = timezone.now()
        return (
            self.is_promo and
            self.promo_price is not None and
            (not self.promo_start_date or self.promo_start_date <= now) and
            (not self.promo_end_date or self.promo_end_date >= now)
        )

    def check_promo_status(self):
        """Désactive automatiquement les promotions expirées"""
        now = timezone.now()
        if self.is_promo and self.promo_end_date and self.promo_end_date < now:
            self.is_promo = False
            self.save()

    def get_final_price(self):
        """Retourne le prix final (promo ou normal)"""
        self.check_promo_status()
        return self.promo_price if self.is_promo_active() else self.price

    def clean(self):
        """Validation personnalisée"""
        super().clean()
        
        # Vérifier que le prix promo est inférieur au prix normal
        if self.is_promo and self.promo_price:
            if float(self.promo_price) >= self.price:
                raise ValidationError('Le prix promotionnel doit être inférieur au prix normal.')
        
        # Vérifier les dates de promotion
        if self.promo_start_date and self.promo_end_date:
            if self.promo_end_date <= self.promo_start_date:
                raise ValidationError('La date de fin doit être postérieure à la date de début.')

    def save(self, *args, **kwargs):
        """Sauvegarde avec validation"""
        self.full_clean()
        super().save(*args, **kwargs)
        
    class Meta:
        ordering = ['-created_date']
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'

# ===========================
# VARIATION
# ===========================
variation_category_choice = (
    ('conditionnement', 'conditionnement'),
)


class VariationManager(models.Manager):
    def conditionnement(self):
        return super(VariationManager, self).filter(variation_category='conditionnement', is_active=True)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    variation_price = models.FloatField(default=0.0)
    variation_image = models.ImageField(upload_to='photos/products', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)
    objects = VariationManager()

    # Champs pour promotion
    is_promo = models.BooleanField(default=False, verbose_name="En promotion")
    promo_price = models.FloatField(blank=True, null=True, verbose_name="Prix promotionnel")
    promo_start_date = models.DateTimeField(blank=True, null=True, verbose_name="Début de la promotion")
    promo_end_date = models.DateTimeField(blank=True, null=True, verbose_name="Fin de la promotion")

    class Meta:
        unique_together = ('product', 'variation_category', 'variation_value')
        verbose_name = 'Variation'
        verbose_name_plural = 'Variations'

    def __str__(self):
        return f"{self.product.product_name} - {self.variation_value}"

    # ===== Gestion promotion =====
    def is_promo_active(self):
        """Vérifie si la promotion est active"""
        now = timezone.now()
        return (
            self.is_promo and
            self.promo_price is not None and
            (not self.promo_start_date or self.promo_start_date <= now) and
            (not self.promo_end_date or self.promo_end_date >= now)
        )

    def check_promo_status(self):
        """Désactive automatiquement les promotions expirées"""
        now = timezone.now()
        if self.is_promo and self.promo_end_date and self.promo_end_date < now:
            self.is_promo = False
            self.save()

    def get_final_price_variation(self):
        """Retourne le prix final de la variation"""
        self.check_promo_status()
        return self.promo_price if self.is_promo_active() else self.variation_price


# ===========================
# REVIEW RATING
# ===========================
class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Avis'
        verbose_name_plural = 'Avis'
        ordering = ['-created_at']

    def __str__(self):
        return f"Avis de {self.user.email} sur {self.product.product_name}"


# ===========================
# PRODUCT GALLERY
# ===========================
class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='store/products', max_length=255)

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = 'Image de galerie'
        verbose_name_plural = 'Images de galerie'