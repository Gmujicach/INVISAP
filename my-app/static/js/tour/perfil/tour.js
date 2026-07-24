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
            description: 'Aqui puede ver y administrar toda su informacion personal registrada en el sistema.'
          },
          side: 'bottom'
        },
        {
          element: '.perfil-card, .card-body',
          popover: {
            title: 'Informacion Personal',
            description: 'Datos basicos: nombre completo, cedula de identidad, correo, telefono y rol asignado.'
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
            description: 'Haga clic aqui para actualizar su informacion en la base de datos del sistema.'
          },
          side: 'top'
        },
        {
          element: '.corner-profile-container .dropdown-menu, .dropdown-menu',
          popover: {
            title: 'Cerrar Sesion',
            description: 'Desde el menu de usuario superior derecho puede cerrar sesion de forma segura cuando termine de usar el sistema.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
