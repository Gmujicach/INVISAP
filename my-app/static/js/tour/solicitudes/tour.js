(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['solicitudes'] = function() {
    return window.driver.js({
      showProgress: true,
      steps: [
        {
          element: 'button[data-bs-target="#modalCrearSolicitud"]',
          popover: {
            title: 'Nueva Solicitud',
            description: 'Abra el formulario para registrar una nueva solicitud (Comunidad, Institución o Particular).'
          },
          side: 'left'
        },
        {
          element: '#widget-pendientes',
          popover: {
            title: 'Solicitudes Pendientes',
            description: 'Indicador con la cantidad de solicitudes que aún no han sido atendidas.'
          },
          side: 'bottom'
        },
        {
          element: '#widget-en-proceso',
          popover: {
            title: 'En Proceso',
            description: 'Muestra las solicitudes que ya fueron asociadas a un proyecto y se encuentran en ejecución.'
          },
          side: 'bottom'
        },
        {
          element: '#search',
          popover: {
            title: 'Búsqueda Rápida',
            description: 'Filtre el registro completo de solicitudes escribiendo solicitante, tipo o problemática.'
          },
          side: 'bottom'
        },
        {
          element: '#tbl_solicitudes',
          popover: {
            title: 'Registro Completo',
            description: 'Tabla con todas las solicitudes, su estatus y las acciones disponibles para cada una.'
          },
          side: 'top'
        },
        {
          element: '#tbl_solicitudes tbody tr:first-child .btn-info',
          popover: {
            title: 'Ver Detalles',
            description: 'Consulte la información completa de la solicitud seleccionada.'
          },
          side: 'left'
        },
        {
          element: '#tbl_solicitudes tbody tr:first-child .btn-warning',
          popover: {
            title: 'Editar Solicitud',
            description: 'Modifique el estatus u observaciones de la solicitud de forma rápida.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
