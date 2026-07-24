(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['empresas'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '#columnaBusqueda, select[name="columna"]',
          popover: {
            title: 'Contexto: Directorio de Empresas',
            description: 'Administre las empresas registradas para procesos de contratación, contactos y facturación en el sistema.'
          },
          side: 'bottom'
        },
        {
          element: '#customBuscador, .form-control[type="search"], input[type="search"]',
          popover: {
            title: 'Buscador Inteligente',
            description: 'Filtre por RIF, nombre de empresa, teléfono o domicilio fiscal. Primero seleccione la columna, luego escriba.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaEmpresas, table.table',
          popover: {
            title: 'Directorio de Empresas',
            description: 'Listado con RIF, nombre comercial, teléfono de contacto y domicilio fiscal de todas las empresas.'
          },
          side: 'top'
        },
        {
          element: '#tablaEmpresas tbody tr:first-child .btn-warning, .btn-warning, .btn-editar',
          popover: {
            title: 'Editar Empresa',
            description: 'Actualice datos de la empresa seleccionada: teléfono, dirección o información de contacto.'
          },
          side: 'left'
        },
        {
          element: '#tablaEmpresas tbody tr:first-child .btn-eliminar, .btn-danger, .btn-eliminar',
          popover: {
            title: 'Eliminar Empresa',
            description: 'Elimina la empresa del directorio. Se solicita confirmación antes de proceder para evitar pérdidas accidentales.'
          },
          side: 'left'
        },
        {
          element: '#paginacionContenedor, .pagination',
          popover: {
            title: 'Paginación',
            description: 'Navegue entre las páginas del directorio y consulte la cantidad total de empresas registradas en el sistema.'
          },
          side: 'top'
        }
      ]
    });
  };
})();
