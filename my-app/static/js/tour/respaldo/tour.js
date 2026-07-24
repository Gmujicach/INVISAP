(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['respaldo'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: 'h1, h2, .card-header-custom',
          popover: {
            title: 'Administracion de Respaldos',
            description: 'Gestione copias de seguridad de la base de datos y descargue archivos SQL para respaldo externo.'
          },
          side: 'bottom'
        },
        {
          element: '.card-respaldo, .card-body',
          popover: {
            title: 'Respaldos Disponibles',
            description: 'Listado de respaldos generados con fecha, tamano y opciones de descarga.'
          },
          side: 'top'
        },
        {
          element: 'a[href*="download"], .btn-download, .btn-descargar',
          popover: {
            title: 'Descargar Respaldo',
            description: 'Descargue el archivo .sql de respaldo a su equipo local para almacenamiento seguro.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
