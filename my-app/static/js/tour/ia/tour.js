(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['ia'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: 'button[onclick="clasificarTodo()"]',
          popover: {
            title: 'Clasificar con IA',
            description: 'Ejecuta la inteligencia artificial sobre todas las solicitudes para asignar prioridad automática.'
          },
          side: 'bottom'
        },
        {
          element: 'button[onclick="cargarPrioridades()"]',
          popover: {
            title: 'Actualizar',
            description: 'Recarga las tarjetas de prioridad desde el servidor.'
          },
          side: 'bottom'
        },
        {
          element: '#buscarPrioridad',
          popover: {
            title: 'Búsqueda Rápida',
            description: 'Filtre las prioridades por solicitud o justificación en la página actual.'
          },
          side: 'bottom'
        },
        {
          element: '#contenedorTarjetas',
          popover: {
            title: 'Tarjetas de Prioridad',
            description: 'Cada tarjeta muestra el rango, semáforo, nivel de gravedad y estado de la solicitud.'
          },
          side: 'top'
        },
        {
          element: '#contadorRegistros',
          popover: {
            title: 'Total de Registros',
            description: 'Cantidad de prioridades gestionadas por el módulo de IA.'
          },
          side: 'bottom'
        },
        {
          element: '#contenedorTarjetas .card:first-child .btn-outline-primary',
          popover: {
            title: 'Ajustar Prioridad',
            description: 'Edite manualmente el rango y la justificación de la prioridad.'
          },
          side: 'left'
        },
        {
          element: '#contenedorTarjetas .card:first-child .btn-outline-info',
          popover: {
            title: 'Clasificar con IA',
            description: 'Solicita a la IA que reevalúe la prioridad de esta solicitud específica.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
