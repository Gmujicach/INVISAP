(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['evidencia'] = function() {
    const path = window.location.pathname || '';
    const isRegisterPage = path.indexOf('/evidencia/register') !== -1 || path.indexOf('/evidencia/create') !== -1 || !!document.querySelector('#formEvidencias');
    const isEditPage = path.indexOf('/evidencia/edit') !== -1 || path.indexOf('/evidencia/modificar') !== -1 || !!document.querySelector('#formEvidenciasUpdate');
    const isDetailPage = path.indexOf('/evidencia/detalle') !== -1 || path.indexOf('/evidencia/detail') !== -1 || !!document.querySelector('.detail-image-wrapper');
    const isListPage = path.indexOf('/evidencia') !== -1 && !isRegisterPage && !isEditPage && !isDetailPage || !!document.querySelector('#tablaEvidencias, .table-evidencias-modern');

    const steps = [];

    if (isListPage) {
      steps.push(
        {
          element: '.card-header-custom h5, .card-header h5',
          popover: {
            title: 'Listado de Evidencias',
            description: 'Aquí puedes ver todas las evidencias fotográficas registradas en el sistema. Cada registro incluye imagen, descripción, etapa y fecha.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaEvidencias, .table-evidencias-modern',
          popover: {
            title: 'Tabla de Evidencias',
            description: 'Cada fila representa una evidencia fotográfica con su imagen, descripción, etapa (Antes, Durante, Después) y fecha de registro.'
          },
          side: 'top'
        },
        {
          element: '#tablaEvidencias thead th:nth-child(1), .table-evidencias-modern thead th:nth-child(1)',
          popover: {
            title: 'Columna #',
            description: 'Es el número de identificación único de la evidencia en el sistema.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaEvidencias thead th:nth-child(2), .table-evidencias-modern thead th:nth-child(2)',
          popover: {
            title: 'Columna Imagen',
            description: 'Muestra una miniatura de la evidencia fotográfica. Haz clic para ampliarla en una nueva pestaña.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaEvidencias thead th:nth-child(3), .table-evidencias-modern thead th:nth-child(3)',
          popover: {
            title: 'Columna Descripción',
            description: 'Describe lo que muestra la imagen. Ejemplo: "Vista frontal de la obra antes del inicio".'
          },
          side: 'bottom'
        },
        {
          element: '#tablaEvidencias thead th:nth-child(4), .table-evidencias-modern thead th:nth-child(4)',
          popover: {
            title: 'Columna Etapa',
            description: 'Indica en qué momento de la obra se tomó la foto: Antes, Durante o Después. Esto ayuda a organizar el historial visual.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaEvidencias thead th:nth-child(5), .table-evidencias-modern thead th:nth-child(5)',
          popover: {
            title: 'Columna Fecha',
            description: 'Muestra la fecha y hora en que se registró la evidencia en el sistema.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaEvidencias thead th:nth-child(6), .table-evidencias-modern thead th:nth-child(6)',
          popover: {
            title: 'Columna Acciones',
            description: 'Aquí puedes ver el detalle completo, modificar la información o desactivar la evidencia.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaEvidencias tbody tr:first-child .btn-outline-info, .table-evidencias-modern tbody tr:first-child .btn-outline-info',
          popover: {
            title: 'Botón Ver Detalle',
            description: 'Haz clic para ver la imagen en tamaño completo junto con toda la información de la evidencia.'
          },
          side: 'left'
        },
        {
          element: '#tablaEvidencias tbody tr:first-child .btn-outline-warning, .table-evidencias-modern tbody tr:first-child .btn-outline-warning',
          popover: {
            title: 'Botón Modificar',
            description: 'Haz clic para editar la descripción, etapa o reemplazar la imagen de la evidencia.'
          },
          side: 'left'
        },
        {
          element: '#tablaEvidencias tbody tr:first-child .btn-outline-danger, .table-evidencias-modern tbody tr:first-child .btn-outline-danger',
          popover: {
            title: 'Botón Desactivar',
            description: 'Elimina la evidencia del listado activo. Ten cuidado porque esta acción no se puede deshacer.'
          },
          side: 'left'
        }
      );
    } else if (isRegisterPage) {
      steps.push(
        {
          element: '.card-header h5',
          popover: {
            title: 'Registrar Evidencias',
            description: 'En esta sección cargarás las imágenes fotográficas de la obra. Puedes subir entre 3 y 5 imágenes por registro.'
          },
          side: 'bottom'
        },
        {
          element: '#dropZone, .file-drop-zone',
          popover: {
            title: 'Zona de Carga de Imágenes',
            description: 'Arrastra las imágenes desde tu equipo hasta aquí, o haz clic en la zona para abrir el explorador de archivos y seleccionarlas manualmente. Formatos permitidos: JPG, PNG.'
          },
          side: 'top'
        },
        {
          element: '#fileInput, input[type="file"]',
          popover: {
            title: 'Selector de Archivos',
            description: 'Campo oculto que se activa al hacer clic en la zona de carga. Úsalo para elegir las fotos desde tu carpeta de imágenes.'
          },
          side: 'right'
        },
        {
          element: '#imagePreview, .preview-container',
          popover: {
            title: 'Vista Previa',
            description: 'Aquí verás las miniaturas de las imágenes que has seleccionado antes de registrarlas. Puedes revisar que sean las correctas.'
          },
          side: 'top'
        },
        {
          element: '#helpEtapa, .text-warning',
          popover: {
            title: 'Asignación de Etapas',
            description: 'Recuerda que cada imagen debe tener una etapa: Antes (estado inicial de la obra), Durante (proceso de ejecución) o Después (obra culminada).'
          },
          side: 'top'
        },
        {
          element: '#btnSubir, button[type="submit"], .btn-primary',
          popover: {
            title: 'Registrar Evidencias',
            description: 'Haz clic aquí para guardar las evidencias en el sistema. El botón se habilita cuando has cumplido con los requisitos mínimos.'
          },
          side: 'left'
        },
        {
          element: 'a[href*="listar_evidencias"], .btn-outline-secondary',
          popover: {
            title: 'Botón Cancelar',
            description: 'Si haces clic aquí, regresarás al listado de evidencias sin guardar ningún dato.'
          },
          side: 'left'
        }
      );
    } else if (isEditPage) {
      steps.push(
        {
          element: '.card-header h5',
          popover: {
            title: 'Modificar Evidencia',
            description: 'En esta página puedes actualizar la información de una evidencia existente: cambiar la imagen, editar la descripción o la etapa.'
          },
          side: 'bottom'
        },
        {
          element: '#dropZone, .file-drop-zone',
          popover: {
            title: 'Zona de Carga de Nueva Imagen',
            description: 'Si deseas reemplazar la imagen actual, arrastra una nueva foto aquí o haz clic para seleccionarla. Si no la cambias, se mantendrá la imagen anterior.'
          },
          side: 'top'
        },
        {
          element: '#imagePreview, .preview-container',
          popover: {
            title: 'Vista Previa de la Evidencia Actual',
            description: 'Aquí puedes ver la imagen actualmente registrada. Si subes una nueva imagen, esta vista se actualizará para mostrarla.'
          },
          side: 'top'
        },
        {
          element: '#btnModificar, button[type="submit"], .btn-warning',
          popover: {
            title: 'Modificar Evidencia',
            description: 'Haz clic aquí para guardar los cambios realizados. El sistema confirmará cuando se hayan actualizado los datos.'
          },
          side: 'left'
        },
        {
          element: 'a[href*="listar_evidencias"], .btn-outline-secondary',
          popover: {
            title: 'Botón Cancelar',
            description: 'Regresa al listado de evidencias sin guardar los cambios realizados.'
          },
          side: 'left'
        }
      );
    } else if (isDetailPage) {
      steps.push(
        {
          element: '.card-header-custom h5, .card-header h5',
          popover: {
            title: 'Detalle de Evidencia',
            description: 'En esta página puedes ver la información completa de la evidencia seleccionada, incluyendo la imagen en tamaño real.'
          },
          side: 'bottom'
        },
        {
          element: '.detail-image-wrapper, .detail-image-main',
          popover: {
            title: 'Imagen de la Evidencia',
            description: 'Aquí se muestra la fotografía en tamaño completo. Puedes observarla con todo detalle para verificar el estado de la obra.'
          },
          side: 'top'
        },
        {
          element: '.detail-info-card',
          popover: {
            title: 'Información de la Evidencia',
            description: 'Aquí encontrarás todos los datos asociados: ID, descripción, etapa, fecha de registro y estado actual.'
          },
          side: 'right'
        },
        {
          element: '.detail-info-card .info-item:nth-child(1)',
          popover: {
            title: 'ID del Registro',
            description: 'Número único que identifica esta evidencia en el sistema. Sirve para referencias o búsquedas.'
          },
          side: 'bottom'
        },
        {
          element: '.detail-info-card .info-item:nth-child(2)',
          popover: {
            title: 'Descripción',
            description: 'Texto que describe lo que se puede observar en la imagen. Es útil para contextualizar la fotografía.'
          },
          side: 'bottom'
        },
        {
          element: '.detail-info-card .info-item:nth-child(3)',
          popover: {
            title: 'Etapa',
            description: 'Momento de la obra al que pertenece la foto: Antes, Durante o Después. Esto organiza cronológicamente las evidencias.'
          },
          side: 'bottom'
        },
        {
          element: '.detail-info-card .info-item:nth-child(4)',
          popover: {
            title: 'Fecha y Hora',
            description: 'Momento exacto en que se registró la evidencia. Incluye la fecha y la hora para mayor precisión.'
          },
          side: 'bottom'
        },
        {
          element: '.detail-info-card .info-item:nth-child(5)',
          popover: {
            title: 'Estado',
            description: 'Indica si la evidencia está Activa o Inactiva. Solo las evidencias activas aparecen en los listados normales.'
          },
          side: 'bottom'
        },
        {
          element: '.detail-actions .btn-primary, .detail-actions a[href*="modificar"]',
          popover: {
            title: 'Botón Modificar',
            description: 'Haz clic aquí para editar la descripción, cambiar la etapa o reemplazar la imagen de la evidencia.'
          },
          side: 'left'
        },
        {
          element: '.detail-actions .btn-outline-danger',
          popover: {
            title: 'Botón Desactivar',
            description: 'Elimina esta evidencia del listado activo. Esta acción no se puede deshacer.'
          },
          side: 'left'
        },
        {
          element: 'a[href*="listar_evidencias"], .btn-outline-secondary',
          popover: {
            title: 'Botón Volver',
            description: 'Regresa al listado principal de evidencias sin realizar cambios.'
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
            title: 'Guía del módulo de Evidencias',
            description: 'Usa esta guía para aprender a registrar, listar, modificar y ver el detalle de evidencias fotográficas en el sistema.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
