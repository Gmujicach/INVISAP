(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['contratacion'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '#columnaBusqueda, select[name="columna"]',
          popover: {
            title: 'Contexto: Modulo de Contrataciones',
            description: 'Administre los procesos de contratacion de obras y servicios: registre, edite y de seguimiento a los contratos.'
          },
          side: 'bottom'
        },
        {
          element: '#customBuscador, .form-control[type="search"], input[type="search"]',
          popover: {
            title: 'Buscador de Contrataciones',
            description: 'Filtre por numero de contrato, descripcion, empresa contratada o monto.'
          },
          side: 'bottom'
        },
        {
          element: 'button[data-bs-target="#modalContratacion"], .btn-primary, .btn-registrar',
          popover: {
            title: 'Registrar Nueva Contratacion',
            description: 'Abra el formulario para crear una contratacion. Asocie la empresa ganadora, monto, numero de contrato y fechas.'
          },
          side: 'left'
        },
        {
          element: '#tablaContrataciones, table.table',
          popover: {
            title: 'Contrataciones Registradas',
            description: 'Listado completo: descripcion, empresa, numero de contrato, monto, clasificacion, fechas de inicio y fin.'
          },
          side: 'top'
        },
        {
          element: '#tablaContrataciones tbody tr:first-child .btn-outline-warning, .btn-warning, .btn-editar',
          popover: {
            title: 'Editar Contratacion',
            description: 'Actualice datos del contrato: fecha de inicio, fin, monto o empresa asociada.'
          },
          side: 'left'
        },
        {
          element: '#tablaContrataciones tbody tr:first-child .btn-eliminar, .btn-danger, .btn-eliminar',
          popover: {
            title: 'Eliminar Contratacion',
            description: 'Elimina la contratacion tras confirmar la accion. Use con precaucion, esta accion no se puede deshacer.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
