(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['inf_avance_obra'] = function() {
    return window.driver.js({
      showProgress: true,
      steps: [
        {
          element: 'button[data-bs-target="#modalRegistrarInforme"]',
          popover: {
            title: 'Registrar Informe',
            description: 'Abra el formulario para crear un nuevo informe de avance de obra.'
          },
          side: 'left'
        },
        {
          element: '.card-estadistica.bg-light',
          popover: {
            title: 'Total de Informes',
            description: 'Indicador con la cantidad total de informes registrados en el sistema.'
          },
          side: 'bottom'
        },
        {
          element: '.card-estadistica.card-aprobados',
          popover: {
            title: 'Aprobados',
            description: 'Cantidad de informes con estado Aprobado.'
          },
          side: 'bottom'
        },
        {
          element: '.card-estadistica.bg-warning',
          popover: {
            title: 'En Ejecución',
            description: 'Informes correspondientes a obras actualmente en ejecución.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaInformes',
          popover: {
            title: 'Tabla de Informes',
            description: 'Listado con tipo, estado, población beneficiada, porcentaje de avance y responsable.'
          },
          side: 'top'
        },
        {
          element: '#tablaInformes tbody tr:first-child .btn-ver-informe',
          popover: {
            title: 'Ver Detalle',
            description: 'Abre el resumen completo del informe, incluyendo evidencias por etapa.'
          },
          side: 'left'
        },
        {
          element: '#tablaInformes tbody tr:first-child .btn-eliminar-informe',
          popover: {
            title: 'Eliminar Informe',
            description: 'Borrado lógico del informe tras confirmación.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
