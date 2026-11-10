(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['respaldo'] = function() {
    const exportModalOpen = !!document.querySelector('#modalExportarRespaldo.show');
    const importModalOpen = !!document.querySelector('#modalImportarRespaldo.show');
    const detailModalOpen = !!document.querySelector('#modalDetalleRespaldo.show');
    const deleteModalOpen = !!document.querySelector('#modalEliminarRespaldo.show');
    let steps;

    if (exportModalOpen) {
      steps = [
        {
          element: '#nombreArchivoRespaldo',
          popover: {
            title: 'Nombre del archivo',
            description: 'Escribe un nombre fácil de reconocer para este respaldo. Si lo dejas vacío, se asignará uno automáticamente.'
          },
          side: 'bottom'
        },
        {
          element: '#descripcionRespaldo',
          popover: {
            title: 'Descripción del respaldo',
            description: 'Agrega una nota opcional para identificar el propósito o el período de esta copia.'
          },
          side: 'bottom'
        },
        {
          element: '#modalExportarRespaldo .alert-warning',
          popover: {
            title: 'Antes de generar',
            description: 'El proceso puede tardar según el tamaño de la base de datos. Mantén esta ventana abierta mientras se completa.'
          },
          side: 'top'
        },
        {
          element: '#btnExportar',
          popover: {
            title: 'Generar respaldo',
            description: 'Pulsa aquí para crear y guardar la copia de seguridad de la base de datos.'
          },
          side: 'top'
        }
      ];
    } else if (importModalOpen) {
      steps = [
        {
          element: '#dropZoneImportar',
          popover: {
            title: 'Seleccionar archivo de respaldo',
            description: 'Arrastra aquí un archivo .sql o pulsa esta zona para buscarlo en tu equipo.'
          },
          side: 'bottom'
        },
        {
          element: '#modalImportarRespaldo .alert-danger',
          popover: {
            title: 'Importante antes de restaurar',
            description: 'La importación reemplaza los datos actuales de la base de datos. Confirma que tienes una copia válida antes de continuar.'
          },
          side: 'top'
        },
        {
          element: '#btnImportar',
          popover: {
            title: 'Importar y restaurar',
            description: 'Después de seleccionar el archivo .sql, usa este botón para iniciar la restauración.'
          },
          side: 'top'
        }
      ];
    } else if (detailModalOpen) {
      steps = [
        {
          element: '#modalDetalleRespaldoLabel',
          popover: {
            title: 'Detalle del respaldo',
            description: 'Esta ventana muestra la información de la copia que seleccionaste.'
          },
          side: 'bottom'
        },
        {
          element: '#cuerpoDetalleRespaldo .list-group-item:nth-child(1)',
          popover: {
            title: 'Archivo',
            description: 'Nombre del archivo de respaldo guardado.'
          },
          side: 'right'
        },
        {
          element: '#cuerpoDetalleRespaldo .list-group-item:nth-child(2)',
          popover: {
            title: 'Fecha de creación',
            description: 'Fecha y hora en que se generó esta copia.'
          },
          side: 'right'
        },
        {
          element: '#cuerpoDetalleRespaldo .list-group-item:nth-child(3)',
          popover: {
            title: 'Tamaño',
            description: 'Espacio que ocupa el archivo del respaldo.'
          },
          side: 'right'
        },
        {
          element: '#cuerpoDetalleRespaldo .list-group-item:nth-child(4)',
          popover: {
            title: 'Descripción',
            description: 'Nota asociada al respaldo, si se indicó una al generarlo.'
          },
          side: 'right'
        },
        {
          element: '#modalDetalleRespaldo .modal-footer button[data-bs-dismiss="modal"]',
          popover: {
            title: 'Cerrar detalle',
            description: 'Cierra la ficha y vuelve al listado de respaldos.'
          },
          side: 'top'
        }
      ];
    } else if (deleteModalOpen) {
      steps = [
        {
          element: '#modalEliminarRespaldo .modal-body',
          popover: {
            title: 'Confirmación de eliminación',
            description: 'Revisa el aviso: eliminar un respaldo también borra su archivo .sql y no se puede deshacer.'
          },
          side: 'bottom'
        },
        {
          element: '#btnConfirmarEliminarRespaldo',
          popover: {
            title: 'Eliminar respaldo',
            description: 'Confirma únicamente si estás seguro de que ya no necesitas esta copia.'
          },
          side: 'top'
        }
      ];
    } else {
      steps = [
        {
          element: '.card-respaldo > .card-header h5',
          popover: {
            title: 'Administración de respaldos',
            description: 'Desde este módulo puedes crear copias de seguridad, restaurarlas y administrar los archivos existentes.'
          },
          side: 'bottom'
        },
        {
          element: '.btn-respaldo-exportar',
          popover: {
            title: 'Generar respaldo',
            description: 'Abre el formulario para crear una copia SQL. Para recorrer sus campos, inicia la guía nuevamente con ese formulario abierto.'
          },
          side: 'left'
        },
        {
          element: '.btn-respaldo-importar',
          popover: {
            title: 'Restaurar respaldo',
            description: 'Abre el formulario para seleccionar un archivo SQL y restaurar la base de datos. Inicia la guía dentro del formulario para recorrer sus controles.'
          },
          side: 'left'
        },
        {
          element: '#tablaRespaldos thead th:nth-child(2)',
          popover: {
            title: 'Nombre de archivo',
            description: 'Identifica cada copia guardada en el sistema.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaRespaldos thead th:nth-child(3)',
          popover: {
            title: 'Fecha de creación',
            description: 'Muestra cuándo fue generado cada respaldo.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaRespaldos thead th:nth-child(4)',
          popover: {
            title: 'Tamaño del archivo',
            description: 'Permite conocer el espacio que ocupa cada copia.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaRespaldos thead th:nth-child(5)',
          popover: {
            title: 'Descripción',
            description: 'Muestra la nota que se agregó para reconocer el respaldo.'
          },
          side: 'bottom'
        },
        {
          element: '#contadorRespaldos',
          popover: {
            title: 'Total de respaldos',
            description: 'Cantidad de copias actualmente registradas.'
          },
          side: 'top'
        }
      ];

      if (document.querySelector('#tbodyRespaldos .btn-ver-respaldo')) {
        steps.push({
            element: '#tbodyRespaldos tr:first-child .btn-ver-respaldo',
            popover: {
              title: 'Ver detalles',
              description: 'Abre la ficha con el nombre, fecha, tamaño y descripción de esta copia.'
            },
            side: 'left'
          });
      }

      if (document.querySelector('#tbodyRespaldos a[href*="/respaldo/descargar/"]')) {
        steps.push({
            element: '#tbodyRespaldos tr:first-child a[href*="/respaldo/descargar/"]',
            popover: {
              title: 'Descargar respaldo',
              description: 'Guarda el archivo SQL seleccionado en tu equipo.'
            },
            side: 'left'
          });
      }

      if (document.querySelector('#tbodyRespaldos .btn-eliminar-respaldo')) {
        steps.push({
            element: '#tbodyRespaldos tr:first-child .btn-eliminar-respaldo',
            popover: {
              title: 'Eliminar respaldo',
              description: 'Abre la confirmación para eliminar esta copia y su archivo.'
            },
            side: 'left'
          });
      }
    }

    return window.driver.js.driver({
      showProgress: true,
      animate: true,
      smoothScroll: false,
      steps: steps
    });
  };
})();
