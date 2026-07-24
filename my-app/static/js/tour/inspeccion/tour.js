(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['inspeccion'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: 'a.btn.btn-primary, .btn-registrar',
          popover: {
            title: 'Contexto: Modulo de Inspecciones',
            description: 'Registre inspecciones de obra en diferentes etapas: inicial, intermedia y final, con observaciones y evidencias.'
          },
          side: 'left'
        },
        {
          element: '#tablaInspecciones, table.table',
          popover: {
            title: 'Registro de Inspecciones',
            description: 'Listado completo con inspector responsable, fecha de inspeccion, tipo, observaciones y acciones.'
          },
          side: 'top'
        },
        {
          element: '#tablaInspecciones tbody tr:first-child .btn-outline-info, .btn-info, .btn-ver',
          popover: {
            title: 'Ver Detalle de la Inspeccion',
            description: 'Consulte la informacion completa de la inspeccion: tipo, observaciones del inspector y fecha programada.'
          },
          side: 'left'
        },
        {
          element: '#tablaInspecciones tbody tr:first-child .btn-outline-warning, .btn-warning, .btn-editar',
          popover: {
            title: 'Editar Inspeccion',
            description: 'Modifique la fecha, tipo de inspeccion u observaciones. Asegurese de guardar los cambios.'
          },
          side: 'left'
        },
        {
          element: '#tablaInspecciones tbody tr:first-child .btn-outline-danger, .btn-danger, .btn-eliminar',
          popover: {
            title: 'Eliminar Inspeccion',
            description: 'Elimina la inspeccion tras confirmar la accion. Ideal para corregir registros duplicados o erroneos.'
          },
          side: 'left'
        },
        {
          element: '.badge-etapa-modern, .badge',
          popover: {
            title: 'Tipos de Inspeccion',
            description: 'Inspeccion Inicial (antes de la obra), Intermedia (durante el avance) o Final (al culminar la obra).'
          },
          side: 'left'
        }
      ]
    });
  };
})();
