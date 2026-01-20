from django.contrib import admin
from .models import Category

# Inline pour afficher les sous-catégories dans l'admin des catégories
class SubCategoryInline(admin.TabularInline):
    model = Category
    fk_name = 'parent'  # Spécifie le champ de relation
    prepopulated_fields = {'slug': ('category_name',)}
    extra = 1
    fields = ('category_name', 'slug', 'is_active', 'cat_image')
    verbose_name = 'Sous-catégorie'
    verbose_name_plural = 'Sous-catégories'

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = (
        'get_indented_name',
        'slug',
        'level',
        'parent',
        'get_children_count',
        'is_active'
    )
    list_filter = ('level', 'is_active', 'parent')
    search_fields = ('category_name', 'slug', 'description')
    list_editable = ('is_active',)
    inlines = [SubCategoryInline]
    readonly_fields = ('level', 'get_breadcrumb_display', 'get_children_count')
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('category_name', 'slug', 'parent', 'description')
        }),
        ('Média', {
            'fields': ('cat_image',)
        }),
        ('Paramètres', {
            'fields': ('is_active',)
        }),
        ('Hiérarchie (lecture seule)', {
            'fields': ('level', 'get_breadcrumb_display', 'get_children_count'),
            'classes': ('collapse',)
        }),
    )
    
    def get_indented_name(self, obj):
        """Affiche le nom avec indentation selon le niveau"""
        indent = '—' * obj.level
        return f"{indent} {obj.category_name}" if indent else obj.category_name
    get_indented_name.short_description = 'Nom de la catégorie'
    
    def get_children_count(self, obj):
        """Compte le nombre d'enfants directs"""
        count = obj.children.count()
        return f"{count} enfant(s)"
    get_children_count.short_description = 'Sous-catégories'
    
    def get_breadcrumb_display(self, obj):
        """Affiche le fil d'Ariane complet"""
        breadcrumb = obj.get_breadcrumb()
        return ' > '.join([cat.category_name for cat in breadcrumb])
    get_breadcrumb_display.short_description = 'Chemin complet'
    
    def get_queryset(self, request):
        """Optimise les requêtes en préchargeant les relations"""
        qs = super().get_queryset(request)
        return qs.select_related('parent').prefetch_related('children')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Empêche une catégorie d'être son propre parent et évite les boucles"""
        if db_field.name == "parent":
            # Lors de la modification, exclut la catégorie elle-même et ses descendants
            if request.resolver_match.kwargs.get('object_id'):
                try:
                    category_id = request.resolver_match.kwargs['object_id']
                    category = Category.objects.get(pk=category_id)
                    # Exclut la catégorie et tous ses descendants
                    exclude_ids = [category.id] + [c.id for c in category.get_descendants()]
                    kwargs["queryset"] = Category.objects.exclude(id__in=exclude_ids)
                except Category.DoesNotExist:
                    pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    class Media:
        css = {
            'all': ('admin/css/custom_category_admin.css',)
        }

# Configuration alternative : vue en liste simple sans inline
class CategoryListAdmin(admin.ModelAdmin):
    """Alternative sans inline pour une vue plus simple"""
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = (
        'get_indented_name',
        'slug',
        'level',
        'parent',
        'get_children_count',
        'is_active'
    )
    list_filter = ('level', 'is_active')
    search_fields = ('category_name', 'slug')
    list_editable = ('is_active',)
    ordering = ('level', 'parent', 'category_name')
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('category_name', 'slug', 'parent', 'description')
        }),
        ('Média', {
            'fields': ('cat_image',)
        }),
        ('Paramètres', {
            'fields': ('is_active',)
        }),
    )
    
    def get_indented_name(self, obj):
        indent = '—' * obj.level
        return f"{indent} {obj.category_name}" if indent else obj.category_name
    get_indented_name.short_description = 'Nom de la catégorie'
    
    def get_children_count(self, obj):
        count = obj.children.count()
        return f"{count}"
    get_children_count.short_description = 'Enfants'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('parent').prefetch_related('children')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            if request.resolver_match.kwargs.get('object_id'):
                try:
                    category_id = request.resolver_match.kwargs['object_id']
                    category = Category.objects.get(pk=category_id)
                    exclude_ids = [category.id] + [c.id for c in category.get_descendants()]
                    kwargs["queryset"] = Category.objects.exclude(id__in=exclude_ids)
                except Category.DoesNotExist:
                    pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Enregistrement
# Utilisez CategoryAdmin (avec inline) ou CategoryListAdmin (sans inline)
admin.site.register(Category, CategoryAdmin)

# Si vous préférez la version sans inline, commentez la ligne au-dessus et décommentez celle-ci :
# admin.site.register(Category, CategoryListAdmin)