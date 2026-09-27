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
            description: 'Listado completo: descripción, empresa, número de contrato, monto, clasificación y fechas del proceso. Cada fila incluye tres acciones: ver, editar y eliminar.'
          },
          side: 'top'
        },
        {
          element: '#tablaContrataciones tbody tr:first-child .btn-accion-ver',
          popover: {
            title: 'Ver Detalle',
            description: 'Abre el modal con la ficha completa de la contratación, sin salir de la lista ni recargar la página.'
          },
          side: 'left'
        },
        {
          element: '#tablaContrataciones tbody tr:first-child .btn-accion-editar',
          popover: {
            title: 'Editar Contratación',
            description: 'Actualice los datos del contrato: fecha de inicio, fin, monto o empresa asociada.'
          },
          side: 'left'
        },
        {
          element: '#tablaContrataciones tbody tr:first-child .btn-accion-eliminar, .btn-eliminar',
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
