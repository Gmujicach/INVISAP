(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['evidencia'] = function() {
    return window.driver.js({
      showProgress: true,
      steps: [
        {
          element: '#dropZone',
          popover: {
            title: 'Zona de Carga',
            description: 'Arrastre imágenes aquí o haga clic para seleccionarlas. Mínimo 3 y máximo 5 imágenes por registro.'
          },
          side: 'top'
        },
        {
          element: '#fileInput',
          popover: {
            title: 'Seleccionar Imágenes',
            description: 'Campo oculto que se activa al hacer clic en la zona de carga para elegir las fotos.'
          },
          side: 'right'
        },
        {
          element: '#imagePreview',
          popover: {
            title: 'Vista Previa',
            description: 'Aquí aparecen las imágenes seleccionadas antes de asignarles una etapa.'
          },
          side: 'top'
        },
        {
          element: '#helpEtapa',
          popover: {
            title: 'Asignar Etapas',
            description: 'Recuerde asignar una etapa (Antes, Durante o Después) a cada imagen antes de guardar.'
          },
          side: 'top'
        },
        {
          element: '#btnSubir',
          popover: {
            title: 'Registrar Evidencias',
            description: 'Guarda las evidencias fotográficas. Se habilita al cumplir los requisitos mínimos.'
          },
          side: 'top'
        }
      ]
    });
  };
})();
