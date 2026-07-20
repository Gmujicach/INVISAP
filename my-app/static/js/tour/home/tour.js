(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['home'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '.dashboard-card',
          popover: {
            title: 'Tarjetas de Resumen',
            description: 'Estas tarjetas muestran indicadores clave: total de solicitudes, pendientes, en proceso y completadas del sistema.'
          },
          side: 'bottom'
        },
        {
          element: '.col-md-3:last-child .dashboard-card',
          popover: {
            title: 'Solicitudes Completadas',
            description: 'Aquí se visualiza la cantidad de solicitudes procesadas o completadas exitosamente.'
          },
          side: 'bottom'
        },
        {
          element: 'img[alt="Gráfico Tipos de Solicitud"]',
          popover: {
            title: 'Análisis por Tipo',
            description: 'Gráfico que distribuye las solicitudes según su tipo (Comunidad, Particular, Institución, etc.).'
          },
          side: 'top'
        },
        {
          element: 'img[alt="Gráfico Estatus de Solicitud"]',
          popover: {
            title: 'Distribución por Estatus',
            description: 'Visualice el porcentaje de solicitudes en cada estatus: pendiente, en proceso o completada.'
          },
          side: 'top'
        },
        {
          element: 'img[alt="Gráfico por Parroquia"]',
          popover: {
            title: 'Análisis por Parroquia',
            description: 'Mapa de calor que agrupa las solicitudes por parroquia de Lara para apoyar la toma de decisiones.'
          },
          side: 'top'
        },
        {
          element: 'table.table',
          popover: {
            title: 'Módulo de Priorización',
            description: 'Tabla con las solicitudes priorizadas por la inteligencia artificial, ordenadas de mayor a menor prioridad.'
          },
          side: 'top'
        }
      ]
    });
  };
})();
