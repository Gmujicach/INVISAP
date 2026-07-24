(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['empleados'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: 'a.btn.btn-primary, .btn-registrar',
          popover: {
            title: 'Contexto: Modulo de Empleados',
            description: 'Gestione el personal de la organizacion: registro, actualizacion y control de estado (activo/inactivo).'
          },
          side: 'left'
        },
        {
          element: '#tablaEmpleados, table.table',
          popover: {
            title: 'Listado de Empleados',
            description: 'Directorio completo con nombre, cargo, gerencia, fecha de ingreso y estado de cada empleado.'
          },
          side: 'top'
        },
        {
          element: '#tablaEmpleados thead th:nth-child(3)',
          popover: {
            title: 'Columna Cargo',
            description: 'Indica el puesto o cargo desempenado por cada empleado dentro de la estructura organizacional.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaEmpleados thead th:nth-child(6)',
          popover: {
            title: 'Columna Estado',
            description: 'Muestra si el empleado esta Activo o Inactivo en el sistema. Solo los empleados activos pueden ser asignados a proyectos.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaEmpleados tbody tr:first-child .btn-warning, .btn-warning, .btn-editar',
          popover: {
            title: 'Editar Empleado',
            description: 'Modifique datos del empleado: cargo, gerencia, telefono o estado. Los cambios se reflejan inmediatamente.'
          },
          side: 'left'
        },
        {
          element: '#tablaEmpleados tbody tr:first-child .btn-danger, .btn-danger, .btn-eliminar',
          popover: {
            title: 'Eliminar Empleado (Borrado Logico)',
            description: 'Inhabilita el empleado sin borrarlo permanentemente. El registro queda inactivo para auditoria pero no aparece en listados activos.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
