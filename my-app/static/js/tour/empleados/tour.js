(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['empleados'] = function() {
    return window.driver.js({
      showProgress: true,
      steps: [
        {
          element: 'a.btn.btn-primary',
          popover: {
            title: 'Registrar Nuevo Empleado',
            description: 'Haga clic aquí para abrir el formulario de registro de un nuevo empleado en el sistema.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaEmpleados',
          popover: {
            title: 'Listado de Empleados',
            description: 'Tabla principal con todo el personal registrado: nombre, cargo, gerencia, ingreso y estado.'
          },
          side: 'top'
        },
        {
          element: '#tablaEmpleados thead th:nth-child(3)',
          popover: {
            title: 'Cargo',
            description: 'Columna que indica el cargo desempeñado por cada empleado dentro de la organización.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaEmpleados thead th:nth-child(6)',
          popover: {
            title: 'Estado',
            description: 'Muestra si el empleado está Activo o Inactivo en el sistema.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaEmpleados tbody tr:first-child .btn-warning',
          popover: {
            title: 'Editar Empleado',
            description: 'Use este botón para modificar los datos de un empleado existente.'
          },
          side: 'left'
        },
        {
          element: '#tablaEmpleados tbody tr:first-child .btn-danger',
          popover: {
            title: 'Eliminar Empleado',
            description: 'Realiza un borrado lógico del empleado. El registro queda inactivo pero se conserva en la base de datos.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
