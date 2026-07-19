(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['seguridad'] = function() {
    return window.driver.js({
      showProgress: true,
      steps: [
        {
          element: '#seguridadTabs #tab-roles',
          popover: {
            title: 'Pestaña Roles',
            description: 'Gestione los roles del sistema y su información asociada.'
          },
          side: 'bottom'
        },
        {
          element: '#seguridadTabs #tab-modulos',
          popover: {
            title: 'Pestaña Módulos',
            description: 'Administre los módulos disponibles y su configuración de menú.'
          },
          side: 'bottom'
        },
        {
          element: '#seguridadTabs #tab-permisos',
          popover: {
            title: 'Asignar Permisos',
            description: 'Configure los permisos (Ver, Crear, Editar, Eliminar) por rol y módulo.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaRoles',
          popover: {
            title: 'Tabla de Roles',
            description: 'Listado de roles con su ID, nombre, descripción y estado.'
          },
          side: 'top'
        },
        {
          element: '#selectRol',
          popover: {
            title: 'Selector de Rol',
            description: 'Elija un rol para visualizar y editar sus permisos en la tabla.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaPermisos',
          popover: {
            title: 'Matriz de Permisos',
            description: 'Marque o desmarque las casillas para definir el acceso de cada módulo por rol.'
          },
          side: 'top'
        },
        {
          element: '#btnGuardarPermisos',
          popover: {
            title: 'Guardar Permisos',
            description: 'Persiste los cambios de permisos realizados para el rol seleccionado.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
