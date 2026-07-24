(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['ia'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '.card-header-custom, h1, h2, h3',
          popover: {
            title: 'Contexto: Modulo de Inteligencia Artificial',
            description: 'Utilice la IA para clasificar automaticamente las solicitudes por nivel de prioridad (Alta, Media, Baja) basandose en factores de gravedad.'
          },
          side: 'bottom'
        },
        {
          element: 'button[onclick="clasificarTodo()"], .btn-primary, .btn-ia',
          popover: {
            title: 'Clasificar Todo con IA',
            description: 'Ejecuta el motor de inteligencia artificial sobre todas las solicitudes pendientes para asignar su prioridad automaticamente.'
          },
          side: 'bottom'
        },
        {
          element: 'button[onclick="cargarPrioridades()"], .btn-outline-secondary, .btn-actualizar',
          popover: {
            title: 'Actualizar Prioridades',
            description: 'Recarga las tarjetas de prioridad desde el servidor para ver los resultados mas recientes de la clasificacion.'
          },
          side: 'bottom'
        },
        {
          element: '#buscarPrioridad, .form-control[type="search"], input[type="search"]',
          popover: {
            title: 'Busqueda Rapida',
            description: 'Filtre las tarjetas de prioridad por numero de solicitud, solicitante o justificacion.'
          },
          side: 'bottom'
        },
        {
          element: '#contenedorTarjetas, .prioridad-card, .card',
          popover: {
            title: 'Tarjetas de Prioridad',
            description: 'Cada tarjeta representa una solicitud con su rango numerico, semaforo de prioridad, nivel de gravedad y justificacion de la IA.'
          },
          side: 'top'
        },
        {
          element: '#contadorRegistros, .badge, .counter',
          popover: {
            title: 'Total de Registros',
            description: 'Cantidad de prioridades gestionadas actualmente por el modulo de inteligencia artificial.'
          },
          side: 'bottom'
        },
        {
          element: '#contenedorTarjetas .card:first-child .btn-outline-primary, .btn-editar',
          popover: {
            title: 'Ajustar Prioridad Manualmente',
            description: 'Edite manualmente el rango y la justificacion de la prioridad si considera que la clasificacion de la IA debe ajustarse.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
