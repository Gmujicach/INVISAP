(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['publicaciones'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '.card-header-custom, h1, h2',
          popover: {
            title: 'Contexto: Módulo de Publicaciones',
            description: 'Gestione publicaciones institucionales, noticias y comunicados dirigidos a usuarios y comunidades del sistema.'
          },
          side: 'bottom'
        },
        {
          element: 'a[href*="registrar"], button[data-bs-target*="modal"], .btn-primary, .btn-registrar',
          popover: {
            title: 'Registrar Nueva Publicación',
            description: 'Abra el formulario para crear una nueva publicación: título, contenido, imagen y estatus de visibilidad.'
          },
          side: 'left'
        },
        {
          element: '#lista-publicaciones, #tablaPublicaciones, table.table',
          popover: {
            title: 'Listado de Publicaciones',
            description: 'Lista completa con título, autor, fecha de publicación, estatus y acciones disponibles.'
          },
          side: 'top'
        },
        {
          element: '.btn-warning, .btn-editar',
          popover: {
            title: 'Editar Publicación',
            description: 'Modifique el contenido, imagen o estatus de la publicación. Los cambios se reflejan inmediatamente en el sitio.'
          },
          side: 'left'
        },
        {
          element: '.btn-danger, .btn-eliminar',
          popover: {
            title: 'Eliminar Publicación',
            description: 'Elimina la publicación previa confirmación. Use con precaución.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
