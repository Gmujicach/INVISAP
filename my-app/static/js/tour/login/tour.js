(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['login'] = function() {
    return window.driver.js.driver({
      showProgress: true,
      steps: [
        {
          element: '.authentication-wrapper .auth-cover',
          popover: {
            title: 'Bienvenido a INVILARA',
            description: 'Sistema de gestión integral para el control de solicitudes, proyectos, obras y reportes.'
          },
          side: 'right'
        },
        {
          element: 'input[name="username"], input[name="email"], #username, #email',
          popover: {
            title: 'Correo Electrónico',
            description: 'Ingrese su correo electrónico registrado en el sistema para iniciar sesión.'
          },
          side: 'bottom'
        },
        {
          element: 'input[name="password"], input[name="clave"], #password, #clave',
          popover: {
            title: 'Contraseña',
            description: 'Escriba su contraseña. Si la olvidó, use el enlace de recuperación para recibir un código OTP.'
          },
          side: 'bottom'
        },
        {
          element: 'button[type="submit"].btn-primary, .btn-login',
          popover: {
            title: 'Iniciar Sesión',
            description: 'Una vez completados los campos, haga clic aquí para ingresar al panel de control.'
          },
          side: 'top'
        },
        {
          element: 'a[href*="recovery"], a[href*="clave"], .forgot-link',
          popover: {
            title: 'Recuperar Contraseña',
            description: '¿Olvidó su clave? Haga clic aquí para iniciar el proceso de recuperación vía correo electrónico.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
