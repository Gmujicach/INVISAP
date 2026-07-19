(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['login'] = function() {
    return window.driver.js({
      showProgress: true,
      steps: [
        {
          element: 'a.btn-back-landing',
          popover: {
            title: 'Volver al Inicio',
            description: 'Regrese a la página principal (landing) del sistema.'
          },
          side: 'right'
        },
        {
          element: '#formAuthentication #nombre',
          popover: {
            title: 'Usuario',
            description: 'Ingrese su nombre de usuario registrado en el sistema.'
          },
          side: 'right'
        },
        {
          element: '#pass_user',
          popover: {
            title: 'Clave de Acceso',
            description: 'Escriba su contraseña. Mínimo 8 caracteres con letras y un símbolo.'
          },
          side: 'right'
        },
        {
          element: '.password-toggle-btn',
          popover: {
            title: 'Mostrar Clave',
            description: 'Alterna la visibilidad de la contraseña mientras la escribe.'
          },
          side: 'left'
        },
        {
          element: 'a[href*="cpanelRecoveryPassUser"]',
          popover: {
            title: '¿Olvidó su Clave?',
            description: 'Acceda a la recuperación de contraseña si no recuerda su clave de acceso.'
          },
          side: 'right'
        },
        {
          element: '.g-recaptcha',
          popover: {
            title: 'Verificación reCAPTCHA',
            description: 'Marque la casilla para confirmar que no es un robot antes de iniciar sesión.'
          },
          side: 'right'
        },
        {
          element: '#formAuthentication button[type="submit"]',
          popover: {
            title: 'Iniciar Sesión',
            description: 'Acceda al panel principal del sistema con sus credenciales.'
          },
          side: 'top'
        }
      ]
    });
  };
})();
