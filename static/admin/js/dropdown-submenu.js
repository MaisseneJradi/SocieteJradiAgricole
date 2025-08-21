document.addEventListener('DOMContentLoaded', function() {
    const dropdownToggles = document.querySelectorAll('.dropdown-submenu .dropdown-toggle');

    dropdownToggles.forEach(function(toggle) {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const submenu = this.nextElementSibling;
            if (submenu) {
                submenu.classList.toggle('show');
            }
        });
    });

    // Fermer tous les sous-menus si on clique ailleurs
    document.addEventListener('click', function() {
        document.querySelectorAll('.dropdown-submenu .dropdown-menu.show').forEach(function(menu) {
            menu.classList.remove('show');
        });
    });
});
