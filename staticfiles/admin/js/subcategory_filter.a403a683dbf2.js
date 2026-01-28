// static/admin/js/subcategory_filter.js
document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ DOM prêt, JS exécuté !");

    const categoryField = document.getElementById("id_category");
    const subCategoryField = document.getElementById("id_subcategory");

    if (!categoryField || !subCategoryField) {
        console.log("⚠️ Impossible de trouver les champs category/subcategory !");
        return;
    }

    // Sauvegarde toutes les sous-catégories existantes avec gestion d'erreur
    let allOptions = [];
    try {
        const optionElements = subCategoryField.querySelectorAll("option");
        if (optionElements && optionElements.length > 0) {
            allOptions = Array.from(optionElements).map(option => ({
                value: option.value,
                text: option.textContent,
                dataCategory: option.getAttribute("data-category")
            }));
            console.log("📋 Options sauvegardées:", allOptions.length);
        } else {
            console.log("⚠️ Aucune option trouvée dans le champ subcategory");
            // Charger les options via AJAX si elles ne sont pas présentes
            loadAllSubcategories();
        }
    } catch (error) {
        console.error("❌ Erreur lors de la sauvegarde des options:", error);
        return;
    }

    function filterSubcategories() {
        const selectedCategory = categoryField.value;
        console.log("📌 Catégorie sélectionnée :", selectedCategory);

        // Vérifier que allOptions n'est pas vide
        if (!allOptions || allOptions.length === 0) {
            console.log("⚠️ Aucune option disponible pour le filtrage");
            return;
        }

        // Vider les options actuelles
        subCategoryField.innerHTML = "";

        // Ajouter l'option vide par défaut
        const emptyOption = document.createElement("option");
        emptyOption.value = "";
        emptyOption.textContent = "---------";
        subCategoryField.appendChild(emptyOption);

        // Ajouter uniquement les sous-catégories correspondant à la catégorie choisie
        allOptions.forEach(optionData => {
            // Ignorer l'option vide d'origine
            if (optionData.value === "") return;

            const shouldShow = !selectedCategory || 
                              optionData.dataCategory === selectedCategory ||
                              optionData.dataCategory === null;

            if (shouldShow) {
                const option = document.createElement("option");
                option.value = optionData.value;
                option.textContent = optionData.text;
                option.setAttribute("data-category", optionData.dataCategory || "");
                subCategoryField.appendChild(option);
            }
        });

        console.log("✅ Filtrage terminé, options visibles:", subCategoryField.options.length);
    }

    // Fonction pour charger toutes les sous-catégories via AJAX si nécessaire
    function loadAllSubcategories() {
        console.log("🔄 Chargement des sous-catégories via AJAX...");
        
        fetch('/admin/load-all-subcategories/')
            .then(response => response.json())
            .then(data => {
                allOptions = data.subcategories.map(sub => ({
                    value: sub.id,
                    text: sub.name,
                    dataCategory: sub.category_id.toString()
                }));
                console.log("✅ Sous-catégories chargées via AJAX:", allOptions.length);
                
                // Remplir le champ avec toutes les options
                populateSubcategoryField();
                
                // Appliquer le filtre
                filterSubcategories();
            })
            .catch(error => {
                console.error("❌ Erreur lors du chargement AJAX:", error);
            });
    }

    // Fonction pour remplir le champ avec toutes les options
    function populateSubcategoryField() {
        subCategoryField.innerHTML = '<option value="">---------</option>';
        allOptions.forEach(optionData => {
            const option = document.createElement("option");
            option.value = optionData.value;
            option.textContent = optionData.text;
            option.setAttribute("data-category", optionData.dataCategory);
            subCategoryField.appendChild(option);
        });
    }

    // Filtrer dès le chargement (utile en édition d'un produit existant)
    if (allOptions.length > 0) {
        filterSubcategories();
    }

    // Réagir au changement de catégorie
    categoryField.addEventListener("change", filterSubcategories);
});