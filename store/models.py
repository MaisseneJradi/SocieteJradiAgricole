from django.db import models
from category.models import Category
from django.urls import reverse

# Create your models here.
class Product(models.Model):
    product_name     = models.CharField(max_length=200 , unique=True)
    slug             = models.SlugField(max_length=200 ,unique=True)
    description      = models.TextField(max_length=5000, blank=True)
    price            = models.FloatField()
    images           = models.ImageField(upload_to='photos/products' ,)
    stock            = models.IntegerField()
    is_available     = models.BooleanField(default=True)
    category         = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date     = models.DateTimeField(auto_now_add=True)
    modified_date    = models.DateTimeField(auto_now=True)

    def has_variations(self):
        """Vérifie si le produit a des variations actives"""
        return self.variation_set.filter(is_active=True).exists()
    
    def get_min_price(self):
        """Retourne le prix minimum du produit"""
        if self.has_variations():
            return self.variation_set.filter(is_active=True).aggregate(
                min_price=models.Min('variation_price')
            )['min_price']
        return self.price
    
    def get_max_price(self):
        """Retourne le prix maximum du produit"""
        if self.has_variations():
            return self.variation_set.filter(is_active=True).aggregate(
                max_price=models.Max('variation_price')
            )['max_price']
        return self.price




    def get_url(self):
        return reverse('product_detail', args=[self.category.slug , self.slug])

    def __str__(self):
        return self.product_name
variation_category_choice=(
    ('conditionnement' , 'conditionnement'),
)

class VariationManager(models.Manager):
    def conditionnement(self):
        return super(VariationManager , self).filter(variation_category='conditionnement' , is_active=True)
    

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100,choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    variation_price = models.FloatField(default=0.0)
    variation_image= models.ImageField(upload_to='photos/products' ,blank=True,null=True)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)
    objects = VariationManager()




    class Meta:
        unique_together = ('product', 'variation_category', 'variation_value')

    def __str__(self):
        return self.variation_value

