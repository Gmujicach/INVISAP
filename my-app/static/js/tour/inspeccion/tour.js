(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['inspeccion'] = function() {
    const esListado = !!document.querySelector('#tablaInspecciones');
    const esFormulario = !!document.querySelector('#formInspeccion');

    let pasos;

    if (esListado) {
      pasos = [
        {
          element: 'a.btn.btn-primary, .btn-registrar',
          popover: {
            title: 'Registrar inspección',
            description: 'Use este botón para abrir el formulario y registrar una inspección de obra nueva.'
          },
          side: 'left'
        },
        {
          element: '#tablaInspecciones',
          popover: {
            title: 'Registro de Inspecciones',
            description: 'Listado completo con inspector responsable, fecha, tipo, observaciones y las tres acciones de cada registro.'
          },
          side: 'top'
        },
        {
          element: '.badge-etapa-modern, .badge',
          popover: {
            title: 'Tipo de inspección',
            description: 'Inicial (antes de la obra), Intermedia (durante el avance) o Final (al culminar la obra). El color identifica la etapa.'
          },
          side: 'left'
        },
        {
          element: '#tablaInspecciones tbody tr:first-child .btn-accion-ver',
          popover: {
            title: 'Botón Ver',
            description: 'Consulte la ficha completa de la inspección: tipo, fecha, inspector y observaciones.'
          },
          side: 'left'
        },
        {
          element: '#tablaInspecciones tbody tr:first-child .btn-accion-editar',
          popover: {
            title: 'Botón Editar',
            description: 'Modifique la fecha, el tipo de inspección o las observaciones. Guarde los cambios al finalizar.'
          },
          side: 'left'
        },
        {
          element: '#tablaInspecciones tbody tr:first-child .btn-accion-eliminar',
          popover: {
            title: 'Botón Eliminar',
            description: 'Elimina la inspección tras confirmar la acción. Ideal para corregir registros duplicados o erróneos.'
          },
          side: 'left'
        },
        {
          element: '#btnTourInvilara, .tour-fab',
          popover: {
            title: 'Guía interactiva del sistema',
            description: 'Este botón verde está disponible en todos los módulos y le muestra, paso a paso, cómo registrar, modificar y ver las listas.'
          },
          side: 'top'
        }
      ];
    } else if (esFormulario) {
      pasos = [
        {
          element: '#formInspeccion select[name="inspector"]',
          popover: {
            title: 'Inspector responsable',
            description: 'Seleccione quién realiza la inspección. El campo es obligatorio y el sistema no permite guardar sin él.'
          },
          side: 'right'
        },
        {
          element: '#formInspeccion input[name="fecha_inspeccion"]',
          popover: {
            title: 'Fecha de la inspección',
            description: 'Campo obligatorio. El sistema valida que la fecha sea correcta y que no esté vacía antes de guardar.'
          },
          side: 'right'
        },
        {
          element: '#formInspeccion select[name="tipo_inspeccion"]',
          popover: {
            title: 'Tipo de inspección',
            description: 'Elija la etapa: Inicial, Intermedia o Final. El tipo determina el color de la insignia en el listado.'
          },
          side: 'right'
        },
        {
          element: '#formInspeccion select[name="obra_id_obra"]',
          popover: {
            title: 'Obra inspeccionada',
            description: 'Seleccione la obra a la que corresponde esta inspección. Solo se muestran las obras registradas en el sistema.'
          },
          side: 'right'
        },
        {
          element: '#evidenciaDisplay',
          popover: {
            title: 'Evidencia fotográfica',
            description: 'Adjunte al menos una evidencia. El sistema valida en el momento que la carga se haya completado.'
          },
          side: 'right'
        },
        {
          element: '#formInspeccion textarea[name="observaciones"]',
          popover: {
            title: 'Observaciones',
            description: 'Describa lo encontrado durante la inspección. Este texto queda asociado al informe de avance de la obra.'
          },
          side: 'right'
        },
        {
          element: '#btnGuardarInspeccion',
          popover: {
            title: 'Botón Guardar',
            description: 'Valida todos los campos en el navegador y en el servidor. Si algo falta, el sistema le indica exactamente qué corregir antes de registrar.'
          },
          side: 'left'
        }
      ];
    } else {
      pasos = [
        {
          element: '#btnTourInvilara, .tour-fab',
          popover: {
            title: 'Módulo de Inspecciones',
            description: 'Abra el listado o el formulario de inspecciones para iniciar este recorrido guiado.'
          },
          side: 'left'
        }
      ];
    }

    return window.driver.js.driver({
      showProgress: true,
      steps: pasos
    });
  };
})();
