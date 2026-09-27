(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['seguridad'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '.seguridad-header, h1, h2',
          popover: {
            title: 'Gestion de Roles y Permisos',
            description: 'Modulo de seguridad para administrar roles, permisos de acceso y configurar que puede hacer cada usuario en el sistema.'
          },
          side: 'bottom'
        },
        {
          element: '.seguridad-filter-card, #formFiltrosSeguridad, .card-body',
          popover: {
            title: 'Filtros de Busqueda',
            description: 'Filtre roles o permisos por nombre, descripcion o estado para encontrar rapidamente lo que necesita.'
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
            description: 'Tabla con todos los roles configurados: nombre, descripcion, cantidad de usuarios asignados y estado.'
          },
          side: 'top'
        },
        {
          element: '#tablaRoles tbody tr:first-child .btn-accion-editar',
          popover: {
            title: 'Botón Editar Rol',
            description: 'Modifique el nombre, la descripción y el estado de un rol. Después podrá asignarle o quitarle permisos desde la pestaña de permisos.'
          },
          side: 'left'
        },
        {
          element: '#tablaRoles tbody tr:first-child .btn-accion-eliminar',
          popover: {
            title: 'Botón Eliminar Rol',
            description: 'Elimina el rol del sistema. Se solicita confirmación antes de proceder y la acción queda registrada en la bitácora.'
          },
          side: 'left'
        },
        {
          element: 'button[data-bs-target*="modal"]',
          popover: {
            title: 'Gestionar el módulo de seguridad',
            description: 'Desde aquí se registran los módulos del sistema, los roles y los permisos por rol: así es como el sistema controla quién entra a cada módulo y qué puede hacer (Roles, permisos y perfiles de usuario).'
          },
          side: 'bottom'
        }
      ]
    });
  };
})();
