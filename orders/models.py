from django.db import models
from accounts.models import Account
from store.models import Product , Variation

# Create your models here.
class Payment(models.Model):
    user = models.ForeignKey(Account , on_delete=models.CASCADE)
    Payment_id = models.CharField(max_length=100)
    Payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.Payment_id
    
class Order(models.Model):
    STATUS = (
        ('New' , 'New' ),
        ('Accepted' , 'Accepted'),
        ('Completed' , 'completed'),
        ('Cancelled' , 'Cancelled'),
    )

    user             = models.ForeignKey(Account , on_delete=models.SET_NULL , null=True)
    Payment          = models.ForeignKey(Payment , on_delete=models.SET_NULL , blank=True , null=True)
    order_number     = models.CharField(max_length=20)
    first_name       = models.CharField(max_length=50)
    last_name        = models.CharField(max_length=50)
    phone            = models.CharField(max_length=15)
    email            = models.EmailField(max_length=50)
    address_line_1   = models.CharField(max_length=50)
    address_line_2   = models.CharField(max_length=50 , blank=True)
    city             = models.CharField(max_length=50)
    region           = models.CharField(max_length=50)
    order_note       = models.CharField(max_length=100, blank=True)
    order_total      = models.FloatField()
    livraison        = models.FloatField()
    status           = models.CharField(max_length=10 , choices=STATUS , default='New')
    ip               = models.CharField(blank=True, max_length=20)
    is_ordered       = models.BooleanField(default=False)
    created_at       = models.DateField(auto_now_add=True)
    updated_at       = models.DateField(auto_now=True)
    
    def __str__(self):
        return self.first_name
    

class OrderProduct(models.Model):
    order = models.ForeignKey(Order , on_delete=models.CASCADE)
    payment  = models.ForeignKey(Payment , on_delete=models.SET_NULL , blank=True , null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product , on_delete=models.CASCADE)
    variation = models.ForeignKey(Variation , on_delete=models.CASCADE)
    conditionnement = models.CharField(max_length=50)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at       = models.DateField(auto_now_add=True)
    updated_at       = models.DateField(auto_now=True)
    


    def __str__(self):
        return self.product.product_name
    
