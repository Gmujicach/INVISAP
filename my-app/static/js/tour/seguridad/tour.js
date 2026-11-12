(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['seguridad'] = function() {
    const activeTab = document.querySelector('#seguridadTabs .nav-link.active');
    const roleModalOpen = !!document.querySelector('#modalRol.show');
    const moduleModalOpen = !!document.querySelector('#modalModulo.show');
    let steps = [];

    if (roleModalOpen) {
      steps = [
        {
          element: '#nombre_rol',
          popover: {
            title: 'Nombre del rol',
            description: 'Escribe un nombre claro para identificar el cargo. Debe tener entre 3 y 20 letras o espacios.'
          },
          side: 'bottom'
        },
        {
          element: '#descripcion_rol',
          popover: {
            title: 'Descripción del rol',
            description: 'Describe brevemente las responsabilidades de las personas que tendrán este rol.'
          },
          side: 'bottom'
        },
        {
          element: '#estado_rol',
          popover: {
            title: 'Estado del rol',
            description: 'Activa o desactiva el rol para controlar si puede asignarse y utilizarse.'
          },
          side: 'right'
        },
        {
          element: '#btnGuardarRol',
          popover: {
            title: 'Guardar rol',
            description: 'Registra el rol nuevo o guarda los cambios del rol que estás editando.'
          },
          side: 'top'
        }
      ];
    } else if (moduleModalOpen) {
      steps = [
        {
          element: '#nombre_modulo',
          popover: {
            title: 'Clave del módulo',
            description: 'Escribe la clave interna del módulo. Debe coincidir con la clave usada por el control de permisos.'
          },
          side: 'bottom'
        },
        {
          element: '#url_modulo',
          popover: {
            title: 'URL del menú',
            description: 'Indica la ruta de acceso del módulo. Esta dirección no podrá modificarse después de crearlo.'
          },
          side: 'bottom'
        },
        {
          element: '#tipo_modulo',
          popover: {
            title: 'Tipo de módulo',
            description: 'Selecciona si el módulo ofrece operaciones CRUD, es transaccional o funciona como enlace.'
          },
          side: 'bottom'
        },
        {
          element: '.icon-picker-dropdown > button',
          popover: {
            title: 'Ícono del módulo',
            description: 'Abre el selector para elegir el ícono que identificará al módulo en el menú.'
          },
          side: 'bottom'
        },
        {
          element: '#orden_modulo',
          popover: {
            title: 'Orden en el menú',
            description: 'Define la posición en la que aparecerá este módulo dentro del menú.'
          },
          side: 'bottom'
        },
        {
          element: '#descripcion_modulo',
          popover: {
            title: 'Descripción del módulo',
            description: 'Agrega una explicación breve de las funciones de este módulo.'
          },
          side: 'top'
        },
        {
          element: '#estado_modulo',
          popover: {
            title: 'Estado del módulo',
            description: 'Activa o desactiva la disponibilidad del módulo.'
          },
          side: 'right'
        },
        {
          element: '#btnGuardarModulo',
          popover: {
            title: 'Guardar módulo',
            description: 'Registra el nuevo módulo o guarda los cambios realizados.'
          },
          side: 'top'
        }
      ];
    } else if (activeTab && activeTab.id === 'tab-roles') {
      steps = [
        {
          element: '#tab-roles',
          popover: {
            title: 'Pestaña Roles',
            description: 'Aquí buscas, registras y administras los cargos que luego reciben permisos.'
          },
          side: 'bottom'
        },
        {
          element: '#buscarRol',
          popover: {
            title: 'Buscar rol',
            description: 'Filtra la tabla por nombre o descripción para encontrar un rol rápidamente.'
          },
          side: 'bottom'
        },
        {
          element: '#contadorRoles',
          popover: {
            title: 'Cantidad de roles',
            description: 'Muestra cuántos roles están registrados.'
          },
          side: 'left'
        },
        {
          element: '#pane-roles .seguridad-filter-card button[data-bs-target="#modalRol"]',
          popover: {
            title: 'Nuevo rol',
            description: 'Abre el formulario para crear un rol. Inicia de nuevo la guía con el formulario abierto para recorrer sus campos.'
          },
          side: 'left'
        },
        {
          element: '#tablaRoles thead th:nth-child(1)',
          popover: {
            title: 'Identificador del rol',
            description: 'Número único que el sistema asigna al rol.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaRoles thead th:nth-child(2)',
          popover: {
            title: 'Nombre del rol',
            description: 'Nombre que identifica el cargo dentro del sistema.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaRoles thead th:nth-child(3)',
          popover: {
            title: 'Descripción',
            description: 'Resumen de las responsabilidades asociadas al rol.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaRoles thead th:nth-child(4)',
          popover: {
            title: 'Estado del rol',
            description: 'Indica si el rol está activo o inactivo.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaRoles thead th:nth-child(5)',
          popover: {
            title: 'Acciones del rol',
            description: 'Desde cada fila puedes consultar, editar o eliminar el rol.'
          },
          side: 'bottom'
        }
      ];

      if (document.querySelector('#cuerpoRoles .btn-accion-ver')) {
        steps.push(
          {
            element: '#cuerpoRoles tr:first-child .btn-accion-ver',
            popover: {
              title: 'Ver rol',
              description: 'Abre el detalle del rol en modo de solo lectura.'
            },
            side: 'left'
          },
          {
            element: '#cuerpoRoles tr:first-child .btn-accion-editar',
            popover: {
              title: 'Editar rol',
              description: 'Abre el formulario para actualizar el nombre, descripción o estado del rol.'
            },
            side: 'left'
          },
          {
            element: '#cuerpoRoles tr:first-child .btn-accion-eliminar',
            popover: {
              title: 'Eliminar rol',
              description: 'Inicia la eliminación del rol seleccionado.'
            },
            side: 'left'
          }
        );
      }
    } else if (activeTab && activeTab.id === 'tab-modulos') {
      steps = [
        {
          element: '#tab-modulos',
          popover: {
            title: 'Pestaña Módulos',
            description: 'Aquí se administran las secciones disponibles en el sistema. Para recorrer Roles o Asignar Permisos, abre esa pestaña e inicia la guía de nuevo.'
          },
          side: 'bottom'
        },
        {
          element: '#buscarModulo',
          popover: {
            title: 'Buscar módulo',
            description: 'Filtra la tabla por clave, URL, tipo o estado del módulo.'
          },
          side: 'bottom'
        },
        {
          element: '#contadorModulos',
          popover: {
            title: 'Cantidad de módulos',
            description: 'Muestra cuántos módulos están listados.'
          },
          side: 'left'
        },
        {
          element: '#pane-modulos .seguridad-filter-card button[data-bs-target="#modalModulo"]',
          popover: {
            title: 'Nuevo módulo',
            description: 'Abre el formulario para registrar una sección del sistema y definir sus datos.'
          },
          side: 'left'
        },
        {
          element: '#tablaModulos thead th:nth-child(1)',
          popover: {
            title: 'Identificador del módulo',
            description: 'Número único que el sistema asigna al módulo.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaModulos thead th:nth-child(2)',
          popover: {
            title: 'Clave',
            description: 'Identificador interno del módulo, utilizado para asociar permisos.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaModulos thead th:nth-child(3)',
          popover: {
            title: 'URL',
            description: 'Ruta que abre el módulo desde el menú.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaModulos thead th:nth-child(4)',
          popover: {
            title: 'Tipo',
            description: 'Clasificación funcional del módulo.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaModulos thead th:nth-child(5)',
          popover: {
            title: 'Estado',
            description: 'Indica si el módulo está disponible.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaModulos thead th:nth-child(6)',
          popover: {
            title: 'Acciones del módulo',
            description: 'Desde cada fila puedes consultar, editar o eliminar el módulo.'
          },
          side: 'bottom'
        }
      ];

      if (document.querySelector('#cuerpoModulos .btn-accion-ver')) {
        steps.push(
          {
            element: '#cuerpoModulos tr:first-child .btn-accion-ver',
            popover: {
              title: 'Ver módulo',
              description: 'Consulta los datos del módulo seleccionado.'
            },
            side: 'left'
          },
          {
            element: '#cuerpoModulos tr:first-child .btn-accion-editar',
            popover: {
              title: 'Editar módulo',
              description: 'Modifica los datos permitidos del módulo.'
            },
            side: 'left'
          },
          {
            element: '#cuerpoModulos tr:first-child .btn-accion-eliminar',
            popover: {
              title: 'Eliminar módulo',
              description: 'Inicia la eliminación del módulo seleccionado.'
            },
            side: 'left'
          }
        );
      }
    } else if (activeTab && activeTab.id === 'tab-permisos') {
      steps = [
        {
          element: '#tab-permisos',
          popover: {
            title: 'Pestaña Asignar Permisos',
            description: 'En esta pestaña eliges un rol, revisas sus usuarios y configuras las acciones permitidas para cada módulo.'
          },
          side: 'bottom'
        },
        {
          element: '#selectRol',
          popover: {
            title: 'Seleccionar rol',
            description: 'Elige el rol cuyos permisos quieres consultar o modificar. La tabla se carga al seleccionar uno.'
          },
          side: 'bottom'
        },
        {
          element: '#selectUsuariosPorRol',
          popover: {
            title: 'Usuarios con este rol',
            description: 'Opcionalmente selecciona un usuario para revisar o ajustar sus permisos individuales además de los heredados del rol.'
          },
          side: 'bottom'
        },
        {
          element: '#pane-permisos button[onclick="cargarPermisos()"]',
          popover: {
            title: 'Recargar permisos',
            description: 'Vuelve a consultar la matriz de permisos para el rol seleccionado.'
          },
          side: 'left'
        },
        {
          element: '#btnGuardarPermisos',
          popover: {
            title: 'Guardar permisos',
            description: 'Guarda los cambios marcados en la matriz. Selecciona un rol antes de guardar.'
          },
          side: 'left'
        },
        {
          element: '#tablaPermisos thead th:nth-child(1)',
          popover: {
            title: 'Módulo',
            description: 'Cada fila corresponde a un módulo al que se pueden conceder permisos.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaPermisos thead th:nth-child(2)',
          popover: {
            title: 'Permiso Ver',
            description: 'Permite consultar el módulo.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaPermisos thead th:nth-child(3)',
          popover: {
            title: 'Permiso Crear',
            description: 'Permite crear registros en el módulo.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaPermisos thead th:nth-child(4)',
          popover: {
            title: 'Permiso Editar',
            description: 'Permite modificar registros del módulo.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaPermisos thead th:nth-child(5)',
          popover: {
            title: 'Permiso Eliminar',
            description: 'Permite eliminar registros del módulo.'
          },
          side: 'bottom'
        }
      ];

      ['puede_ver', 'puede_crear', 'puede_editar', 'puede_eliminar'].forEach(function(permission) {
        if (!document.querySelector('#cuerpoPermisos .perm-check[data-campo="' + permission + '"]')) return;
        const labels = {
          puede_ver: 'Ver',
          puede_crear: 'Crear',
          puede_editar: 'Editar',
          puede_eliminar: 'Eliminar'
        };
        steps.push({
          element: '#cuerpoPermisos tr:first-child .perm-check[data-campo="' + permission + '"]',
          popover: {
            title: 'Permiso ' + labels[permission],
            description: 'Activa o desactiva la capacidad de ' + labels[permission].toLowerCase() + ' para este módulo.'
          },
          side: 'top'
        });
      });
    } else {
      steps = [
        {
          element: '#tab-roles',
          popover: {
            title: 'Pestaña Roles',
            description: 'Busca y administra los cargos del sistema. Para recorrer esta pestaña, déjala seleccionada al iniciar la guía.'
          },
          side: 'bottom'
        },
        {
          element: '#tab-modulos',
          popover: {
            title: 'Pestaña Módulos',
            description: 'Administra las secciones que aparecen en la matriz de permisos. Selecciona esta pestaña y reinicia la guía para recorrerla.'
          },
          side: 'bottom'
        },
        {
          element: '#tab-permisos',
          popover: {
            title: 'Pestaña Asignar Permisos',
            description: 'Configura lo que cada rol o usuario puede hacer en cada módulo. Selecciona esta pestaña y reinicia la guía para recorrer sus controles.'
          },
          side: 'bottom'
        }
      ];
    }

    return window.driver.js.driver({
      showProgress: true,
      animate: true,
      smoothScroll: false,
      steps: steps
    });
  };
})();
