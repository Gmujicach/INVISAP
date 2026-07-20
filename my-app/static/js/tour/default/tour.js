(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['default'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '.layout-menu',
          popover: {
            title: 'Barra Lateral (Menú)',
            description: 'Desde aquí navega por todos los módulos del sistema: solicitudes, proyectos, obras, reportes y más.'
          },
          side: 'right'
        },
        {
          element: '.layout-navbar, .navbar, nav',
          popover: {
            title: 'Barra de Navegación',
            description: 'Contiene la búsqueda y accesos rápidos superiores de la interfaz.'
          },
          side: 'bottom'
        },
        {
          element: '.corner-profile-container .profile-link-fixed',
          popover: {
            title: 'Mi Perfil',
            description: 'Botón superior derecho para editar su perfil, cambiar tema y cerrar sesión.'
          },
          side: 'left'
        },
        {
          element: '.corner-profile-container .dropdown-menu',
          popover: {
            title: 'Menú de Usuario',
            description: 'Acceda a Editar Perfil, Configuración, modo claro/oscuro y Cerrar Sesión.'
          },
          side: 'left'
        },
        {
          element: '#btnTourInvilara, .tour-fab',
          popover: {
            title: 'Recorrido Guiado',
            description: 'En cualquier momento puede volver a iniciar este recorrido con el botón de ayuda.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
