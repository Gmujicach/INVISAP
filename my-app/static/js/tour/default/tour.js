(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['default'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '.layout-menu',
          popover: {
            title: 'Barra Lateral (Menú Principal)',
            description: 'Aquí encontrará todos los módulos del sistema. Haga clic en cualquier módulo para acceder a sus funciones.'
          },
          side: 'right'
        },
        {
          element: '.layout-navbar, .navbar, nav',
          popover: {
            title: 'Barra de Navegación Superior',
            description: 'Contiene accesos rápidos, notificaciones y controles globales de la interfaz.'
          },
          side: 'bottom'
        },
        {
          element: '.corner-profile-container .profile-link-fixed',
          popover: {
            title: 'Acceso Rápido a Mi Perfil',
            description: 'Haga clic aquí para editar su información personal, cambiar contraseña, alternar tema y cerrar sesión.'
          },
          side: 'left'
        },
        {
          element: '.corner-profile-container .dropdown-menu',
          popover: {
            title: 'Menú de Usuario',
            description: 'Acceda a Editar Perfil, Configuración, alternar Modo Oscuro/Claro y la opción de Cerrar Sesión.'
          },
          side: 'left'
        },
        {
          element: '#btnTourInvilara, .tour-fab',
          popover: {
            title: 'Guía del Sistema (Tour)',
            description: 'Botón flotante de ayuda. En cualquier momento puede iniciar el recorrido guiado del módulo actual para aprender a navegar.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
