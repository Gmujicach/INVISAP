(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['manual'] = function() {
    return window.driver.js({
      showProgress: true,
      steps: [
        {
          element: '.manual-toolbar .brand',
          popover: {
            title: 'Manual del Sistema',
            description: 'Barra superior con el título del manual interactivo de INVILARA.'
          },
          side: 'bottom'
        },
        {
          element: '.manual-actions a[download]',
          popover: {
            title: 'Descargar',
            description: 'Descargue el manual completo en formato PDF a su equipo.'
          },
          side: 'bottom'
        },
        {
          element: '.manual-actions button[onclick*="print"]',
          popover: {
            title: 'Imprimir',
            description: 'Envíe el manual a impresión desde el navegador.'
          },
          side: 'bottom'
        },
        {
          element: '.manual-actions button[onclick*="close"]',
          popover: {
            title: 'Cerrar',
            description: 'Cierre la ventana del manual cuando termine de consultarlo.'
          },
          side: 'bottom'
        },
        {
          element: '.manual-frame',
          popover: {
            title: 'Visor del Manual',
            description: 'Aquí se muestra el documento PDF embebido para su lectura.'
          },
          side: 'top'
        }
      ]
    });
  };
})();
