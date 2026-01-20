from django.contrib import admin
from .models import Product, Variation, ReviewRating, ProductGallery 
import admin_thumbnails
from django import forms
from django.forms import ModelForm
from django.db import models
from category.models import Category

# ===========================
# GALERIE INLINE
# ===========================
@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(image=models.F('product__images'))

# ===========================
# VARIATIONS INLINE
# ===========================
class VariationInline(admin.TabularInline):
    model = Variation
    readonly_fields = ('created_date',)
    extra = 1
    fields = (
        'variation_category', 'variation_value', 'variation_price',
        'variation_image', 'is_promo', 'promo_price','promo_start_date',
        'promo_end_date', 'is_active'
    )

# ===========================
# CHAMP PERSONNALISÉ POUR CATÉGORIES HIÉRARCHIQUES
# ===========================
class HierarchicalCategoryChoiceField(forms.ModelChoiceField):
    """Champ personnalisé qui affiche les catégories avec indentation"""
    
    def label_from_instance(self, obj):
        """Personnalise l'affichage de chaque option"""
        indent = '—' * obj.level
        return f"{indent} {obj.category_name}" if indent else obj.category_name

# ===========================
# PRODUCT ADMIN FORM
# ===========================
class ProductAdminForm(ModelForm):
    """Formulaire personnalisé pour l'admin des produits"""
    
    # Utiliser le champ personnalisé
    category = HierarchicalCategoryChoiceField(
        queryset=Category.objects.filter(is_active=True).select_related('parent').order_by('level', 'category_name'),
        required=True,
        label="Catégorie",
        help_text="Sélectionnez la catégorie la plus spécifique pour ce produit"
    )
    
    class Meta:
        model = Product
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configuration du champ category
        self.fields['category'].widget.attrs.update({
            'class': 'category-select',
            'style': 'width: 400px;'
        })

# ===========================
# PRODUCT ADMIN
# ===========================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = (
        'product_name', 'get_category_path', 'price', 'is_promo', 'promo_price',
        'stock', 'modified_date', 'is_available'
    )
    list_filter = ('category', 'is_available', 'is_promo')
    search_fields = ('product_name', 'category__category_name', 'description')
    list_editable = ('is_available',)
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [VariationInline, ProductGalleryInline]
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('product_name', 'slug', 'description')
        }),
        ('Catégorie', {
            'fields': ('category',),
            'description': 'Sélectionnez la catégorie la plus spécifique. Les catégories sont affichées avec indentation.'
        }),
        ('Prix et stock', {
            'fields': ('price', 'is_promo', 'promo_price', 'promo_start_date', 'promo_end_date', 'stock')
        }),
        ('Médias', {
            'fields': ('images',)
        }),
        ('Paramètres', {
            'fields': ('is_available',)
        }),
    )
    
    def get_category_path(self, obj):
        """Affiche le chemin complet de la catégorie"""
        if obj.category:
            breadcrumb = obj.category.get_breadcrumb()
            return ' > '.join([cat.category_name for cat in breadcrumb])
        return '-'
    get_category_path.short_description = 'Catégorie'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Optimiser les requêtes
        qs = qs.select_related('category', 'category__parent', 'category__parent__parent')
        for product in qs:
            product.check_promo_status()
        return qs

# ===========================
# VARIATION ADMIN
# ===========================
@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    autocomplete_fields = ['product']
    list_display = (
        'product', 'variation_category', 'variation_value',
        'variation_price', 'is_promo', 'promo_price', 'is_active'
    )
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'is_active', 'is_promo')
    search_fields = ('product__product_name', 'variation_value')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        for var in qs:
            var.check_promo_status()
        return qs
    

# ===========================
# REVIEW RATING ADMIN
# ===========================
class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'status', 'created_at')
    list_filter = ('status', 'rating')
    search_fields = ('product__product_name', 'user__email')
    list_editable = ('status',)

# ===========================
# REGISTRATIONS
# ===========================
admin.site.register(ReviewRating, ReviewRatingAdmin)
admin.site.register(ProductGallery)
