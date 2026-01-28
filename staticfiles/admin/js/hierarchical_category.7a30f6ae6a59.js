// static/admin/js/hierarchical_category.js
// Gestion des catégories hiérarchiques dans l'admin Django

(function($) {
    'use strict';
    
    $(document).ready(function() {
        // Éléments du DOM
        const $mainCategory = $('#id_main_category');
        const $subCategory = $('#id_sub_category');
        const $subSubCategory = $('#id_subsub_category');
        const $categoryDirect = $('#id_category');
        
        // Fonction pour charger les sous-catégories
        function updateSubCategories(parentId) {
            if (!parentId) {
                $subCategory.html('<option value="">---------</option>').prop('disabled', true);
                $subSubCategory.html('<option value="">---------</option>').prop('disabled', true);
                return;
            }
            
            // Afficher un loader
            $subCategory.html('<option value="">Chargement...</option>').prop('disabled', true);
            $subSubCategory.html('<option value="">---------</option>').prop('disabled', true);
            
            // Appel AJAX pour récupérer les sous-catégories
            $.ajax({
                url: '/admin/get-subcategories/',
                data: { parent_id: parentId },
                dataType: 'json',
                success: function(data) {
                    let options = '<option value="">---------</option>';
                    
                    if (data.subcategories && data.subcategories.length > 0) {
                        $.each(data.subcategories, function(i, cat) {
                            options += `<option value="${cat.id}">${cat.name}</option>`;
                        });
                        $subCategory.html(options).prop('disabled', false);
                    } else {
                        $subCategory.html('<option value="">Aucune sous-catégorie</option>').prop('disabled', true);
                    }
                },
                error: function() {
                    $subCategory.html('<option value="">Erreur de chargement</option>').prop('disabled', true);
                }
            });
        }
        
        // Fonction pour charger les sous-sous-catégories
        function updateSubSubCategories(parentId) {
            if (!parentId) {
                $subSubCategory.html('<option value="">---------</option>').prop('disabled', true);
                return;
            }
            
            $subSubCategory.html('<option value="">Chargement...</option>').prop('disabled', true);
            
            $.ajax({
                url: '/admin/get-subcategories/',
                data: { parent_id: parentId },
                dataType: 'json',
                success: function(data) {
                    let options = '<option value="">---------</option>';
                    
                    if (data.subcategories && data.subcategories.length > 0) {
                        $.each(data.subcategories, function(i, cat) {
                            options += `<option value="${cat.id}">${cat.name}</option>`;
                        });
                        $subSubCategory.html(options).prop('disabled', false);
                    } else {
                        $subSubCategory.html('<option value="">Aucune sous-sous-catégorie</option>').prop('disabled', true);
                    }
                },
                error: function() {
                    $subSubCategory.html('<option value="">Erreur de chargement</option>').prop('disabled', true);
                }
            });
        }
        
        // Exposer les fonctions globalement
        window.updateSubCategories = updateSubCategories;
        window.updateSubSubCategories = updateSubSubCategories;
        
        // Événements
        $mainCategory.on('change', function() {
            const mainId = $(this).val();
            updateSubCategories(mainId);
        });
        
        $subCategory.on('change', function() {
            const subId = $(this).val();
            updateSubSubCategories(subId);
        });
        
        // Synchroniser avec le champ direct
        $mainCategory.add($subCategory).add($subSubCategory).on('change', function() {
            const subsubId = $subSubCategory.val();
            const subId = $subCategory.val();
            const mainId = $mainCategory.val();
            
            if (subsubId) {
                $categoryDirect.val(subsubId);
            } else if (subId) {
                $categoryDirect.val(subId);
            } else if (mainId) {
                $categoryDirect.val(mainId);
            }
        });
    });
})(django.jQuery);