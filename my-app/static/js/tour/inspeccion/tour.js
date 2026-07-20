(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['inspeccion'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: 'a.btn.btn-primary',
          popover: {
            title: 'Nueva Inspección',
            description: 'Desde el listado, acceda al formulario para registrar una inspección de obra.'
          },
          side: 'left'
        },
        {
          element: '#tablaInspecciones',
          popover: {
            title: 'Registro de Inspecciones',
            description: 'Tabla con las inspecciones: inspector, fecha, tipo, observaciones y acciones.'
          },
          side: 'top'
        },
        {
          element: '#tablaInspecciones tbody tr:first-child .btn-outline-info',
          popover: {
            title: 'Ver Detalle',
            description: 'Consulte la información completa de la inspección.'
          },
          side: 'left'
        },
        {
          element: '#tablaInspecciones tbody tr:first-child .btn-outline-warning',
          popover: {
            title: 'Editar Inspección',
            description: 'Modifique los datos de la inspección seleccionada.'
          },
          side: 'left'
        },
        {
          element: '#tablaInspecciones tbody tr:first-child .btn-outline-danger',
          popover: {
            title: 'Eliminar Inspección',
            description: 'Elimina la inspección tras confirmar la acción.'
          },
          side: 'left'
        },
        {
          element: '.badge-etapa-modern',
          popover: {
            title: 'Tipo de Inspección',
            description: 'Inspección Inicial (antes), Intermedia (durante) o Final (después) según el avance de la obra.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
