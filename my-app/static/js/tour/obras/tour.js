(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['obras'] = function() {
    const path = window.location.pathname || '';

    const isEditPage = path.indexOf('editar-obra') !== -1 ||
                        !!document.querySelector('#formEditarObra');

    const modalRegistrar = document.getElementById('modalNuevaObra');
    const isRegisterModalOpen = !!modalRegistrar && modalRegistrar.classList.contains('show');

    const isListPage = path.indexOf('gestionar-obras') !== -1 && !isEditPage;

    const isDetailPage = path.indexOf('obra/detalle') !== -1 ||
                          !!document.querySelector('.evidencia-container .card-modern');

    /**
     * Hook onHighlighted: se dispara DESPUÉS de que driver.js posicionó el
     * highlight. Si el elemento está dentro de un contenedor con scroll
     * interno (ej. el modal-body), ajustamos el scroll de ese contenedor
     * para que el elemento quede centrado. Esto evita el "salto" doble
     * de usar scrollIntoView antes del posicionamiento de driver.
     */
    const onHighlighted = (element) => {
      if (!element) return;
      try {
        const modalBody = element.closest('.modal-body');
        const dialog = element.closest('.modal-dialog');
        const scrollContainer = modalBody || dialog;
        if (scrollContainer && scrollContainer.scrollHeight > scrollContainer.clientHeight) {
          const rect = element.getBoundingClientRect();
          const containerRect = scrollContainer.getBoundingClientRect();
          const desiredCenter = containerRect.top + (scrollContainer.clientHeight / 2);
          const elementCenter = rect.top + (rect.height / 2);
          const delta = elementCenter - desiredCenter;
          scrollContainer.scrollBy({ top: delta, behavior: 'smooth' });
        }
      } catch (e) { /* noop */ }
    };

    const baseStep = (step) => Object.assign({}, step, { onHighlighted });

    const steps = [];

    if (isListPage) {
      steps.push(
        baseStep({
          element: '.card-header h5, .card-header h1',
          popover: {
            title: '¡Bienvenido al Módulo de Obras!',
            description: 'Aquí verás todas las obras del sistema. Podrás consultarlas, registrarlas, modificarlas y desactivarlas.'
          },
          side: 'bottom'
        }),
        baseStep({
          element: 'button[data-bs-target="#modalNuevaObra"]',
          popover: {
            title: 'Registrar Nueva Obra',
            description: 'Este botón azul abre un formulario para crear una obra nueva con todos sus datos.'
          },
          side: 'left'
        }),
        baseStep({
          element: 'table.table',
          popover: {
            title: 'Tabla de Obras',
            description: 'Aquí aparecerán todas las obras que registres. Cada fila es una obra y al final de cada fila verás botones para ver, modificar o desactivar.'
          },
          side: 'top'
        }),
        baseStep({
          element: 'table.table thead th:nth-child(1)',
          popover: { title: 'ID', description: 'Es el número único que el sistema asigna a cada obra para identificarla.' },
          side: 'bottom'
        }),
        baseStep({
          element: 'table.table thead th:nth-child(2)',
          popover: { title: 'Título', description: 'El nombre de la obra. Te ayuda a reconocerla rápidamente.' },
          side: 'bottom'
        }),
        baseStep({
          element: 'table.table thead th:nth-child(3)',
          popover: { title: 'Ubicación', description: 'La dirección exacta donde se realiza la obra.' },
          side: 'bottom'
        }),
        baseStep({
          element: 'table.table thead th:nth-child(4)',
          popover: { title: 'Inicio', description: 'La fecha en que comenzó la obra.' },
          side: 'bottom'
        }),
        baseStep({
          element: 'table.table thead th:nth-child(5)',
          popover: { title: 'Avance', description: 'Qué tanto se ha avanzado en la obra. Se actualiza con cada informe.' },
          side: 'bottom'
        }),
        baseStep({
          element: 'table.table thead th:nth-child(6)',
          popover: {
            title: 'Estado',
            description: 'Un semáforo de colores que te dice cómo va la obra: Verde si va bien, Amarillo si necesita atención, Rojo si está parada.'
          },
          side: 'bottom'
        }),
        baseStep({
          element: 'table.table thead th:nth-child(7)',
          popover: { title: 'Acciones', description: 'Aquí están las opciones para ver, editar o desactivar cada obra.' },
          side: 'bottom'
        }),
        baseStep({
          element: 'table.table tbody tr:first-child .btn-outline-info',
          popover: {
            title: 'Ver Detalle',
            description: 'Abre una página con toda la información de la obra. Solo consulta, no modifica nada.'
          },
          side: 'left'
        }),
        baseStep({
          element: 'table.table tbody tr:first-child .btn-outline-warning',
          popover: {
            title: 'Modificar Obra',
            description: 'Abre el formulario para cambiar los datos de la obra. La contratación y el proyecto no se pueden cambiar.'
          },
          side: 'left'
        }),
        baseStep({
          element: 'table.table tbody tr:first-child .btn-outline-danger',
          popover: {
            title: 'Desactivar Obra',
            description: 'Cambia el estado de la obra a inactiva. No la borra, solo la desactiva para conservar el historial.'
          },
          side: 'left'
        })
      );
    } else if (isRegisterModalOpen) {
      steps.push(
        baseStep({
          element: '#modalNuevaObra .modal-title',
          popover: {
            title: 'Registro de Nueva Obra',
            description: 'Aquí llenas los datos de la obra. Cuando termines, aparecerá en la tabla del listado.'
          },
          side: 'bottom'
        }),
        baseStep({
          element: 'input[name="titulo_obra"]',
          popover: {
            title: 'Título',
            description: 'Escribe el nombre de la obra, por ejemplo: Restauración Vial Av. Venezuela.'
          },
          side: 'right'
        }),
        baseStep({
          element: 'input[name="ubicacion_obra"]',
          popover: {
            title: 'Ubicación',
            description: 'Escribe la dirección exacta, por ejemplo: Calle 5 con Carrera 6, Barquisimeto.'
          },
          side: 'right'
        }),
        baseStep({
          element: 'input[name="periodo_ejecucion"]',
          popover: {
            title: 'Período de Ejecución',
            description: 'Cuánto durará la obra, por ejemplo: 2 meses o 90 días.'
          },
          side: 'right'
        }),
        baseStep({
          element: 'input[name="fecha_inicio"]',
          popover: { title: 'Fecha de Inicio', description: 'El día que comienza la obra.' },
          side: 'right'
        }),
        baseStep({
          element: 'input[name="fecha_fin"]',
          popover: { title: 'Fecha de Fin', description: 'El día que se espera terminar la obra.' },
          side: 'right'
        }),
        baseStep({
          element: 'input[name="mediciones_obra"]',
          popover: {
            title: 'Mediciones',
            description: 'Detalla las medidas, por ejemplo: 230 m² de asfalto.'
          },
          side: 'right'
        }),
        baseStep({
          element: 'input[name="valuaciones"]',
          popover: {
            title: 'Valuaciones',
            description: 'El monto de la obra, por ejemplo: Bs. 31.745.715,41.'
          },
          side: 'right'
        }),
        baseStep({
          element: 'input[name="porcentaje_avance_obra"]',
          popover: {
            title: 'Avance',
            description: 'El porcentaje actual de la obra. 0 significa que no ha empezado, 100 que está terminada.'
          },
          side: 'right'
        }),
        baseStep({
          element: 'input[name="numero_contrato"]',
          popover: {
            title: 'Número de Contrato',
            description: 'El identificador del contrato, por ejemplo: FLR-23580.'
          },
          side: 'right'
        }),
        baseStep({
          element: 'input[name="modificaciones_contrato"]',
          popover: {
            title: 'Modificaciones',
            description: 'Si hubo cambios al contrato, descríbelos. Si no, escribe N/A.'
          },
          side: 'right'
        }),
        baseStep({
          element: 'input[name="certificaciones_obras_ejecutadas"]',
          popover: {
            title: 'Certificaciones',
            description: 'Cuántas certificaciones se han ejecutado hasta ahora.'
          },
          side: 'right'
        }),
        baseStep({
          element: 'select[name="contratacion_id_contratacion"]',
          popover: {
            title: 'Contratación',
            description: 'Selecciona la contratación asociada a esta obra.'
          },
          side: 'right'
        }),
        baseStep({
          element: 'select[name="gestionar_proyectos_codigo_proyecto"]',
          popover: {
            title: 'Proyecto',
            description: 'Selecciona el proyecto al que pertenece la obra.'
          },
          side: 'right'
        }),
        baseStep({
          element: '#modalNuevaObra .btn-outline-secondary',
          popover: {
            title: 'Cancelar',
            description: 'Cierra el formulario sin guardar nada.'
          },
          side: 'left'
        }),
        baseStep({
          element: '#modalNuevaObra button[type="submit"]',
          popover: {
            title: 'Guardar Obra',
            description: 'Guarda todos los datos. Si todo está bien, la obra aparecerá en la tabla.'
          },
          side: 'left'
        })
      );
    } else if (isEditPage) {
      steps.push(
        baseStep({
          element: '.hero-card h3, .card-header h5',
          popover: {
            title: 'Modificar Obra',
            description: 'Estás actualizando una obra que ya existe. Puedes cambiar casi todo, menos la contratación y el proyecto.'
          },
          side: 'bottom'
        }),
        baseStep({ element: 'input[name="titulo_obra"]', popover: { title: 'Título', description: 'Cambia el nombre si es necesario.' }, side: 'right' }),
        baseStep({ element: 'input[name="ubicacion_obra"]', popover: { title: 'Ubicación', description: 'Cambia la dirección si es necesario.' }, side: 'right' }),
        baseStep({ element: 'input[name="periodo_ejecucion"]', popover: { title: 'Período', description: 'Cambia la duración estimada si es necesario.' }, side: 'right' }),
        baseStep({ element: 'input[name="fecha_inicio"]', popover: { title: 'Fecha de Inicio', description: 'Cambia la fecha de inicio si es necesario.' }, side: 'right' }),
        baseStep({ element: 'input[name="fecha_fin"]', popover: { title: 'Fecha de Fin', description: 'Cambia la fecha de culminación. No puede ser antes del inicio.' }, side: 'right' }),
        baseStep({ element: 'input[name="mediciones_obra"]', popover: { title: 'Mediciones', description: 'Cambia las medidas de la obra.' }, side: 'right' }),
        baseStep({ element: 'input[name="valuaciones"]', popover: { title: 'Valuaciones', description: 'Cambia el monto si ha cambiado.' }, side: 'right' }),
        baseStep({ element: 'input[name="porcentaje_avance_obra"]', popover: { title: 'Avance', description: 'Cambia el porcentaje de avance. El semáforo se actualiza solo.' }, side: 'right' }),
        baseStep({ element: 'input[name="numero_contrato"]', popover: { title: 'Número de Contrato', description: 'Cambia el contrato si es necesario.' }, side: 'right' }),
        baseStep({ element: 'input[name="modificaciones_contrato"]', popover: { title: 'Modificaciones', description: 'Actualiza los cambios del contrato.' }, side: 'right' }),
        baseStep({ element: 'input[name="certificaciones_obras_ejecutadas"]', popover: { title: 'Certificaciones', description: 'Cambia la cantidad de certificaciones ejecutadas.' }, side: 'right' }),
        baseStep({
          element: 'input[name="contratacion_id_contratacion_locked"]',
          popover: {
            title: 'Contratación (Bloqueada)',
            description: 'Este campo no se puede cambiar para mantener la trazabilidad.'
          },
          side: 'right'
        }),
        baseStep({
          element: 'input[name="gestionar_proyectos_codigo_proyecto_locked"]',
          popover: {
            title: 'Proyecto (Bloqueado)',
            description: 'Este campo no se puede cambiar para mantener la trazabilidad.'
          },
          side: 'right'
        }),
        baseStep({
          element: '#formEditarObra .btn-outline-secondary',
          popover: {
            title: 'Cancelar',
            description: 'Regresa al listado sin guardar los cambios.'
          },
          side: 'left'
        }),
        baseStep({
          element: '#formEditarObra button[type="submit"]',
          popover: {
            title: 'Actualizar',
            description: 'Guarda los cambios realizados.'
          },
          side: 'left'
        })
      );
    } else if (isDetailPage) {
      steps.push(
        baseStep({
          element: '.card-header-custom h5, .card-header h5',
          popover: {
            title: 'Detalle de la Obra',
            description: 'Aquí ves toda la información de la obra. Esta vista es solo para consultar, no modifica nada.'
          },
          side: 'bottom'
        }),
        baseStep({
          element: '.badge-count, .badge',
          popover: {
            title: 'Estado',
            description: 'Te dice si la obra está activa o inactiva.'
          },
          side: 'left'
        }),
        baseStep({ element: '.detail-info-card .info-item:nth-child(1)', popover: { title: 'ID', description: 'Identificador único de la obra.' }, side: 'right' }),
        baseStep({ element: '.detail-info-card .info-item:nth-child(2)', popover: { title: 'Título', description: 'Nombre de la obra.' }, side: 'right' }),
        baseStep({ element: '.detail-info-card .info-item:nth-child(3)', popover: { title: 'Ubicación', description: 'Dirección donde se ejecuta la obra.' }, side: 'right' }),
        baseStep({ element: '.detail-info-card .info-item:nth-child(4)', popover: { title: 'Período', description: 'Duración estimada de la obra.' }, side: 'right' }),
        baseStep({ element: '.detail-info-card .info-item:nth-child(5)', popover: { title: 'Fecha de Inicio', description: 'Cuándo comenzó la obra.' }, side: 'right' }),
        baseStep({ element: '.detail-info-card .info-item:nth-child(6)', popover: { title: 'Fecha de Fin', description: 'Cuándo se espera terminar.' }, side: 'right' }),
        baseStep({ element: '.detail-info-card .info-item:nth-child(7)', popover: { title: 'Mediciones', description: 'Las medidas de la obra.' }, side: 'right' }),
        baseStep({ element: '.detail-info-card .info-item:nth-child(8)', popover: { title: 'Valuaciones', description: 'El monto de la obra.' }, side: 'right' }),
        baseStep({ element: '.detail-info-card .info-item:nth-child(9)', popover: { title: 'Avance', description: 'Porcentaje de ejecución actual.' }, side: 'right' }),
        baseStep({
          element: '.col-lg-7 .detail-info-card',
          popover: {
            title: 'Datos del Contrato',
            description: 'Información del contrato, contratista, proyecto y estado.'
          },
          side: 'left'
        }),
        baseStep({
          element: '.bi-folder2-open',
          popover: {
            title: 'Proyecto Relacionado',
            description: 'Datos del proyecto al que pertenece esta obra.'
          },
          side: 'right'
        }),
        baseStep({
          element: 'table.table-bordered',
          popover: {
            title: 'Solicitudes y Maquinaria',
            description: 'Las solicitudes ciudadanas y la maquinaria asignada al proyecto.'
          },
          side: 'top'
        }),
        baseStep({
          element: '.bi-graph-up-arrow',
          popover: {
            title: 'Avances Registrados',
            description: 'El historial de todos los informes de avance de la obra.'
          },
          side: 'right'
        }),
        baseStep({
          element: '.detail-actions .btn-primary',
          popover: {
            title: 'Modificar',
            description: 'Abre el formulario para editar la obra.'
          },
          side: 'right'
        }),
        baseStep({
          element: '.detail-actions .btn-outline-danger',
          popover: {
            title: 'Desactivar',
            description: 'Cambia la obra a estado inactivo sin borrarla.'
          },
          side: 'right'
        }),
        baseStep({
          element: '.btn-outline-secondary.btn-custom-cta',
          popover: {
            title: 'Volver al Listado',
            description: 'Regresa a la tabla principal de obras.'
          },
          side: 'left'
        })
      );
    }

    return window.driver.js.driver({
      showProgress: true,
      smoothScroll: true,
      nextBtnText: 'Siguiente',
      prevBtnText: 'Anterior',
      doneBtnText: 'Entendido',
      onHighlighted: onHighlighted,
      steps: steps.length ? steps : [
        baseStep({
          element: '#btnTourInvilara, .tour-fab',
          popover: {
            title: 'Guía del módulo de Obras',
            description: 'Navega por el módulo para ver el recorrido guiado.'
          },
          side: 'left'
        })
      ]
    });
  };
})();