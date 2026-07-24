(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['proyectos'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '#contador-total, .badge, .counter',
          popover: {
            title: 'Contexto: Módulo de Proyectos',
            description: 'Aquí gestiona todos los proyectos derivados de las solicitudes aprobadas del sistema.'
          },
          side: 'bottom'
        },
        {
          element: 'button[data-bs-target="#modalRegistrarProyecto"], .btn-primary, .btn-registrar',
          popover: {
            title: 'Registrar Nuevo Proyecto',
            description: 'Abra el formulario para crear un proyecto. Seleccione la solicitud aprobada, asigne proyectista, fechas y presupuesto estimado.'
          },
          side: 'left'
        },
        {
          element: '#search, .form-control[type="search"], input[type="search"]',
          popover: {
            title: 'Búsqueda Rápida',
            description: 'Filtre proyectos por código, solicitante, descripción o estatus en tiempo real.'
          },
          side: 'bottom'
        },
        {
          element: 'table.table',
          popover: {
            title: 'Listado de Proyectos',
            description: 'Tabla completa con código, solicitante, descripción técnica, maquinaria asignada, estatus de costo, fechas y acciones.'
          },
          side: 'top'
        },
        {
          element: 'table.table thead th:nth-child(1), table.table thead th:first-child',
          popover: {
            title: 'Código / Identificador',
            description: 'Código único del proyecto para identificarlo rápidamente en todo el sistema.'
          },
          side: 'bottom'
        },
        {
          element: 'table.table tbody tr:first-child .btn-outline-info, .btn-info, .btn-ver',
          popover: {
            title: 'Ver Detalle del Proyecto',
            description: 'Consulte el resumen completo: fechas de inicio y fin, maquinaria asignada, proyectista responsable y observaciones.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
