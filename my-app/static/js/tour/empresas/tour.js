(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['empresas'] = function() {
    return window.driver.js({
      showProgress: true,
      steps: [
        {
          element: '#columnaBusqueda',
          popover: {
            title: 'Filtro por Columna',
            description: 'Seleccione el criterio de búsqueda: RIF, Empresa, Teléfono o Domicilio Fiscal antes de escribir.'
          },
          side: 'bottom'
        },
        {
          element: '#customBuscador',
          popover: {
            title: 'Buscador de Empresas',
            description: 'Escriba aquí el término a buscar. La tabla se filtra automáticamente según la columna seleccionada.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaEmpresas',
          popover: {
            title: 'Directorio de Empresas',
            description: 'Listado de todas las empresas registradas con su RIF, nombre, teléfono y domicilio fiscal.'
          },
          side: 'top'
        },
        {
          element: '#tablaEmpresas tbody tr:first-child .btn-warning',
          popover: {
            title: 'Editar Empresa',
            description: 'Modifique los datos de la empresa seleccionada.'
          },
          side: 'left'
        },
        {
          element: '#tablaEmpresas tbody tr:first-child .btn-eliminar',
          popover: {
            title: 'Eliminar Empresa',
            description: 'Elimina la empresa del directorio. Se solicita confirmación antes de proceder.'
          },
          side: 'left'
        },
        {
          element: '#paginacionContenedor',
          popover: {
            title: 'Paginación',
            description: 'Navegue entre las páginas del directorio y consulte la cantidad total de empresas registradas.'
          },
          side: 'top'
        }
      ]
    });
  };
})();
