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
            description: 'Sistema de gestion integral para el control de solicitudes, proyectos, obras y reportes.'
          },
          side: 'right'
        },
        {
          element: 'input[name="username"], input[name="email"], #username, #email',
          popover: {
            title: 'Correo Electronico',
            description: 'Ingrese su correo electronico registrado en el sistema para iniciar sesion.'
          },
          side: 'bottom'
        },
        {
          element: 'input[name="password"], input[name="clave"], #password, #clave',
          popover: {
            title: 'Contrasena',
            description: 'Escriba su contrasena. Si la olvido, use el enlace de recuperacion para recibir un codigo OTP.'
          },
          side: 'bottom'
        },
        {
          element: 'button[type="submit"].btn-primary, .btn-login',
          popover: {
            title: 'Iniciar Sesion',
            description: 'Una vez completados los campos, haga clic aqui para ingresar al panel de control.'
          },
          side: 'top'
        },
        {
          element: 'a[href*="recovery"], a[href*="clave"], .forgot-link',
          popover: {
            title: 'Recuperar Contrasena',
            description: '¿Olvido su clave? Haga clic aqui para iniciar el proceso de recuperacion via correo electronico.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
