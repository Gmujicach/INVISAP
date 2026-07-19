(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['bitacora'] = function() {
    return window.driver.js({
      showProgress: true,
      steps: [
        {
          element: '.stat-card',
          popover: {
            title: 'Tarjetas Estadísticas',
            description: 'Resumen de creaciones, ediciones, eliminaciones y total de registros en la bitácora.'
          },
          side: 'bottom'
        },
        {
          element: '#total-registros',
          popover: {
            title: 'Total Filtrado',
            description: 'Cantidad de registros que coinciden con los filtros aplicados.'
          },
          side: 'bottom'
        },
        {
          element: '#formFiltrosBitacora',
          popover: {
            title: 'Filtros de Bitácora',
            description: 'Filtre por usuario, módulo y acción para auditar las operaciones del sistema.'
          },
          side: 'bottom'
        },
        {
          element: '#formFiltrosBitacora button[type="submit"]',
          popover: {
            title: 'Aplicar Filtro',
            description: 'Ejecute la búsqueda con los criterios seleccionados.'
          },
          side: 'left'
        },
        {
          element: '#tabla-bitacora',
          popover: {
            title: 'Registro de Acciones',
            description: 'Tabla con cada acción realizada: usuario, módulo, tipo de acción, fecha y hora de inicio de sesión.'
          },
          side: 'top'
        },
        {
          element: '#buscarBitacora',
          popover: {
            title: 'Búsqueda Rápida',
            description: 'Filtre los registros visibles escribiendo en este campo de búsqueda.'
          },
          side: 'bottom'
        }
      ]
    });
  };
})();
