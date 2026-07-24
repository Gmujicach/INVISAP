(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['usuarios'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '#respuestaFiltroMes h2, .card-header-custom, h1, h2',
          popover: {
            title: 'Contexto: Modulo de Usuarios',
            description: 'Administre las cuentas de acceso al sistema: cree nuevos usuarios, asigne roles, edite informacion y controle el estado.'
          },
          side: 'bottom'
        },
        {
          element: 'table.table',
          popover: {
            title: 'Directorio de Usuarios',
            description: 'Lista completa con avatar, nombre completo, cedula de identidad, correo electronico, rol y acciones disponibles.'
          },
          side: 'top'
        },
        {
          element: 'table.table thead th:nth-child(5)',
          popover: {
            title: 'Columna Rol',
            description: 'Muestra el nivel de acceso asignado (Super Usuario, Administrador, Gerente, Inspector, Recepcionista, Asistente, Proyectista, Usuario).'
          },
          side: 'bottom'
        },
        {
          element: 'table.table tbody tr:first-child .btn-warning, .btn-editar',
          popover: {
            title: 'Editar Usuario',
            description: 'Modifique datos del usuario: nombre, correo, rol o estado. Los Super Usuarios estan protegidos contra eliminacion.'
          },
          side: 'left'
        },
        {
          element: 'table.table tbody tr:first-child .btn-danger, .btn-eliminar',
          popover: {
            title: 'Eliminar Usuario',
            description: 'Elimina el usuario permanentemente tras confirmacion. Asegurese de no eliminar cuentas activas sin autorizacion.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
