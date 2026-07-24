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
            description: 'Las solicitudes son el punto de entrada del sistema. Registre aqui nuevas peticiones: Comunidad, Institucion o Particular.'
          },
          side: 'left'
        },
        {
          element: '#widget-pendientes, .stat-card, .counter',
          popover: {
            title: 'Solicitudes Pendientes',
            description: 'Indicador en tiempo real de las solicitudes que aun no han sido atendidas por el equipo.'
          },
          side: 'bottom'
        },
        {
          element: '#widget-en-proceso, .stat-card, .counter',
          popover: {
            title: 'Solicitudes en Proceso',
            description: 'Muestra las solicitudes que ya fueron asociadas a un proyecto y se encuentran en ejecucion.'
          },
          side: 'bottom'
        },
        {
          element: '#search, .form-control[type="search"], input[type="search"]',
          popover: {
            title: 'Busqueda Rapida',
            description: 'Filtre por solicitante, tipo de solicitud, problematica o estatus para localizar registros rapidamente.'
          },
          side: 'bottom'
        },
        {
          element: '#tbl_solicitudes, table.table',
          popover: {
            title: 'Registro Completo de Solicitudes',
            description: 'Listado general con tipo, solicitante, parroquia, problematica, estatus y acciones disponibles.'
          },
          side: 'top'
        },
        {
          element: '#tbl_solicitudes tbody tr:first-child .btn-info, .btn-info, .btn-ver',
          popover: {
            title: 'Ver Detalle de la Solicitud',
            description: 'Consulte toda la informacion: datos del solicitante, descripcion del problema y seguimiento.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
