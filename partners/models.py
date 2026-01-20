# partners/models.py
from django.db import models
from django.utils.safestring import mark_safe

# ==================== CAROUSEL HOME ====================
class HomeCarousel(models.Model):
    image = models.ImageField(
        "Image du carousel",
        upload_to='home/carousel/',
        help_text="Recommandé : 1920x800px minimum, format JPG/PNG"
    )
    is_active = models.BooleanField("Afficher sur la page d'accueil", default=True)
    order = models.PositiveIntegerField("Ordre d'affichage", default=0, help_text="Plus petit = apparaît en premier")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Image du carousel"
        verbose_name_plural = "Carousel Accueil"
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Image {self.id} - {'Active' if self.is_active else 'Inactive'}"

    # Aperçu dans l'admin
    def image_preview(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" style="max-height: 100px; object-fit: cover; border-radius: 6px;">')
        return "(Aucune image)"
    image_preview.short_description = "Aperçu"
    
class Partner(models.Model):
    """
    Modèle pour gérer les partenaires affichés sur le site
    (Bayer, Syngenta, Yara, etc.)
    """
    name = models.CharField(
        "Nom du partenaire",
        max_length=100,
        help_text="Ex: Bayer, Syngenta, Yara..."
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        help_text="Laisser vide → sera généré automatiquement"
    )
    logo = models.ImageField(
        "Logo du partenaire",
        upload_to='partners/logos/',
        help_text="Format recommandé : PNG transparent ou JPG blanc – 300x150px max"
    )
    website = models.URLField(
        "Site web officiel",
        blank=True,
        null=True,
        help_text="Ex: https://www.bayer.com (avec https://)"
    )
    is_active = models.BooleanField(
        "Afficher sur le site",
        default=True
    )
    order = models.PositiveIntegerField(
        "Ordre d'affichage",
        default=0,
        help_text="Plus le nombre est petit → plus il apparaît en premier"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Partenaire"
        verbose_name_plural = "Partenaires"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Génère automatiquement le slug si vide
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1
            while Partner.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    # Pour afficher un aperçu du logo dans l'admin
    def logo_preview(self):
        if self.logo:
            return mark_safe(f'<img src="{self.logo.url}" style="max-height: 80px; object-fit: contain;">')
        return "(Aucun logo)"
    logo_preview.short_description = "Aperçu"
    logo_preview.allow_tags = True