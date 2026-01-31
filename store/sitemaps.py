from django.contrib.sitemaps import Sitemap
from .models import Product
from category.models import Category


class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    
    def items(self):
        return Product.objects.filter(is_available=True)
    
    def lastmod(self, obj):
        return obj.modified_date
    
    def location(self, obj):
        return obj.get_url()


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7
    
    def items(self):
        return Category.objects.filter(is_active=True)
    
    def location(self, obj):
        if obj.parent:
            return f'/store/category/{obj.parent.slug}/{obj.slug}/'
        return f'/store/category/{obj.slug}/'


class PromotionsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8
    
    def items(self):
        return ['promotions']
    
    def location(self, item):
        return '/store/promotions/'