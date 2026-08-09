(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['empleados'] = function() {
    const path = window.location.pathname || '';
    const isRegisterPage = path.indexOf('/empleados/create') !== -1 || !!document.querySelector('#formEmpleado');
    const isEditPage = path.indexOf('/empleados/edit/') !== -1 || !!document.querySelector('#formEmpleadoUpdate');
    const isListPage = path.indexOf('/empleados') !== -1 && !isRegisterPage && !isEditPage || !!document.querySelector('#tablaEmpleados');

    const steps = [];

    if (isListPage) {
      steps.push(
        {
          element: '#infoRegistros',
          popover: {
            title: 'Contador de registros',
            description: 'Aquí puedes ver cuántos empleados hay en total y cuántos se están mostrando en la página actual.'
          },
          side: 'bottom'
        },
        {
          element: '#btnRegistrarNuevo, a.btn-primary[href*="viewFormEmpleado"]',
          popover: {
            title: 'Registrar Nuevo Empleado',
            description: 'Haz clic aquí para abrir el formulario y agregar un nuevo empleado al sistema. Podrás ingresar sus datos laborales y personales.'
          },
          side: 'left'
        },
        {
          element: '#tablaEmpleados',
          popover: {
            title: 'Listado de Empleados',
            description: 'Esta tabla muestra a todo el personal activo registrado en Invilara. Cada fila representa un empleado con su información completa.'
          },
          side: 'top'
        },
        {
          element: '#tablaEmpleados thead th:nth-child(1)',
          popover: {
            title: 'Columna ID',
            description: 'Es el número de identificación único del empleado en el sistema. No se repite y sirve para buscar o editar registros.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaEmpleados thead th:nth-child(2)',
          popover: {
            title: 'Columna Nombre',
            description: 'Muestra el nombre completo del empleado tal como fue registrado en el sistema.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaEmpleados thead th:nth-child(3)',
          popover: {
            title: 'Columna Cargo',
            description: 'Indica el puesto o cargo que desempeña el empleado dentro de la estructura organizacional de Invilara.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaEmpleados thead th:nth-child(4)',
          popover: {
            title: 'Columna Gerencia',
            description: 'Muestra la gerencia o departamento al que está asignado el empleado.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaEmpleados thead th:nth-child(5)',
          popover: {
            title: 'Columna Ingreso',
            description: 'Es la fecha en la que el empleado ingresó a la institución. Se usa para calcular antigüedad.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaEmpleados thead th:nth-child(6)',
          popover: {
            title: 'Columna Estado',
            description: 'Muestra si el empleado está Activo o Inactivo. Solo los empleados activos pueden ser asignados a proyectos o aparecen en los listados.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaEmpleados thead th:nth-child(7)',
          popover: {
            title: 'Columna Acciones',
            description: 'Aquí encontrarás dos botones: uno para editar la información del empleado y otro para desactivarlo (borrado lógico).'
          },
          side: 'bottom'
        },
        {
          element: '#tablaEmpleados tbody tr:first-child .btn-warning',
          popover: {
            title: 'Botón Editar',
            description: 'Haz clic en este botón para modificar los datos del empleado: nombre, cargo, gerencia, teléfono, entre otros. Los cambios se guardan automáticamente al enviar el formulario.'
          },
          side: 'left'
        },
        {
          element: '#tablaEmpleados tbody tr:first-child .btn-danger',
          popover: {
            title: 'Botón Eliminar (Borrado Lógico)',
            description: 'Al hacer clic, el empleado será borrado su información de la lista.'
          },
          side: 'left'
        },
        {
          element: '.pagination',
          popover: {
            title: 'Paginación',
            description: 'Si hay más de 10 empleados, usa estos botones para navegar entre las páginas. Haz clic en los números o en las flechas para avanzar o retroceder.'
          },
          side: 'top'
        }
      );
    } else if (isRegisterPage) {
      steps.push(
        {
          element: '.card-header h5',
          popover: {
            title: 'Formulario de Registro',
            description: 'En esta sección ingresarás toda la información del nuevo empleado. Asegúrate de completar todos los campos obligatorios antes de guardar.'
          },
          side: 'bottom'
        },
        {
          element: 'input[name="nombre_empleado"]',
          popover: {
            title: 'Nombre Completo',
            description: 'Escribe el nombre completo del empleado. Solo se permiten letras y espacios. Mínimo 3 caracteres, máximo 45. Ejemplo: Juan Carlos Pérez González.'
          },
          side: 'right'
        },
        {
          element: 'select[name="cargo"]',
          popover: {
            title: 'Cargo Institucional',
            description: 'Selecciona el cargo que desempeñará el empleado. Opciones disponibles: Gerente, Inspector, Asistente, Proyectista, Recepcionista, Ingeniero, Coordinador u Operador.'
          },
          side: 'right'
        },
        {
          element: 'input[name="fecha_ingreso"]',
          popover: {
            title: 'Fecha de Ingreso',
            description: 'Selecciona la fecha en la que el empleado comenzó a trabajar en Invilara. Formato: AAAA-MM-DD. Este campo es obligatorio.'
          },
          side: 'right'
        },
        {
          element: 'input[name="gerencia_asignada"]',
          popover: {
            title: 'Gerencia Asignada',
            description: 'Escribe el nombre de la gerencia o departamento al que pertenecerá el empleado. Ejemplo: Gerencia de Infraestructura y Mantenimiento. Mínimo 5 caracteres.'
          },
          side: 'right'
        },
        {
          element: 'input[name="cedula_empleado"]',
          popover: {
            title: 'Cédula de Identidad',
            description: 'Ingresa el número de cédula del empleado. Debe contener entre 7 y 8 dígitos numéricos. Este dato es único y obligatorio.'
          },
          side: 'right'
        },
        {
          element: 'input[name="telefono"]',
          popover: {
            title: 'Teléfono',
            description: 'Ingresa el número de teléfono del empleado. Escribe solo números, sin espacios ni guiones. Debe tener entre 10 y 11 dígitos. Ejemplo: 04141234567. Este campo es opcional pero recomendado.'
          },
          side: 'right'
        },
        {
          element: 'input[name="correo"]',
          popover: {
            title: 'Correo Electrónico',
            description: 'Escribe el correo electrónico del empleado. Debe tener un formato válido como usuario@dominio.com. Este campo es opcional.'
          },
          side: 'right'
        },
        {
          element: 'input[name="direccion"]',
          popover: {
            title: 'Dirección',
            description: 'Escribe la dirección de habitación del empleado. Este campo es opcional.'
          },
          side: 'right'
        },
        {
          element: 'input[name="parroquia"]',
          popover: {
            title: 'Parroquia',
            description: 'Indica la parroquia donde reside el empleado. Campo opcional.'
          },
          side: 'right'
        },
        {
          element: 'input[name="municipio"]',
          popover: {
            title: 'Municipio',
            description: 'Indica el municipio donde reside el empleado. Campo opcional.'
          },
          side: 'right'
        },
        {
          element: '#btnCancelar',
          popover: {
            title: 'Botón Cancelar',
            description: 'Si haces clic aquí, regresarás al listado de empleados sin guardar ningún dato. Los campos se limpiarán y no se creará el registro.'
          },
          side: 'left'
        },
        {
          element: '#btnGuardar',
          popover: {
            title: 'Registrar Empleado',
            description: 'Haz clic aquí para guardar toda la información y crear el registro del empleado en el sistema. Si hay campos vacíos o incorrectos, el sistema te lo indicará.'
          },
          side: 'left'
        }
      );
    } else if (isEditPage) {
      steps.push(
        {
          element: '.card-header h5',
          popover: {
            title: 'Modo Edición',
            description: 'En esta página puedes modificar la información del empleado seleccionado. Los cambios se guardan al hacer clic en Actualizar Información.'
          },
          side: 'bottom'
        },
        {
          element: 'input[name="nombre_empleado"]',
          popover: {
            title: 'Nombre Completo',
            description: 'Modifica el nombre del empleado si es necesario. Recuerda usar solo letras y espacios, entre 3 y 45 caracteres.'
          },
          side: 'right'
        },
        {
          element: 'select[name="cargo"]',
          popover: {
            title: 'Cargo Institucional',
            description: 'Cambia el cargo del empleado si ha sido promocionado o reasignado. Selecciona una opción de la lista.'
          },
          side: 'right'
        },
        {
          element: 'input[name="fecha_ingreso"]',
          popover: {
            title: 'Fecha de Ingreso',
            description: 'Corrige la fecha de ingreso si estaba incorrecta. Usa el formato AAAA-MM-DD.'
          },
          side: 'right'
        },
        {
          element: 'input[name="gerencia_asignada"]',
          popover: {
            title: 'Gerencia Asignada',
            description: 'Actualiza la gerencia o departamento si el empleado fue transferido a otra área. Mínimo 5 caracteres, solo letras y espacios.'
          },
          side: 'right'
        },
        {
          element: '#btnCancelar',
          popover: {
            title: 'Botón Cancelar',
            description: 'Regresa al listado de empleados sin guardar los cambios realizados.'
          },
          side: 'left'
        },
        {
          element: '#btnActualizar',
          popover: {
            title: 'Actualizar Información',
            description: 'Haz clic aquí para guardar los cambios realizados en el formulario. El sistema validará los datos y mostrará una confirmación si todo está correcto.'
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
          element: '#btnTourInvilara, .tour-fab',
          popover: {
            title: 'Guía del módulo de empleados',
            description: 'Navega por las opciones del módulo para ver el recorrido guiado de listado, registro o edición.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
