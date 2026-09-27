(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['publicaciones'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '.card-header-custom, h1, h2',
          popover: {
            title: 'Contexto: Modulo de Publicaciones',
            description: 'Gestione publicaciones institucionales, noticias y comunicados dirigidos a usuarios y comunidades del sistema.'
          },
          side: 'bottom'
        },
        {
          element: 'a[href*="registrar"], button[data-bs-target*="modal"], .btn-primary, .btn-registrar',
          popover: {
            title: 'Registrar Nueva Publicacion',
            description: 'Abra el formulario para crear una nueva publicacion: titulo, contenido, imagen y estatus de visibilidad.'
          },
          side: 'left'
        },
        {
          element: '#tbl_publicaciones, table.table',
          popover: {
            title: 'Listado de Publicaciones',
            description: 'Lista completa con título, responsable, tipo, estado, fecha y las tres acciones: ver, editar y eliminar.'
          },
          side: 'top'
        },
        {
          element: '#search',
          popover: {
            title: 'Buscar publicación',
            description: 'Escriba para filtrar la tabla en tiempo real por título, responsable o tipo.'
          },
          side: 'bottom'
        },
        {
          element: '#tbl_publicaciones tbody tr:first-child .btn-accion-ver',
          popover: {
            title: 'Botón Ver',
            description: 'Abre la ficha de la publicación con su contenido completo, imagen y datos del responsable.'
          },
          side: 'left'
        },
        {
          element: '#tbl_publicaciones tbody tr:first-child .btn-accion-editar',
          popover: {
            title: 'Botón Editar',
            description: 'Modifique el contenido, imagen o estatus de la publicación. Los cambios se reflejan inmediatamente.'
          },
          side: 'left'
        },
        {
          element: '#tbl_publicaciones tbody tr:first-child .btn-accion-eliminar',
          popover: {
            title: 'Botón Eliminar',
            description: 'Pide confirmación y elimina la publicación por AJAX, sin recargar la página. Use con precaución. Queda registrado en la bitácora.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
