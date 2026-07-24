(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['contratacion'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '#columnaBusqueda, select[name="columna"]',
          popover: {
            title: 'Contexto: Módulo de Contrataciones',
            description: 'Administre los procesos de contratación de obras y servicios: registre, edite y dé seguimiento a los contratos.'
          },
          side: 'bottom'
        },
        {
          element: '#customBuscador, .form-control[type="search"], input[type="search"]',
          popover: {
            title: 'Buscador de Contrataciones',
            description: 'Filtre por número de contrato, descripción, empresa contratada o monto.'
          },
          side: 'bottom'
        },
        {
          element: 'button[data-bs-target="#modalContratacion"], .btn-primary, .btn-registrar',
          popover: {
            title: 'Registrar Nueva Contratación',
            description: 'Abra el formulario para crear una contratación. Asocie la empresa ganadora, monto, número de contrato y fechas.'
          },
          side: 'left'
        },
        {
          element: '#tablaContrataciones, table.table',
          popover: {
            title: 'Contrataciones Registradas',
            description: 'Listado completo: descripción, empresa, número de contrato, monto, clasificación, fechas de inicio y fin.'
          },
          side: 'top'
        },
        {
          element: '#tablaContrataciones tbody tr:first-child .btn-outline-warning, .btn-warning, .btn-editar',
          popover: {
            title: 'Editar Contratación',
            description: 'Actualice datos del contrato: fecha de inicio, fin, monto o empresa asociada.'
          },
          side: 'left'
        },
        {
          element: '#tablaContrataciones tbody tr:first-child .btn-eliminar, .btn-danger, .btn-eliminar',
          popover: {
            title: 'Eliminar Contratación',
            description: 'Elimina la contratación tras confirmar la acción. Use con precaución, esta acción no se puede deshacer.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
