from django.db import models
from store.models import Product ,Variation
from accounts.models import Account
# Create your models here.
class Cart(models.Model):
    cart_id      = models.CharField(max_length=250 , blank=True)
    date_added   = models.DateField(auto_now_add=True)



    def __str__(self):
        return self.cart_id
    

class CartItem(models.Model):
    user        = models.ForeignKey(Account , on_delete=models.CASCADE , null=True)
    product     = models.ForeignKey(Product , on_delete=models.CASCADE)
    variations  = models.ManyToManyField(Variation , blank=True)
    cart        = models.ForeignKey(Cart , on_delete=models.CASCADE , null=True)
    quantity    = models.IntegerField()
    is_active   = models.BooleanField(default=True)
     
    @property
    def sub_total(self):
        if self.variations.exists():
            variation = self.variations.first()
            variation.check_promo_status()
            if getattr(variation, 'is_promo', False) and getattr(variation, 'promo_price', None):
                price = variation.promo_price
            else:
                price = variation.variation_price
        else:
            # Produit sans variation, on utilise le produit directement
            self.product.check_promo_status()
            if getattr(self.product, 'is_promo', False) and getattr(self.product, 'promo_price', None):
                price = self.product.promo_price
            else:
                price = self.product.price

        return price * self.quantity

    
    def __unicode__(self):
        return self.product