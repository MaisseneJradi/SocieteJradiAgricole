# category/admin_views.py
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from .models import Category

@staff_member_required
def get_subcategories(request):
    """
    Vue AJAX pour récupérer les sous-catégories d'une catégorie donnée
    Utilisée dans l'admin pour le formulaire des produits
    """
    parent_id = request.GET.get('parent_id')
    
    if not parent_id:
        return JsonResponse({'subcategories': []})
    
    try:
        subcategories = Category.objects.filter(
            parent_id=parent_id,
            is_active=True
        ).values('id', 'category_name').order_by('category_name')
        
        # Formater les données pour le JavaScript
        subcategories_list = [
            {'id': cat['id'], 'name': cat['category_name']}
            for cat in subcategories
        ]
        
        return JsonResponse({'subcategories': subcategories_list})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ========================================
# Dans votre urls.py principal ou dans category/urls.py
# ========================================
"""
# urls.py
from django.urls import path
from category.admin_views import get_subcategories

urlpatterns = [
    # ... vos autres URLs ...
    path('admin/get-subcategories/', get_subcategories, name='admin_get_subcategories'),
]
"""