(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['inf_avance_obra'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '.card-header-custom, h1, h2',
          popover: {
            title: 'Contexto: Informes de Avance de Obra',
            description: 'Registre informes mensuales o periódicos del avance físico de cada obra, con observaciones y soportes.'
          },
          side: 'bottom'
        },
        {
          element: 'a[href*="registrar"], button[data-bs-target*="modal"], .btn-primary, .btn-registrar',
          popover: {
            title: 'Registrar Nuevo Informe',
            description: 'Abra el formulario para crear un informe de avance: seleccione la obra, ingrese porcentaje de avance y agregue observaciones.'
          },
          side: 'left'
        },
        {
          element: '#tablaInformes, table.table',
          popover: {
            title: 'Registro de Informes',
            description: 'Listado de informes registrados: obra, fecha, porcentaje de avance, inspector y observaciones.'
          },
          side: 'top'
        },
        {
          element: '.btn-info, .btn-ver',
          popover: {
            title: 'Ver Informe',
            description: 'Consulte el detalle completo del informe: avance, fotografías, observaciones y firmas registradas.'
          },
          side: 'left'
        },
        {
          element: '.btn-warning, .btn-editar',
          popover: {
            title: 'Editar Informe',
            description: 'Corrija datos del informe: avance porcentual, observaciones o fotografías si es necesario.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
