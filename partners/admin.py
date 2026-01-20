# partners/admin.py
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Partner , HomeCarousel

@admin.register(HomeCarousel)
class HomeCarouselAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'is_active', 'order', 'created_at')
    list_editable = ('is_active', 'order')
    list_filter = ('is_active', 'created_at')
    list_per_page = 20

    fields = ('image', 'image_preview', 'is_active', 'order')
    readonly_fields = ('image_preview', 'created_at')

    def has_add_permission(self, request):
        return True
@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_preview', 'is_active', 'order', 'website')
    list_editable = ('is_active', 'order')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'website')
    prepopulated_fields = {'slug': ('name',)}  # remplissage auto du slug
    readonly_fields = ('logo_preview', 'created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'logo', 'logo_preview', 'website')
        }),
        ('Affichage', {
            'fields': ('is_active', 'order'),
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def logo_preview(self, obj):
        return obj.logo_preview()
    logo_preview.short_description = "Aperçu"