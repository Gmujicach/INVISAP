(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['usuarios'] = function() {
    return window.driver.js({
      showProgress: true,
      steps: [
        {
          element: '#respuestaFiltroMes h2',
          popover: {
            title: 'Lista de Usuarios',
            description: 'Panel con todos los usuarios creados en el sistema.'
          },
          side: 'bottom'
        },
        {
          element: 'table.table',
          popover: {
            title: 'Directorio de Usuarios',
            description: 'Tabla con avatar, nombre, cédula, correo, rol y acciones de cada usuario.'
          },
          side: 'top'
        },
        {
          element: 'table.table thead th:nth-child(5)',
          popover: {
            title: 'Rol',
            description: 'Nivel de acceso asignado a cada usuario dentro del sistema.'
          },
          side: 'bottom'
        },
        {
          element: 'table.table tbody tr:first-child .btn-warning',
          popover: {
            title: 'Editar Usuario',
            description: 'Modifique los datos del usuario. Los Super Usuario están protegidos.'
          },
          side: 'left'
        },
        {
          element: 'table.table tbody tr:first-child .btn-danger',
          popover: {
            title: 'Eliminar Usuario',
            description: 'Elimina el usuario permanentemente tras confirmación.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
