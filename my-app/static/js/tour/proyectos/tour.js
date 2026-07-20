(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['proyectos'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '#contador-total',
          popover: {
            title: 'Registros Totales',
            description: 'Muestra la cantidad total de proyectos gestionados en el sistema.'
          },
          side: 'bottom'
        },
        {
          element: 'button[data-bs-target="#modalRegistrarProyecto"]',
          popover: {
            title: 'Registrar Proyecto',
            description: 'Abra el formulario para crear un nuevo proyecto, asociándolo a una solicitud pendiente si lo desea.'
          },
          side: 'left'
        },
        {
          element: 'table.table',
          popover: {
            title: 'Tabla de Proyectos',
            description: 'Listado general de proyectos con su código, solicitante, descripción técnica, maquinaria y estatus de costo.'
          },
          side: 'top'
        },
        {
          element: 'table.table thead th:nth-child(11)',
          popover: {
            title: 'Acciones por Proyecto',
            description: 'Desde aquí puede ver el detalle, editar o eliminar cada proyecto registrado.'
          },
          side: 'left'
        },
        {
          element: 'table.table tbody tr:first-child .btn-outline-info',
          popover: {
            title: 'Ver Detalle',
            description: 'Muestra el resumen completo del proyecto: fechas, maquinaria, proyectista y observaciones.'
          },
          side: 'left'
        },
        {
          element: 'table.table tbody tr:first-child .btn-outline-danger',
          popover: {
            title: 'Eliminar Proyecto',
            description: 'Elimina el proyecto previa confirmación. Use con precaución.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
