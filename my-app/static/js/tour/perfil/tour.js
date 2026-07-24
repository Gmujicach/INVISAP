(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['perfil'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '.perfil-header, .card-header-custom, h1, h2',
          popover: {
            title: 'Mi Perfil',
            description: 'Aquí puede ver y administrar toda su información personal registrada en el sistema.'
          },
          side: 'bottom'
        },
        {
          element: '.perfil-card, .card-body',
          popover: {
            title: 'Información Personal',
            description: 'Datos básicos: nombre completo, cédula de identidad, correo, teléfono y rol asignado.'
          },
          side: 'top'
        },
        {
          element: '.perfil-input, input[name="nombre"], input[name="email"]',
          popover: {
            title: 'Campos Editables',
            description: 'Modifique sus datos personales. Recuerde guardar los cambios al finalizar.'
          },
          side: 'left'
        },
        {
          element: '.perfil-footer, .btn-guardar-perfil, button[type="submit"]',
          popover: {
            title: 'Guardar Cambios',
            description: 'Haga clic aquí para actualizar su información en la base de datos del sistema.'
          },
          side: 'top'
        },
        {
          element: '.corner-profile-container .dropdown-menu, .dropdown-menu',
          popover: {
            title: 'Cerrar Sesión',
            description: 'Desde el menú de usuario superior derecho puede cerrar sesión de forma segura cuando termine de usar el sistema.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
