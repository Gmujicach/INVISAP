(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['evidencia'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: 'h1, h2, .card-header-custom',
          popover: {
            title: 'Contexto: Modulo de Evidencias',
            description: 'Suba y gestione evidencias fotograficas por obra. Cada imagen se asigna a una etapa: Antes, Durante o Despues.'
          },
          side: 'bottom'
        },
        {
          element: '#dropZone, .drop-zone, .file-drop-zone',
          popover: {
            title: 'Zona de Carga de Imagenes',
            description: 'Arrastre las imagenes fotograficas aqui o haga clic para seleccionarlas desde su equipo. Minimo 3 y maximo 5 imagenes por registro.'
          },
          side: 'top'
        },
        {
          element: '#fileInput, input[type="file"]',
          popover: {
            title: 'Seleccionar Imagenes',
            description: 'Campo de seleccion de archivos. Se activa al hacer clic en la zona de carga para elegir las fotos de la obra.'
          },
          side: 'right'
        },
        {
          element: '#imagePreview, .preview-card',
          popover: {
            title: 'Vista Previa de Imagenes',
            description: 'Aqui puede previsualizar las imagenes seleccionadas antes de registrar las evidencias.'
          },
          side: 'top'
        },
        {
          element: '#helpEtapa, .form-label, label',
          popover: {
            title: 'Asignar Etapa a Cada Imagen',
            description: 'Recuerde asignar una etapa a cada imagen: Antes (previa a la obra), Durante (en ejecucion) o Despues (obra culminada).'
          },
          side: 'top'
        },
        {
          element: '#btnSubir, .btn-primary, button[type="submit"]',
          popover: {
            title: 'Registrar Evidencias',
            description: 'Guarde las evidencias fotograficas en el sistema. El boton se habilita al cumplir los requisitos minimos de carga.'
          },
          side: 'top'
        }
      ]
    });
  };
})();
