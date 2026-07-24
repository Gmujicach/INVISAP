(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['default'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '.layout-menu',
          popover: {
            title: 'Barra Lateral (Menu Principal)',
            description: 'Aqui encontrara todos los modulos del sistema. Haga clic en cualquier modulo para acceder a sus funciones.'
          },
          side: 'right'
        },
        {
          element: '.layout-navbar, .navbar, nav',
          popover: {
            title: 'Barra de Navegacion Superior',
            description: 'Contiene accesos rapidos, notificaciones y controles globales de la interfaz.'
          },
          side: 'bottom'
        },
        {
          element: '.corner-profile-container .profile-link-fixed',
          popover: {
            title: 'Acceso Rapido a Mi Perfil',
            description: 'Haga clic aqui para editar su informacion personal, cambiar contrasena, alternar tema y cerrar sesion.'
          },
          side: 'left'
        },
        {
          element: '.corner-profile-container .dropdown-menu',
          popover: {
            title: 'Menu de Usuario',
            description: 'Acceda a Editar Perfil, Configuracion, alternar Modo Oscuro/Claro y la opcion de Cerrar Sesion.'
          },
          side: 'left'
        },
        {
          element: '#btnTourInvilara, .tour-fab',
          popover: {
            title: 'Guia del Sistema (Tour)',
            description: 'Boton flotante de ayuda. En cualquier momento puede iniciar el recorrido guiado del modulo actual para aprender a navegar.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
