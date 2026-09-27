(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['manual'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '.manual-toolbar .brand',
          popover: {
            title: 'Manual del Sistema INVILARA',
            description: 'Documentación oficial con guías visuales paso a paso para dominar cada módulo del sistema.'
          },
          side: 'bottom'
        },
        {
          element: 'iframe.manual-frame',
          popover: {
            title: 'Contenido del Manual',
            description: 'Aquí se muestra el manual completo. Desplace el contenido con la barra lateral o use los botones de la barra superior para moverse entre páginas.'
          },
          side: 'top'
        },
        {
          element: '.manual-actions a[download]',
          popover: {
            title: 'Descargar Manual en PDF',
            description: 'Descargue el manual completo en formato PDF para consultarlo sin conexión o compartirlo con su equipo.'
          },
          side: 'left'
        },
        {
          element: '.manual-actions button.secondary',
          popover: {
            title: 'Imprimir y cerrar',
            description: 'Use "Imprimir" para generar una copia en papel del manual y "Cerrar" para salir de esta ventana y volver al sistema.'
          },
          side: 'left'
        },
        {
          element: '#btnTourInvilara',
          popover: {
            title: 'Guía interactiva',
            description: 'En cualquier módulo del sistema, este botón verde abre el recorrido guiado que le enseña a registrar, modificar y ver las listas.'
          },
          side: 'top'
        }
      ]
    });
  };
})();
