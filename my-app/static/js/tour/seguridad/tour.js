(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['seguridad'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '.seguridad-header, h1, h2',
          popover: {
            title: 'Gestión de Roles y Permisos',
            description: 'Módulo de seguridad para administrar roles, permisos de acceso y configurar qué puede hacer cada usuario en el sistema.'
          },
          side: 'bottom'
        },
        {
          element: '.seguridad-filter-card, #formFiltrosSeguridad, .card-body',
          popover: {
            title: 'Filtros de Búsqueda',
            description: 'Filtre roles o permisos por nombre, descripción o estado para encontrar rápidamente lo que necesita.'
          },
          side: 'top'
        },
        {
          element: 'button[data-bs-target*="modal"], .btn-primary, .btn-registrar',
          popover: {
            title: 'Registrar Nuevo Rol',
            description: 'Abra el formulario para crear un nuevo rol de usuario dentro del sistema.'
          },
          side: 'left'
        },
        {
          element: '#tablaRoles, table.table, .seguridad-table-card table',
          popover: {
            title: 'Directorio de Roles',
            description: 'Tabla con todos los roles configurados: nombre, descripción, cantidad de usuarios asignados y estado.'
          },
          side: 'top'
        },
        {
          element: '.btn-warning, .btn-editar',
          popover: {
            title: 'Editar Rol',
            description: 'Modifique los permisos asociados a un rol. Los cambios se aplican inmediatamente a todos los usuarios con ese rol.'
          },
          side: 'left'
        },
        {
          element: '.btn-danger, .btn-eliminar',
          popover: {
            title: 'Eliminar Rol',
            description: 'Elimina el rol del sistema. Se solicita confirmación antes de proceder.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
