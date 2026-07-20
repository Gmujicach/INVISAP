(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['reportes'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '#filtroBusqueda',
          popover: {
            title: 'Filtro de Datos',
            description: 'Escriba un módulo a analizar (ej: solicitudes). Déjelo vacío para un análisis global del sistema.'
          },
          side: 'bottom'
        },
        {
          element: '#btnAplicarFiltro',
          popover: {
            title: 'Aplicar Filtro',
            description: 'Actualiza los gráficos estadísticos según el módulo indicado.'
          },
          side: 'bottom'
        },
        {
          element: '#tipoChart',
          popover: {
            title: 'Tipo de Solicitud',
            description: 'Gráfico que distribuye las solicitudes por su tipo. Use el selector para cambiar el tipo de visualización.'
          },
          side: 'top'
        },
        {
          element: '#estatusChart',
          popover: {
            title: 'Estatus de Solicitud',
            description: 'Gráfico del estado de las solicitudes (pendiente, en proceso, completada).'
          },
          side: 'top'
        },
        {
          element: '#fechaChart',
          popover: {
            title: 'Tendencia por Fecha',
            description: 'Evolución temporal de las solicitudes registradas.'
          },
          side: 'top'
        },
        {
          element: 'a[href*="generarReporteEstadistico"]',
          popover: {
            title: 'Descargar PDF',
            description: 'Exporte el análisis estadístico completo en formato PDF.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
