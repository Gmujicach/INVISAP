(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['solicitudes'] = function() {
    const path = window.location.pathname || '';
    const isRegisterPage = path.indexOf('form-registrar-solicitud') !== -1 || !!document.querySelector('#seccion_comunidad') || !!document.querySelector('#seccion_institucion') || !!document.querySelector('#seccion_particular');
    const isEditPage = path.indexOf('editar-solicitud') !== -1 || path.indexOf('update-solicitud') !== -1 || !!document.querySelector('input[name="id_solicitud"]') || !!document.querySelector('select[name="estatus_solicitud"]');
    const isListPage = path.indexOf('lista-solicitudes') !== -1 || !!document.querySelector('#tbl_solicitudes') || !!document.querySelector('#modalCrearSolicitud');

    const steps = [];

    if (isRegisterPage) {
      steps.push(
        {
          element: '#tipo_solicitud',
          popover: {
            title: 'Paso 1: Elegir tipo de solicitante',
            description: 'Inicie seleccionando si la solicitud corresponde a una comunidad, institución o solicitante particular. Este campo activa el bloque correspondiente del formulario.'
          },
          side: 'left'
        },
        {
          element: '#seccion_comunidad, #seccion_institucion, #seccion_particular',
          popover: {
            title: 'Paso 2: Completar los datos del perfil',
            description: 'Dependiendo del tipo de solicitante, complete el formulario correspondiente con nombre, municipio, parroquia, contacto y demás datos requeridos.'
          },
          side: 'top'
        },
        {
          element: '#seccion_detalles',
          popover: {
            title: 'Paso 3: Describir la problemática',
            description: 'En la sección de detalles indique la categoría del problema y escriba la descripción clara del requerimiento para la solicitud.'
          },
          side: 'top'
        },
        {
          element: 'button[type="submit"]',
          popover: {
            title: 'Paso 4: Registrar la solicitud',
            description: 'Cuando el formulario esté completo, use el botón Registrar Solicitud para guardar la información en el sistema.'
          },
          side: 'left'
        }
      );
    } else if (isEditPage) {
      steps.push(
        {
          element: 'select[name="estatus_solicitud"]',
          popover: {
            title: 'Modificar estatus de la solicitud',
            description: 'Aquí puede actualizar el estatus de la solicitud según su estado de atención actual: Pendiente, En Proceso o Completada.'
          },
          side: 'left'
        },
        {
          element: 'textarea[name="problematica"]',
          popover: {
            title: 'Actualizar la problemática',
            description: 'Revise o modifique la descripción técnica del reclamo para mantener la información completa y consistente.'
          },
          side: 'left'
        },
        {
          element: 'button[type="submit"]',
          popover: {
            title: 'Guardar cambios',
            description: 'Cuando termine la modificación, confirme con el botón Guardar Cambios para persistir los nuevos datos.'
          },
          side: 'left'
        }
      );
    } else if (isListPage) {
      steps.push(
        {
          element: 'button[data-bs-target="#modalCrearSolicitud"], .btn-primary, .btn-registrar',
          popover: {
            title: 'Nueva Solicitud',
            description: 'Desde aquí puede abrir el formulario para registrar una nueva solicitud del tipo comunidad, institución o particular.'
          },
          side: 'left'
        },
        {
          element: '#widget-pendientes, .stat-card, .counter',
          popover: {
            title: 'Solicitudes Pendientes',
            description: 'Indicador en tiempo real de las solicitudes que aún no han sido atendidas por el equipo.'
          },
          side: 'bottom'
        },
        {
          element: '#widget-en-proceso, .stat-card, .counter',
          popover: {
            title: 'Solicitudes en Proceso',
            description: 'Muestra las solicitudes que ya fueron asociadas a un proyecto y se encuentran en ejecución.'
          },
          side: 'bottom'
        },
        {
          element: '#search, .form-control[type="search"], input[type="search"]',
          popover: {
            title: 'Búsqueda rápida',
            description: 'Filtre por solicitante, tipo de solicitud, problemática o estatus para localizar registros rapidamente.'
          },
          side: 'bottom'
        },
        {
          element: '#tbl_solicitudes, table.table',
          popover: {
            title: 'Registro completo de solicitudes',
            description: 'Listado general con tipo, solicitante, parroquia, problemática, estatus y acciones disponibles.'
          },
          side: 'top'
        },
        {
          element: '#tbl_solicitudes tbody tr:first-child .btn-info, .btn-info, .btn-ver',
          popover: {
            title: 'Ver detalle de la solicitud',
            description: 'Consulte toda la información: datos del solicitante, descripción del problema y seguimiento.'
          },
          side: 'left'
        }
      );
    }

    return window.driver.js.driver({
      showProgress: true,
      steps: steps.length ? steps : [
        {
          element: '#btnTourInvilara, .tour-fab',
          popover: {
            title: 'Guía del módulo de solicitudes',
            description: 'Abra la vista de lista o el formulario para continuar con el recorrido de registro y edición.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
