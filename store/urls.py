from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('search/', views.search, name='search'),
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
    
    # Détail produit avec sous-catégorie (3 slugs)
    path('category/<slug:category_slug>/<slug:subcategory_slug>/<slug:product_slug>/', 
         views.product_detail, 
         name='product_detail_with_subcategory'),
    
    # Combined: Sous-catégorie listing OU détail produit sans sous-catégorie (2 slugs)
    path('category/<slug:category_slug>/<slug:second_slug>/', 
         views.category_item, 
         name='category_item'),
    
    # Produits par catégorie principale (1 slug)
    path('category/<slug:category_slug>/', 
         views.store, 
         name='products_by_category'),


     path('promotions/', views.promotions, name='promotions'),    
]