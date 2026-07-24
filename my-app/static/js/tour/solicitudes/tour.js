(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['solicitudes'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: 'button[data-bs-target="#modalCrearSolicitud"], .btn-primary, .btn-registrar',
          popover: {
            title: 'Contexto y Nueva Solicitud',
            description: 'Las solicitudes son el punto de entrada del sistema. Registre aquí nuevas peticiones: Comunidad, Institución o Particular.'
          },
          side: 'left'
        },
        {
          element: '#widget-pendientes, .stat-card, .counter',
          popover: {
            title: 'Solicitudes Pendientes',
            description: 'Indicador en tiempo real de las solicitudes que aún no han sido atendidas por el equipo.'
          },
          side: 'bottom'
        },
        {
          element: '#widget-en-proceso, .stat-card, .counter',
          popover: {
            title: 'Solicitudes en Proceso',
            description: 'Muestra las solicitudes que ya fueron asociadas a un proyecto y se encuentran en ejecución.'
          },
          side: 'bottom'
        },
        {
          element: '#search, .form-control[type="search"], input[type="search"]',
          popover: {
            title: 'Búsqueda Rápida',
            description: 'Filtre por solicitante, tipo de solicitud, problemática o estatus para localizar registros rápidamente.'
          },
          side: 'bottom'
        },
        {
          element: '#tbl_solicitudes, table.table',
          popover: {
            title: 'Registro Completo de Solicitudes',
            description: 'Listado general con tipo, solicitante, parroquia, problemática, estatus y acciones disponibles.'
          },
          side: 'top'
        },
        {
          element: '#tbl_solicitudes tbody tr:first-child .btn-info, .btn-info, .btn-ver',
          popover: {
            title: 'Ver Detalle de la Solicitud',
            description: 'Consulte toda la información: datos del solicitante, descripción del problema y seguimiento.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
