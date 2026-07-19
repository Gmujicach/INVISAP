(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['respaldo'] = function() {
    return window.driver.js({
      showProgress: true,
      steps: [
        {
          element: 'button[data-bs-target="#modalExportarRespaldo"]',
          popover: {
            title: 'Generar Respaldo',
            description: 'Cree un archivo .sql completo de la base de datos con una descripción opcional.'
          },
          side: 'left'
        },
        {
          element: 'button[data-bs-target="#modalImportarRespaldo"]',
          popover: {
            title: 'Restaurar Respaldo',
            description: 'Importe un archivo .sql válido para restaurar la base de datos. ¡Cuidado, sobrescribe los datos!'
          },
          side: 'left'
        },
        {
          element: '#tablaRespaldos',
          popover: {
            title: 'Respaldos Registrados',
            description: 'Tabla con los archivos de respaldo: nombre, fecha, tamaño y descripción.'
          },
          side: 'top'
        },
        {
          element: '#tablaRespaldos tbody tr:first-child .btn-outline-success',
          popover: {
            title: 'Descargar Respaldo',
            description: 'Descargue el archivo .sql del respaldo seleccionado.'
          },
          side: 'left'
        },
        {
          element: '#tablaRespaldos tbody tr:first-child .btn-eliminar-respaldo',
          popover: {
            title: 'Eliminar Respaldo',
            description: 'Elimina el respaldo y su archivo físico previa confirmación.'
          },
          side: 'left'
        },
        {
          element: '#contadorRespaldos',
          popover: {
            title: 'Total de Respaldos',
            description: 'Cantidad total de respaldos disponibles en el sistema.'
          },
          side: 'bottom'
        }
      ]
    });
  };
})();
