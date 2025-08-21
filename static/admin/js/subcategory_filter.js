// Fichier à placer dans static/admin/js/subcategory_filter.js
(function($) {
    $(document).ready(function() {
        var categoryField = $('#id_category');
        var subcategoryField = $('#id_subcategory');
        var originalSubcategoryValue = subcategoryField.val(); // Conserver la valeur originale
        
        // Fonction pour filtrer les sous-catégories
        function filterSubcategories() {
            var categoryId = categoryField.val();
            
            if (categoryId) {
                // Faire une requête AJAX pour récupérer les sous-catégories
                $.ajax({
                    url: '/admin/get-subcategories/',
                    data: {
                        'category_id': categoryId
                    },
                    success: function(data) {
                        var currentValue = subcategoryField.val();
                        
                        subcategoryField.empty();
                        subcategoryField.append('<option value="">---------</option>');
                        
                        var hasCurrentValue = false;
                        $.each(data.subcategories, function(index, subcategory) {
                            var selected = '';
                            if (subcategory.id == currentValue || subcategory.id == originalSubcategoryValue) {
                                selected = 'selected';
                                hasCurrentValue = true;
                            }
                            
                            subcategoryField.append(
                                '<option value="' + subcategory.id + '" ' + selected + '>' + 
                                subcategory.name + '</option>'
                            );
                        });
                        
                        // Si la valeur actuelle n'est plus valide, réinitialiser
                        if (!hasCurrentValue) {
                            subcategoryField.val('');
                        }
                    },
                    error: function() {
                        console.log('Erreur lors du chargement des sous-catégories');
                        subcategoryField.empty();
                        subcategoryField.append('<option value="">---------</option>');
                    }
                });
            } else {
                subcategoryField.empty();
                subcategoryField.append('<option value="">---------</option>');
            }
        }
        
        // Déclencher le filtrage quand la catégorie change
        categoryField.change(function() {
            originalSubcategoryValue = null; // Reset après changement manuel
            filterSubcategories();
        });
        
        // Filtrer au chargement de la page si une catégorie est déjà sélectionnée
        if (categoryField.val()) {
            filterSubcategories();
        }
    });
})(django.jQuery);