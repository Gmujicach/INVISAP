(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['usuarios'] = function() {
    const path = window.location.pathname || '';
    const isRegisterPage = path.indexOf('/users/register') !== -1 || !!document.querySelector('#formRegisterUser');
    const isEditPage = path.indexOf('/users/edit/') !== -1 || !!document.querySelector('#formUpdateUser');
    const isListPage = path.indexOf('/users') !== -1 && !isRegisterPage && !isEditPage || !!document.querySelector('#tablaUsuarios, #respuestaFiltroMes');

    const steps = [];

    if (isListPage) {
      steps.push(
        {
          element: '#respuestaFiltroMes h2',
          popover: {
            title: 'Listado de Usuarios',
            description: 'Aquí puedes ver todos los usuarios registrados en el sistema. Puedes buscarlos, editarlos o eliminarlos desde esta tabla.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaUsuarios',
          popover: {
            title: 'Tabla de Usuarios',
            description: 'Cada fila representa una cuenta de acceso. Incluye avatar, nombre, cédula, correo, rol y botones de acción.'
          },
          side: 'top'
        },
        {
          element: '#tablaUsuarios thead th:nth-child(1)',
          popover: {
            title: 'Columna Avatar',
            description: 'Muestra la foto de perfil del usuario. Si no tiene imagen, se muestra un avatar genérico por defecto.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaUsuarios thead th:nth-child(2)',
          popover: {
            title: 'Columna Nombre',
            description: 'Muestra el nombre completo del usuario tal como fue registrado.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaUsuarios thead th:nth-child(3)',
          popover: {
            title: 'Columna Cédula',
            description: 'Es el número de identidad del usuario. Se usa como dato de referencia y validación.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaUsuarios thead th:nth-child(4)',
          popover: {
            title: 'Columna Correo',
            description: 'Correo electrónico del usuario. Sirve para notificaciones y recuperación de acceso.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaUsuarios thead th:nth-child(5)',
          popover: {
            title: 'Columna Rol',
            description: 'Indica el nivel de acceso del usuario: Super Usuario, Administrador, Gerente, Inspector, etc. Cada rol tiene permisos diferentes.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaUsuarios thead th:nth-child(6)',
          popover: {
            title: 'Columna Acciones',
            description: 'Aquí puedes editar la información del usuario o eliminarlo si ya no debe tener acceso al sistema.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaUsuarios tbody tr:first-child .btn-warning',
          popover: {
            title: 'Botón Editar',
            description: 'Haz clic para modificar los datos del usuario: nombre, correo, rol y contraseña. Los cambios se guardan al enviar el formulario.'
          },
          side: 'left'
        },
        {
          element: '#tablaUsuarios tbody tr:first-child .btn-danger',
          popover: {
            title: 'Botón Eliminar',
            description: 'Elimina al usuario de forma permanente tras confirmar. Ten cuidado porque esta acción no se puede deshacer.'
          },
          side: 'left'
        },
        {
          element: '#respuestaFiltroMes .btn-primary',
          popover: {
            title: 'Registrar Nuevo Usuario',
            description: 'Haz clic aquí para abrir el formulario y agregar un nuevo usuario al sistema. Podrás ingresar su nombre, cédula, correo, rol y contraseña.'
          },
          side: 'left'
        }
      );
    } else if (isRegisterPage) {
      steps.push(
        {
          element: '.card-header h4',
          popover: {
            title: 'Formulario de Registro',
            description: 'Completa todos los campos para crear una nueva cuenta de usuario en el sistema. Los campos marcados como obligatorios deben llenarse sí o sí.'
          },
          side: 'bottom'
        },
        {
          element: 'input[name="nombre"]',
          popover: {
            title: 'Nombre y Apellido',
            description: 'Escribe el nombre completo del usuario. Ejemplo: Juan Carlos Pérez González. Solo letras y espacios.'
          },
          side: 'right'
        },
        {
          element: 'input[name="cedula_usuario"]',
          popover: {
            title: 'Cédula',
            description: 'Ingresa el número de cédula del usuario. Debe tener hasta 10 dígitos numéricos. Este dato es único.'
          },
          side: 'right'
        },
        {
          element: 'input[name="correo"]',
          popover: {
            title: 'Correo Electrónico',
            description: 'Escribe el correo del usuario. Debe ser una dirección válida como usuario@dominio.com.'
          },
          side: 'right'
        },
        {
          element: 'select[name="rol"]',
          popover: {
            title: 'Rol',
            description: 'Selecciona el nivel de acceso que tendrá el usuario: Asistente, Recepcionista, Gerente, Presidente, Administrador, Proyectista o Inspector.'
          },
          side: 'right'
        },
        {
          element: 'input[name="pass_user"]',
          popover: {
            title: 'Contraseña',
            description: 'Crea una contraseña segura. Debe tener entre 8 y 12 caracteres, al menos una letra y un símbolo especial. Ejemplo: Inv1lara#2026.'
          },
          side: 'right'
        },
        {
          element: 'button[type="submit"]',
          popover: {
            title: 'Registrar Usuario',
            description: 'Haz clic aquí para guardar el nuevo usuario. El sistema validará los datos y te confirmará si se creó correctamente.'
          },
          side: 'left'
        },
        {
          element: 'a[href*="list_users"], .btn-secondary',
          popover: {
            title: 'Botón Cancelar',
            description: 'Si haces clic aquí, regresarás al listado de usuarios sin guardar ningún dato.'
          },
          side: 'left'
        }
      );
    } else if (isEditPage) {
      steps.push(
        {
          element: '.card-header h4',
          popover: {
            title: 'Modificar Usuario',
            description: 'En esta página puedes actualizar los datos del usuario seleccionado. Los cambios se guardan al hacer clic en Modificar Usuario.'
          },
          side: 'bottom'
        },
        {
          element: 'input[name="nombre"]',
          popover: {
            title: 'Nombre y Apellido',
            description: 'Modifica el nombre del usuario si es necesario. Recuerda usar solo letras y espacios.'
          },
          side: 'right'
        },
        {
          element: 'input[name="cedula_usuario"]',
          popover: {
            title: 'Cédula',
            description: 'Corrige el número de cédula si estaba incorrecto. Hasta 10 dígitos numéricos.'
          },
          side: 'right'
        },
        {
          element: 'input[name="correo"]',
          popover: {
            title: 'Correo Electrónico',
            description: 'Actualiza el correo electrónico si el usuario cambió de dirección de correo.'
          },
          side: 'right'
        },
        {
          element: 'select[name="rol"]',
          popover: {
            title: 'Rol',
            description: 'Cambia el nivel de acceso del usuario si fue reasignado a otro cargo. Ejemplo: de Asistente a Gerente.'
          },
          side: 'right'
        },
        {
          element: 'input[name="pass_user"]',
          popover: {
            title: 'Nueva Contraseña (Opcional)',
            description: 'Solo escribe algo aquí si deseas cambiar la contraseña actual. Si lo dejas vacío, la contraseña se mantiene igual.'
          },
          side: 'right'
        },
        {
          element: 'button[type="submit"]',
          popover: {
            title: 'Modificar Usuario',
            description: 'Haz clic aquí para guardar los cambios realizados. El sistema confirmará cuando se hayan actualizado los datos.'
          },
          side: 'left'
        },
        {
          element: 'a[href*="list_users"], .btn-secondary',
          popover: {
            title: 'Botón Volver',
            description: 'Regresa al listado de usuarios sin guardar los cambios realizados.'
          },
          side: 'left'
        }
      );
    }

    return window.driver.js.driver({
      showProgress: true,
      nextBtnText: 'Siguiente',
      prevBtnText: 'Anterior',
      doneBtnText: 'Entendido',
      steps: steps.length ? steps : [
        {
          element: '#btnTourInvilara, .tour-fab, .btn-primary',
          popover: {
            title: 'Guía del módulo de Usuarios',
            description: 'Usa esta guía para aprender a registrar, listar y modificar usuarios en el sistema.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
