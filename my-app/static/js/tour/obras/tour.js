(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['obras'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: 'button[data-bs-target="#modalNuevaObra"], .btn-primary, .btn-registrar',
          popover: {
            title: 'Contexto: Módulo de Obras',
            description: 'Registre y gestione las obras físicas derivadas de proyectos aprobados, con control de avance y estatus.'
          },
          side: 'left'
        },
        {
          element: 'table.table',
          popover: {
            title: 'Gestión de Obras',
            description: 'Listado de obras con título, ubicación, fechas de inicio y fin, porcentaje de avance y semáforo de estatus.'
          },
          side: 'top'
        },
        {
          element: 'table.table thead th:nth-child(5)',
          popover: {
            title: 'Avance (%)',
            description: 'Porcentaje de ejecución física registrado para cada obra. Permite monitorear el cumplimiento de metas.'
          },
          side: 'bottom'
        },
        {
          element: 'table.table thead th:nth-child(6)',
          popover: {
            title: 'Semáforo de Estatus',
            description: 'Indicador visual: Verde (avance normal), Amarillo (atención) o Rojo (crítico/atrasado).'
          },
          side: 'bottom'
        },
        {
          element: 'table.table tbody tr:first-child .btn-outline-info, .btn-info, .btn-ver',
          popover: {
            title: 'Ver Detalle de la Obra',
            description: 'Consulte información completa: contratación asociada, fechas, certificaciones y observaciones del supervisor.'
          },
          side: 'left'
        },
        {
          element: 'table.table tbody tr:first-child .btn-outline-warning, .btn-warning, .btn-editar',
          popover: {
            title: 'Editar Obra',
            description: 'Modifique datos de la obra: avance, fechas, estatus o contratación. Los cambios se guardan automáticamente.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
