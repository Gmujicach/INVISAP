(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['reportes'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '.card-header-custom, h1, h2',
          popover: {
            title: 'Centro de Reportes',
            description: 'Generacion de informes en Excel, PDF y estadisticas para analizar la informacion del sistema.'
          },
          side: 'bottom'
        },
        {
          element: 'a[href*="excel"], .btn-excel, .card-reporte:first-child',
          popover: {
            title: 'Reporte Excel',
            description: 'Descargue reportes detallados en formato Excel con filtros por fechas y modulos.'
          },
          side: 'top'
        },
        {
          element: 'a[href*="pdf"], .btn-pdf, .card-reporte:nth-child(2)',
          popover: {
            title: 'Reporte PDF',
            description: 'Genere informes ejecutivos en formato PDF listos para presentar o imprimir.'
          },
          side: 'top'
        },
        {
          element: 'a[href*="estadistico"], .btn-estadistico, .card-reporte:nth-child(3)',
          popover: {
            title: 'Reporte Estadistico',
            description: 'Visualice graficos y metricas clave del sistema para toma de decisiones institucional.'
          },
          side: 'top'
        }
      ]
    });
  };
})();
