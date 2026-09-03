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
          element: 'button[onclick="clasificarTodo()"], .btn-warning',
          popover: {
            title: 'Clasificar Todo con IA',
            description: 'Ejecuta el motor de inteligencia artificial sobre todas las solicitudes pendientes para asignar su prioridad automaticamente.'
          },
          side: 'bottom'
        },
        {
          element: 'button[onclick="cargarPrioridades()"], .btn-primary',
          popover: {
            title: 'Actualizar Prioridades',
            description: 'Recarga las filas de prioridad desde el servidor para ver los resultados mas recientes de la clasificacion.'
          },
          side: 'bottom'
        },
        {
          element: '#buscarPrioridad, .form-control[type="search"], input[type="search"]',
          popover: {
            title: 'Busqueda Rapida',
            description: 'Filtre las filas de prioridad por numero de solicitud, solicitante o justificacion.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaPrioridades, .table-row, .custom-table',
          popover: {
            title: 'Tabla de Prioridades',
            description: 'Cada fila representa una solicitud con su rango numerico, semaforo de prioridad, nivel de gravedad y justificacion de la IA.'
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
          element: '#tablaPrioridades tbody tr:first-child .btn-outline-primary, .btn-editar',
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
