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
          element: 'img[alt="Grafico Tipos de Solicitud"]',
          popover: {
            title: 'Grafico por Tipo de Solicitud',
            description: 'Distribucion visual de solicitudes segun su tipo: Comunidad, Particular, Institucion, entre otros.'
          },
          side: 'bottom'
        },
        {
          element: 'img[alt="Grafico Estatus de Solicitud"]',
          popover: {
            title: 'Grafico por Estatus',
            description: 'Porcentaje de solicitudes en cada estatus: pendiente, en proceso o completada.'
          },
          side: 'bottom'
        },
        {
          element: 'img[alt="Grafico por Parroquia"]',
          popover: {
            title: 'Mapa Geografico por Parroquia',
            description: 'Visualice en que parroquias del estado Lara se concentran las solicitudes para apoyar la toma de decisiones.'
          },
          side: 'bottom'
        },
        {
          element: 'table.table-hover.mb-0',
          popover: {
            title: 'Modulo de Priorizacion Inteligente',
            description: 'Solicitudes priorizadas automaticamente por IA, ordenadas de mayor a menor prioridad para una gestion eficiente.'
          },
          side: 'bottom'
        },
        {
          element: 'table.table-hover.mb-0 tbody tr:first-child',
          popover: {
            title: 'Fila de Solicitud Priorizada',
            description: 'se puede observar la solicitud priorizada junto con su informacion detallada.'
          },
          side: 'right'
        }
      ]
    });
  };
})();
