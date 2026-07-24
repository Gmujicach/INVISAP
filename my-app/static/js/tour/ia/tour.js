(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['ia'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '.card-header-custom, h1, h2, h3',
          popover: {
            title: 'Contexto: Módulo de Inteligencia Artificial',
            description: 'Utilice la IA para clasificar automáticamente las solicitudes por nivel de prioridad (Alta, Media, Baja) basándose en factores de gravedad.'
          },
          side: 'bottom'
        },
        {
          element: 'button[onclick="clasificarTodo()"], .btn-primary, .btn-ia',
          popover: {
            title: 'Clasificar Todo con IA',
            description: 'Ejecuta el motor de inteligencia artificial sobre todas las solicitudes pendientes para asignar su prioridad automáticamente.'
          },
          side: 'bottom'
        },
        {
          element: 'button[onclick="cargarPrioridades()"], .btn-outline-secondary, .btn-actualizar',
          popover: {
            title: 'Actualizar Prioridades',
            description: 'Recarga las tarjetas de prioridad desde el servidor para ver los resultados más recientes de la clasificación.'
          },
          side: 'bottom'
        },
        {
          element: '#buscarPrioridad, .form-control[type="search"], input[type="search"]',
          popover: {
            title: 'Búsqueda Rápida',
            description: 'Filtre las tarjetas de prioridad por número de solicitud, solicitante o justificación.'
          },
          side: 'bottom'
        },
        {
          element: '#contenedorTarjetas, .prioridad-card, .card',
          popover: {
            title: 'Tarjetas de Prioridad',
            description: 'Cada tarjeta representa una solicitud con su rango numérico, semáforo de prioridad, nivel de gravedad y justificación de la IA.'
          },
          side: 'top'
        },
        {
          element: '#contadorRegistros, .badge, .counter',
          popover: {
            title: 'Total de Registros',
            description: 'Cantidad de prioridades gestionadas actualmente por el módulo de inteligencia artificial.'
          },
          side: 'bottom'
        },
        {
          element: '#contenedorTarjetas .card:first-child .btn-outline-primary, .btn-editar',
          popover: {
            title: 'Ajustar Prioridad Manualmente',
            description: 'Edite manualmente el rango y la justificación de la prioridad si considera que la clasificación de la IA debe ajustarse.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
