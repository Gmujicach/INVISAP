(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['bitacora'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      animate: true,
      smoothScroll: false,
      steps: [
        {
          element: '#btnActualizarBitacora',
          popover: {
            title: 'Actualizar la bitácora',
            description: 'Recarga los registros y las estadísticas de actividad sin salir de esta pantalla.'
          },
          side: 'left'
        },
        {
          element: '#total-registros',
          popover: {
            title: 'Total de registros',
            description: 'Consulta cuántos registros coinciden con los filtros seleccionados.'
          },
          side: 'bottom'
        },
        {
          element: '#formFiltrosBitacora input[name="usuario"]',
          popover: {
            title: 'Filtrar por usuario',
            description: 'Escribe el nombre de usuario para ver únicamente las acciones realizadas por esa persona.'
          },
          side: 'bottom'
        },
        {
          element: '#formFiltrosBitacora select[name="modulo"]',
          popover: {
            title: 'Filtrar por módulo',
            description: 'Selecciona un módulo para limitar los resultados a las acciones registradas en esa sección.'
          },
          side: 'bottom'
        },
        {
          element: '#formFiltrosBitacora select[name="accion"]',
          popover: {
            title: 'Filtrar por acción',
            description: 'Selecciona el tipo de acción que deseas consultar, como crear, editar, eliminar o iniciar sesión.'
          },
          side: 'bottom'
        },
        {
          element: '#formFiltrosBitacora button[type="submit"]',
          popover: {
            title: 'Aplicar filtros',
            description: 'Pulsa Filtrar para actualizar la lista con los criterios de usuario, módulo y acción seleccionados.'
          },
          side: 'left'
        },
        {
          element: '#buscarBitacora',
          popover: {
            title: 'Búsqueda rápida',
            description: 'Busca texto en los registros mostrados en la tabla sin volver a enviar los filtros.'
          },
          side: 'left'
        },
        {
          element: '#tabla-bitacora thead',
          popover: {
            title: 'Columnas de la bitácora',
            description: 'La tabla organiza cada registro por usuario, módulo, acción, fecha, inicio de sesión y detalle.'
          },
          side: 'bottom'
        },
        {
          element: '#tabla-bitacora tbody tr.fila-registro:first-child',
          popover: {
            title: 'Registros de actividad',
            description: 'Cada fila representa una acción registrada. Revisa quién la realizó, en qué módulo y cuándo ocurrió.'
          },
          side: 'top'
        },
        {
          element: '#tabla-bitacora tbody tr.fila-registro:first-child .btn-detalle-bitacora',
          popover: {
            title: 'Ver detalle del registro',
            description: 'Abre la ficha del evento con la información completa del usuario, módulo, acción y sesión.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
