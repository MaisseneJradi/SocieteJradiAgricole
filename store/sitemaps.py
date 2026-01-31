from django.contrib.sitemaps import Sitemap
from .models import Product

class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    
    def items(self):
        return Product.objects.filter(is_available=True)
    
    def lastmod(self, obj):
        return obj.modified_date
    
    def location(self, obj):
        return obj.get_url()