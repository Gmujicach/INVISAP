(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['evidencia'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: 'h1, h2, .card-header-custom',
          popover: {
            title: 'Contexto: Módulo de Evidencias',
            description: 'Suba y gestione evidencias fotográficas por obra. Cada imagen se asigna a una etapa: Antes, Durante o Después.'
          },
          side: 'bottom'
        },
        {
          element: '#dropZone, .drop-zone, .file-drop-zone',
          popover: {
            title: 'Zona de Carga de Imágenes',
            description: 'Arrastre las imágenes fotográficas aquí o haga clic para seleccionarlas desde su equipo. Mínimo 3 y máximo 5 imágenes por registro.'
          },
          side: 'top'
        },
        {
          element: '#fileInput, input[type="file"]',
          popover: {
            title: 'Seleccionar Imágenes',
            description: 'Campo de selección de archivos. Se activa al hacer clic en la zona de carga para elegir las fotos de la obra.'
          },
          side: 'right'
        },
        {
          element: '#imagePreview, .preview-card',
          popover: {
            title: 'Vista Previa de Imágenes',
            description: 'Aquí puede previsualizar las imágenes seleccionadas antes de registrar las evidencias.'
          },
          side: 'top'
        },
        {
          element: '#helpEtapa, .form-label, label',
          popover: {
            title: 'Asignar Etapa a Cada Imagen',
            description: 'Recuerde asignar una etapa a cada imagen: Antes (previa a la obra), Durante (en ejecución) o Después (obra culminada).'
          },
          side: 'top'
        },
        {
          element: '#btnSubir, .btn-primary, button[type="submit"]',
          popover: {
            title: 'Registrar Evidencias',
            description: 'Guarde las evidencias fotográficas en el sistema. El botón se habilita al cumplir los requisitos mínimos de carga.'
          },
          side: 'top'
        }
      ]
    });
  };
})();
