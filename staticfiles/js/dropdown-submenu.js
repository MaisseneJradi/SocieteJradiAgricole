document.addEventListener('DOMContentLoaded', function () {
  const toggles = document.querySelectorAll('.dropdown-submenu > .dropdown-toggle');

  toggles.forEach(function (toggle) {
    toggle.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();

      const submenu = this.nextElementSibling;

      // Fermer tous les autres sous-menus au même niveau
      const parentMenu = this.closest('.dropdown-menu');
      parentMenu.querySelectorAll('.dropdown-submenu .dropdown-menu.show').forEach(function (menu) {
        if (menu !== submenu) {
          menu.classList.remove('show');
        }
      });

      // Toggle le sous-menu actuel
      if (submenu) {
        submenu.classList.toggle('show');
      }
    });
  });

  // Fermer tout en cliquant en dehors
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.dropdown-menu')) {
      document.querySelectorAll('.dropdown-menu.show').forEach(function (menu) {
        menu.classList.remove('show');
      });
    }
  });
});
