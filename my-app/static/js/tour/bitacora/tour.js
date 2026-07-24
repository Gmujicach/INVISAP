(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['bitacora'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '.stat-card',
          popover: {
            title: 'Resumen de Actividad',
            description: 'Tarjetas estadísticas con totales de creaciones, ediciones, eliminaciones y movimientos registrados en la bitácora.'
          },
          side: 'bottom'
        },
        {
          element: '#total-registros, .badge, .counter',
          popover: {
            title: 'Total de Registros Filtrados',
            description: 'Cantidad de registros que coinciden con los criterios de filtro aplicados actualmente.'
          },
          side: 'bottom'
        },
        {
          element: '#formFiltrosBitacora, .bitacora-filter-card, .card-body',
          popover: {
            title: 'Filtros de Auditoría',
            description: 'Filtre por usuario específico, módulo consultado y tipo de acción (crear, editar, eliminar, ver).'
          },
          side: 'bottom'
        },
        {
          element: '#formFiltrosBitacora button[type="submit"], .btn-primary',
          popover: {
            title: 'Aplicar Filtro',
            description: 'Ejecute la búsqueda con los criterios seleccionados para refrescar la tabla de registros.'
          },
          side: 'left'
        },
        {
          element: '#buscarBitacora, .form-control[type="search"], input[type="search"]',
          popover: {
            title: 'Búsqueda Rápida en la Tabla',
            description: 'Filtre los registros visibles sin necesidad de recargar la página, escribiendo usuario, módulo o acción.'
          },
          side: 'bottom'
        },
        {
          element: '#tabla-bitacora, table.table',
          popover: {
            title: 'Registro de Acciones del Sistema',
            description: 'Tabla detallada con cada operación: usuario responsable, módulo afectado, tipo de acción, fecha y hora exacta.'
          },
          side: 'top'
        }
      ]
    });
  };
})();
