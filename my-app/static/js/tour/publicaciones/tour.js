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
          element: '#lista-publicaciones, #tablaPublicaciones, table.table',
          popover: {
            title: 'Listado de Publicaciones',
            description: 'Lista completa con titulo, autor, fecha de publicacion, estatus y acciones disponibles.'
          },
          side: 'top'
        },
        {
          element: '.btn-warning, .btn-editar',
          popover: {
            title: 'Editar Publicacion',
            description: 'Modifique el contenido, imagen o estatus de la publicacion. Los cambios se reflejan inmediatamente en el sitio.'
          },
          side: 'left'
        },
        {
          element: '.btn-danger, .btn-eliminar',
          popover: {
            title: 'Eliminar Publicacion',
            description: 'Elimina la publicacion previa confirmacion. Use con precaucion.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
