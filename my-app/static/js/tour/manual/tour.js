(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['manual'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '.card-header-custom, h1, h2',
          popover: {
            title: 'Manual del Sistema INVILARA',
            description: 'Documentacion oficial con guias visuales paso a paso para dominar cada modulo del sistema.'
          },
          side: 'bottom'
        },
        {
          element: '.card-body, .manual-container, #manual-container',
          popover: {
            title: 'Contenido del Manual',
            description: 'Explore las secciones organizadas por modulo. Cada guia incluye capturas de pantalla y procedimientos detallados.'
          },
          side: 'top'
        },
        {
          element: 'a[href*="pdf"], .btn-pdf, .btn-download',
          popover: {
            title: 'Descargar Manual en PDF',
            description: 'Descargue el manual completo en formato PDF para consultas offline o compartir con su equipo.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
