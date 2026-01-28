document.addEventListener('DOMContentLoaded', function() {
    const dropdownToggles = document.querySelectorAll('.dropdown-submenu .dropdown-toggle');

    dropdownToggles.forEach(function(toggle) {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            const submenu = this.nextElementSibling;

            // Fermer les autres sous-menus ouverts
            document.querySelectorAll('.dropdown-submenu .dropdown-menu.show').forEach(function(menu) {
                if (menu !== submenu) {
                    menu.classList.remove('show');
                    menu.previousElementSibling.setAttribute('aria-expanded', 'false');
                }
            });

            // Toggle le sous-menu cliqué
            if (submenu) {
                const isOpen = submenu.classList.contains('show');
                submenu.classList.toggle('show', !isOpen);
                this.setAttribute('aria-expanded', String(!isOpen));
            }
        });

        // Gestion via le clavier (Accessibilité)
        toggle.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });

    // Fermer tous les sous-menus si on clique ailleurs
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown-submenu')) {
            document.querySelectorAll('.dropdown-submenu .dropdown-menu.show').forEach(function(menu) {
                menu.classList.remove('show');
                menu.previousElementSibling.setAttribute('aria-expanded', 'false');
            });
        }
    });
});
