(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['obras'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: 'button[data-bs-target="#modalNuevaObra"]',
          popover: {
            title: 'Registrar Obra',
            description: 'Abra el formulario para crear una nueva obra asociada a un proyecto, contratación y semáforo.'
          },
          side: 'left'
        },
        {
          element: 'table.table',
          popover: {
            title: 'Gestión de Obras',
            description: 'Listado de obras con su título, ubicación, fechas, porcentaje de avance y semáforo de estatus.'
          },
          side: 'top'
        },
        {
          element: 'table.table thead th:nth-child(5)',
          popover: {
            title: 'Avance (%)',
            description: 'Porcentaje de ejecución física de cada obra registrada.'
          },
          side: 'bottom'
        },
        {
          element: 'table.table thead th:nth-child(6)',
          popover: {
            title: 'Semáforo',
            description: 'Indicador de color (Verde, Amarillo o Rojo) que refleja la criticidad de la obra.'
          },
          side: 'bottom'
        },
        {
          element: 'table.table tbody tr:first-child .btn-outline-info',
          popover: {
            title: 'Ver Detalle',
            description: 'Consulte toda la información de la obra: contratación, fechas y certificaciones.'
          },
          side: 'left'
        },
        {
          element: 'table.table tbody tr:first-child .btn-outline-warning',
          popover: {
            title: 'Editar Obra',
            description: 'Modifique los datos de la obra seleccionada.'
          },
          side: 'left'
        },
        {
          element: 'table.table tbody tr:first-child .btn-outline-danger',
          popover: {
            title: 'Eliminar Obra',
            description: 'Inhabilita la obra tras confirmar la acción.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
