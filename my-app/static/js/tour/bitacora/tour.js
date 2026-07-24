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
            description: 'Tarjetas estadisticas con totales de creaciones, ediciones, eliminaciones y movimientos registrados en la bitacora.'
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
            title: 'Filtros de Auditoria',
            description: 'Filtre por usuario especifico, modulo consultado y tipo de accion (crear, editar, eliminar, ver).'
          },
          side: 'bottom'
        },
        {
          element: '#formFiltrosBitacora button[type="submit"], .btn-primary',
          popover: {
            title: 'Aplicar Filtro',
            description: 'Ejecute la busqueda con los criterios seleccionados para refrescar la tabla de registros.'
          },
          side: 'left'
        },
        {
          element: '#buscarBitacora, .form-control[type="search"], input[type="search"]',
          popover: {
            title: 'Busqueda Rapida en la Tabla',
            description: 'Filtre los registros visibles sin necesidad de recargar la pagina, escribiendo usuario, modulo o accion.'
          },
          side: 'bottom'
        },
        {
          element: '#tabla-bitacora, table.table',
          popover: {
            title: 'Registro de Acciones del Sistema',
            description: 'Tabla detallada con cada operacion: usuario responsable, modulo afectado, tipo de accion, fecha y hora exacta.'
          },
          side: 'top'
        }
      ]
    });
  };
})();
