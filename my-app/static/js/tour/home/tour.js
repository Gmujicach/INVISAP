(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['home'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '.dashboard-card',
          popover: {
            title: 'Panel de Control (Dashboard)',
            description: 'Vista general del sistema con indicadores clave: total de solicitudes, pendientes, en proceso y completadas.'
          },
          side: 'bottom'
        },
        {
          element: '.col-md-3:last-child .dashboard-card',
          popover: {
            title: 'Solicitudes Completadas',
            description: 'Indicador que muestra la cantidad de solicitudes procesadas exitosamente.'
          },
          side: 'bottom'
        },
        {
          element: 'img[alt="Gráfico Tipos de Solicitud"]',
          popover: {
            title: 'Gráfico por Tipo de Solicitud',
            description: 'Distribución visual de solicitudes según su tipo: Comunidad, Particular, Institución, entre otros.'
          },
          side: 'bottom'
        },
        {
          element: 'img[alt="Gráfico Estatus de Solicitud"]',
          popover: {
            title: 'Gráfico por Estatus',
            description: 'Porcentaje de solicitudes en cada estatus: pendiente, en proceso o completada.'
          },
          side: 'bottom'
        },
        {
          element: 'img[alt="Gráfico por Parroquia"]',
          popover: {
            title: 'Mapa Geográfico por Parroquia',
            description: 'Visualice en qué parroquias del estado Lara se concentran las solicitudes para apoyar la toma de decisiones.'
          },
          side: 'bottom'
        },
        {
          element: 'table.table-hover.mb-0',
          popover: {
            title: 'Módulo de Priorización Inteligente',
            description: 'Solicitudes priorizadas automáticamente por IA, ordenadas de mayor a menor prioridad para una gestión eficiente.'
          },
          side: 'bottom'
        },
        {
          element: 'table.table-hover.mb-0 tbody tr:first-child',
          popover: {
            title: 'Fila de Solicitud Priorizada',
            description: 'se puede observar la solicitud priorizada junto con su información detallada.'
          },
          side: 'right'
        }
      ]
    });
  };
})();
