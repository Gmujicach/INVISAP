(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['reportes'] = function() {
    const hayEstadistico = !!document.querySelector('#formEstadisticos, #chart1');
    const hayPdf = !!document.querySelector('#moduloPDF, form[action*="PDF" i], form[action*="pdf" i]');
    const hayExcel = !!document.querySelector('#moduloExcel, form[action*="Excel" i], form[action*="excel" i]');

    let steps = [];

    if (hayEstadistico) {
      steps = [
        {
          element: '#tipoReporteEst',
          popover: {
            title: 'Tipo de reporte estadístico',
            description: 'Elija sobre qué módulo quiere el análisis: solicitudes, obras, empleados, contrataciones o publicaciones. Es la fuente de las decisiones institucionales.'
          },
          side: 'bottom'
        },
        {
          element: '#agrupacionEst',
          popover: {
            title: 'Agrupación',
            description: 'Defina cómo se agrupan los datos (por estatus, por municipio, por mes, etc.) para que el gráfico sea legible.'
          },
          side: 'bottom'
        },
        {
          element: '#filtroBusqueda',
          popover: {
            title: 'Filtro rápido',
            description: 'Filtre los resultados por cualquier palabra clave sin salir de la pantalla.'
          },
          side: 'bottom'
        },
        {
          element: '.filtro-estad',
          popover: {
            title: 'Filtros detallados',
            description: 'Aquí puede acotar por solicitante, cédula, correo, municipio, parroquia, rango de fechas y estado. Los campos cambian según el tipo de reporte elegido.'
          },
          side: 'top'
        },
        {
          element: '#chart1, #chart2, #chart3',
          popover: {
            title: 'Gráficos estadísticos',
            description: 'Los gráficos resumen la distribución de los datos. Son el soporte visual para la toma de decisiones del Instituto.'
          },
          side: 'top'
        },
        {
          element: '#btnDescargarPDF',
          popover: {
            title: 'Descargar en PDF',
            description: 'Exporte el reporte estadístico en PDF, listo para presentar o archivar.'
          },
          side: 'left'
        }
      ];
    } else if (hayPdf) {
      steps = [
        {
          element: '#moduloPDF, .card-header, h3, h4',
          popover: {
            title: 'Reporte en PDF',
            description: 'Generación de documentos PDF listos para imprimir o presentar.'
          },
          side: 'bottom'
        },
        {
          element: 'input, select',
          popover: {
            title: 'Filtros del reporte',
            description: 'Elija el módulo y el rango de fechas que se incluirán en el documento. El sistema valida los campos antes de exportar.'
          },
          side: 'top'
        },
        {
          element: 'button[type="submit"]',
          popover: {
            title: 'Generar PDF',
            description: 'Al hacer clic el sistema valida las fechas y los campos obligatorios, y entrega el archivo PDF para descargar.'
          },
          side: 'left'
        }
      ];
    } else if (hayExcel) {
      steps = [
        {
          element: '#moduloExcel, .card-header, h3, h4',
          popover: {
            title: 'Reporte en Excel',
            description: 'Exportación de los datos del sistema a formato .xlsx para su análisis en hoja de cálculo.'
          },
          side: 'bottom'
        },
        {
          element: 'input, select',
          popover: {
            title: 'Filtros de la exportación',
            description: 'Elija el módulo y el rango de fechas. El sistema valida que las fechas sean correctas antes de exportar.'
          },
          side: 'top'
        },
        {
          element: 'button[type="submit"]',
          popover: {
            title: 'Descargar Excel',
            description: 'Al hacer clic se genera el archivo .xlsx con los registros filtrados y se descarga de inmediato.'
          },
          side: 'left'
        }
      ];
    } else {
      steps = [
        {
          element: '#btnTourInvilara, .tour-fab',
          popover: {
            title: 'Centro de Reportes',
            description: 'Desde el menú lateral puede generar reportes en Excel, PDF y estadísticos. Abra cualquiera de ellos para iniciar este recorrido guiado.'
          },
          side: 'left'
        }
      ];
    }

    steps.push({
      element: '#btnTourInvilara, .tour-fab',
      popover: {
        title: 'Guía interactiva del sistema',
        description: 'Este botón verde está disponible en todos los módulos y le muestra, paso a paso, cómo registrar, modificar y ver las listas.'
      },
      side: 'top'
    });

    return window.driver.js.driver({
      showProgress: true,
      steps: steps
    });
  };
})();
