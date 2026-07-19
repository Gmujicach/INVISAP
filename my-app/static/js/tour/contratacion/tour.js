(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['contratacion'] = function() {
    return window.driver.js({
      showProgress: true,
      steps: [
        {
          element: '#columnaBusqueda',
          popover: {
            title: 'Filtro por Columna',
            description: 'Elija el criterio de búsqueda: N° Contrato, Descripción, Monto o Empresa.'
          },
          side: 'bottom'
        },
        {
          element: '#customBuscador',
          popover: {
            title: 'Buscador de Contrataciones',
            description: 'Escriba aquí para filtrar las contrataciones registradas en el sistema.'
          },
          side: 'bottom'
        },
        {
          element: 'button[data-bs-target="#modalContratacion"]',
          popover: {
            title: 'Nueva Contratación',
            description: 'Abra el formulario para registrar una contratación asociando una empresa ganadora.'
          },
          side: 'left'
        },
        {
          element: '#tablaContrataciones',
          popover: {
            title: 'Contrataciones Registradas',
            description: 'Tabla con descripción, empresa, número de contrato, monto, clasificación y fechas del proceso.'
          },
          side: 'top'
        },
        {
          element: '#tablaContrataciones tbody tr:first-child .btn-outline-warning',
          popover: {
            title: 'Editar Contratación',
            description: 'Modifique los datos de la contratación seleccionada.'
          },
          side: 'left'
        },
        {
          element: '#tablaContrataciones tbody tr:first-child .btn-eliminar',
          popover: {
            title: 'Eliminar Contratación',
            description: 'Elimina la contratación previa confirmación.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
