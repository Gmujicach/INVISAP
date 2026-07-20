(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['publicaciones'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: 'button[data-bs-target="#contenedorFormulario"]',
          popover: {
            title: 'Nueva Publicación',
            description: 'Despliega el formulario colapsable para registrar una publicación.'
          },
          side: 'left'
        },
        {
          element: 'table.table',
          popover: {
            title: 'Gestión de Publicaciones',
            description: 'Tabla con todas las publicaciones: título, responsable, tipo, fecha y acciones.'
          },
          side: 'top'
        },
        {
          element: '#contenedorFormulario #titulo_publicacion',
          popover: {
            title: 'Título de la Publicación',
            description: 'Campo obligatorio para nombrar la publicación que se registrará.'
          },
          side: 'top'
        },
        {
          element: '#contenedorFormulario #tipo_publicacion',
          popover: {
            title: 'Tipo de Publicación',
            description: 'Seleccione la categoría: Noticia, Informe, Evento u Otro.'
          },
          side: 'top'
        },
        {
          element: '#contenedorFormulario button[type="submit"]',
          popover: {
            title: 'Guardar Publicación',
            description: 'Registra la publicación con los datos ingresados.'
          },
          side: 'top'
        },
        {
          element: 'table.table tbody tr:first-child .btn-outline-danger',
          popover: {
            title: 'Eliminar Publicación',
            description: 'Elimina la publicación seleccionada previa confirmación.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
