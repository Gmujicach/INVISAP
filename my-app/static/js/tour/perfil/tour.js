(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['perfil'] = function() {
    return window.driver.js({
      showProgress: true,
      steps: [
        {
          element: '#avatar-preview',
          popover: {
            title: 'Foto de Perfil',
            description: 'Imagen actual de su perfil. Puede cambiarla con el icono de cámara.'
          },
          side: 'right'
        },
        {
          element: '#btn-change-avatar',
          popover: {
            title: 'Cambiar Foto',
            description: 'Seleccione una nueva imagen (PNG, JPG, GIF o WEBP, máx. 5 MB).'
          },
          side: 'top'
        },
        {
          element: '#name_surname',
          popover: {
            title: 'Nombre de Usuario',
            description: 'Edite su nombre de usuario. Mínimo 3 caracteres.'
          },
          side: 'right'
        },
        {
          element: '#email_user',
          popover: {
            title: 'Correo Electrónico',
            description: 'Actualice su correo electrónico asociado a la cuenta.'
          },
          side: 'right'
        },
        {
          element: '#new_pass_user',
          popover: {
            title: 'Cambiar Contraseña',
            description: 'Opcional: ingrese una nueva contraseña (mín. 8 caracteres con un símbolo).'
          },
          side: 'right'
        },
        {
          element: '#repetir_pass_user',
          popover: {
            title: 'Repetir Contraseña',
            description: 'Confirme la nueva contraseña ingresada anteriormente.'
          },
          side: 'right'
        },
        {
          element: '#btn-guardar',
          popover: {
            title: 'Guardar Cambios',
            description: 'Confirme y guarde la información de su perfil.'
          },
          side: 'top'
        }
      ]
    });
  };
})();
