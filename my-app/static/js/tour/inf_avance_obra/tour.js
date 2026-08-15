(function() {
  if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

  window.INVISAP_TOURS['inf_avance_obra'] = function() {
    const path = window.location.pathname || '';
    const modalRegistrar = document.getElementById('modalRegistrarInforme');
    const isRegisterPage = path.indexOf('form-registrar-informe-avance-obra') !== -1 || 
                           (!!modalRegistrar && modalRegistrar.classList.contains('show'));
    const isEditPage = path.indexOf('editar-informe') !== -1 || path.indexOf('Inf_avance_obra_modificar') !== -1 || !!document.querySelector('#formEditarInforme');
    const isListPage = (path.indexOf('inf_avance_obra') !== -1 && !isRegisterPage && !isEditPage) || 
                       (!!document.querySelector('#tablaInformes') && !isRegisterPage && !isEditPage);

    const steps = [];

    if (isListPage) {
      steps.push(
        {
          element: '.card-header h5, .text-invilara-verde',
          popover: {
            title: 'Listado de Informes de Avance',
            description: 'Aquí puedes ver todos los informes registrados. Usa los filtros y la paginación para navegar entre los registros.'
          },
          side: 'bottom'
        },
        {
          element: 'button[data-bs-target="#modalRegistrarInforme"], .btn-invilara-primary',
          popover: {
            title: 'Registrar Nuevo Informe',
            description: 'Haz clic aquí para abrir el formulario y crear un nuevo informe de avance de obra.'
          },
          side: 'left'
        },
        {
          element: '#tablaInformes',
          popover: {
            title: 'Tabla de Informes',
            description: 'Cada fila representa un informe con su tipo, estado, población beneficiada, porcentaje de avance, responsable y fecha.'
          },
          side: 'top'
        },
        {
          element: '#tablaInformes thead th:nth-child(1)',
          popover: {
            title: 'Columna #',
            description: 'Es el número de identificación único del informe en el sistema.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaInformes thead th:nth-child(2)',
          popover: {
            title: 'Tipo de Informe',
            description: 'Indica la categoría del informe: Ficha Inspección Técnica, Informe Menor, Informe Mayor o Avance Mensual.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaInformes thead th:nth-child(3)',
          popover: {
            title: 'Estado',
            description: 'Muestra el estado actual de la obra: Aprobado, En Ejecución, Culminado o Paralizado.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaInformes thead th:nth-child(4)',
          popover: {
            title: 'Población Beneficiada',
            description: 'Describe la comunidad o población que se beneficia con la obra.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaInformes thead th:nth-child(5)',
          popover: {
            title: '% Avance',
            description: 'Porcentaje de avance físico de la obra. Se muestra con una barra de progreso visual.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaInformes thead th:nth-child(6)',
          popover: {
            title: 'Gerente/Inspector',
            description: 'Nombre del empleado responsable del informe (Inspector o Gerente).'
          },
          side: 'bottom'
        },
        {
          element: '#tablaInformes thead th:nth-child(7)',
          popover: {
            title: 'Fecha',
            description: 'Fecha en la que se registró el informe en el sistema.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaInformes thead th:nth-child(8)',
          popover: {
            title: 'Acciones',
            description: 'Botones para Ver, Editar o Eliminar (borrado lógico) cada informe.'
          },
          side: 'bottom'
        },
        {
          element: '#tablaInformes tbody tr:first-child .btn-ver-informe',
          popover: {
            title: 'Botón Ver (Ojo)',
            description: 'Abre un modal con el detalle completo del informe: avance, observaciones, evidencias fotográficas y responsable.'
          },
          side: 'left'
        },
        {
          element: '#tablaInformes tbody tr:first-child .btn-editar-informe',
          popover: {
            title: 'Botón Editar',
            description: 'Te permite modificar los datos del informe: tipo, estado, avance, observaciones, responsable y evidencias.'
          },
          side: 'left'
        },
        {
          element: '#tablaInformes tbody tr:first-child .btn-eliminar-informe',
          popover: {
            title: 'Botón Eliminar',
            description: 'Desactiva el informe (borrado lógico). No se borra permanentemente para preservar el historial y auditoría.'
          },
          side: 'left'
        },
        {
          element: '#paginacionInformes, .pagination',
          popover: {
            title: 'Paginación',
            description: 'Si hay muchos informes, usa estos botones para navegar entre las páginas.'
          },
          side: 'top'
        }
      );
    } else if (isRegisterPage) {
      steps.push(
        {
          element: '#modalRegistrarInforme .modal-title',
          popover: {
            title: 'Formulario de Registro',
            description: 'Aquí registrarás un nuevo informe de avance de obra. Sigue los pasos: completa la información básica, selecciona el responsable, agrega observaciones y adjunta evidencias.'
          },
          side: 'bottom'
        },
        {
          element: '#tipo_informe',
          popover: {
            title: 'Paso 1: Tipo de Informe',
            description: 'Selecciona el tipo de informe según la naturaleza del avance: Ficha Inspección Técnica, Informe Menor, Informe Mayor o Avance Mensual.'
          },
          side: 'right'
        },
        {
          element: '#estado',
          popover: {
            title: 'Paso 2: Estado de la Obra',
            description: 'Indica el estado actual de la obra: Aprobado, En Ejecución, Culminado o Paralizado.'
          },
          side: 'right'
        },
        {
          element: '#poblacion_beneficiada',
          popover: {
            title: 'Paso 3: Población Beneficiada',
            description: 'Escribe el nombre de la comunidad o población que se beneficia con la obra. Ejemplo: Comunidad La Salle, Sector El Cuji.'
          },
          side: 'right'
        },
        {
          element: '#porcentaje_avance',
          popover: {
            title: 'Paso 4: % de Avance',
            description: 'Ingresa el porcentaje de avance físico de la obra. Debe ser un número entre 0 y 100.'
          },
          side: 'right'
        },
        {
          element: '#inspector_nombre_display, #gerente_responsable_id',
          popover: {
            title: 'Paso 5: Inspector Responsable',
            description: 'Haz clic en el botón "Seleccionar Inspector" para abrir un modal donde podrás elegir al empleado responsable del informe. Solo se muestran inspectores activos.'
          },
          side: 'right'
        },
        {
          element: '#observaciones',
          popover: {
            title: 'Paso 6: Observaciones Técnicas',
            description: 'Escribe las observaciones técnicas captadas en campo. Este campo es opcional pero recomendado. Máximo 2000 caracteres.'
          },
          side: 'right'
        },
        {
          element: 'button[data-bs-target="#modalEvidenciasAntes"]',
          popover: {
            title: 'Paso 7: Evidencias ANTES',
            description: 'Haz clic aquí para seleccionar las fotografías del estado ANTES de la obra. Máximo 5 imágenes.'
          },
          side: 'right'
        },
        {
          element: 'button[data-bs-target="#modalEvidenciasDurante"]',
          popover: {
            title: 'Paso 8: Evidencias DURANTE',
            description: 'Haz clic aquí para seleccionar las fotografías del estado DURANTE la obra. Máximo 5 imágenes.'
          },
          side: 'right'
        },
        {
          element: 'button[data-bs-target="#modalEvidenciasDespues"]',
          popover: {
            title: 'Paso 9: Evidencias DESPUÉS',
            description: 'Haz clic aquí para seleccionar las fotografías del estado DESPUÉS de la obra. Máximo 5 imágenes.'
          },
          side: 'right'
        },
        {
          element: '#modalRegistrarInforme .btn-outline-secondary',
          popover: {
            title: 'Botón Cancelar',
            description: 'Si haces clic aquí, se cerrará el formulario sin guardar el informe. Los datos ingresados se perderán.'
          },
          side: 'left'
        },
        {
          element: '#modalRegistrarInforme .btn-invilara-primary',
          popover: {
            title: 'Registrar Informe',
            description: 'Cuando hayas completado todos los pasos, haz clic aquí para guardar el informe en el sistema.'
          },
          side: 'left'
        }
      );
    } else if (isEditPage) {
      steps.push(
        {
          element: '.hero-card h3',
          popover: {
            title: 'Modificar Informe de Avance',
            description: 'Aquí puedes actualizar la información del informe seleccionado. Asegúrate de revisar el estado, el avance y las observaciones antes de guardar.'
          },
          side: 'bottom'
        },
        {
          element: 'select[name="tipo_informe"]',
          popover: {
            title: 'Tipo de Informe',
            description: 'Cambia el tipo de informe si es necesario. Opciones: Ficha Inspección Técnica, Informe Menor, Informe Mayor o Avance Mensual.'
          },
          side: 'right'
        },
        {
          element: 'select[name="estado"]',
          popover: {
            title: 'Estado de la Obra',
            description: 'Actualiza el estado actual de la obra según su avance real.'
          },
          side: 'right'
        },
        {
          element: 'input[name="poblacion_beneficiada"]',
          popover: {
            title: 'Población Beneficiada',
            description: 'Corrige el nombre de la población beneficiada si es necesario.'
          },
          side: 'right'
        },
        {
          element: 'input[name="porcentaje_avance"]',
          popover: {
            title: '% de Avance',
            description: 'Actualiza el porcentaje de avance físico de la obra. Valor entre 0 y 100.'
          },
          side: 'right'
        },
        {
          element: '#inspectorDisplay',
          popover: {
            title: 'Inspector Responsable',
            description: 'Haz clic aquí para cambiar el inspector responsable del informe. Se abrirá un modal con la lista de inspectores activos.'
          },
          side: 'right'
        },
        {
          element: 'textarea[name="observaciones"]',
          popover: {
            title: 'Observaciones Técnicas',
            description: 'Modifica las observaciones técnicas si es necesario. Máximo 2000 caracteres.'
          },
          side: 'right'
        },
        {
          element: 'button[data-bs-target="#modalEvidenciasAntes"]',
          popover: {
            title: 'Evidencias ANTES',
            description: 'Haz clic para agregar o cambiar las fotografías del estado ANTES de la obra.'
          },
          side: 'right'
        },
        {
          element: 'button[data-bs-target="#modalEvidenciasDurante"]',
          popover: {
            title: 'Evidencias DURANTE',
            description: 'Haz clic para agregar o cambiar las fotografías del estado DURANTE la obra.'
          },
          side: 'right'
        },
        {
          element: 'button[data-bs-target="#modalEvidenciasDespues"]',
          popover: {
            title: 'Evidencias DESPUÉS',
            description: 'Haz clic para agregar o cambiar las fotografías del estado DESPUÉS de la obra.'
          },
          side: 'right'
        },
        {
          element: '#formEditarInforme .btn-outline-secondary',
          popover: {
            title: 'Botón Cancelar',
            description: 'Regresa al listado de informes sin guardar los cambios realizados.'
          },
          side: 'left'
        },
        {
          element: '#formEditarInforme .btn-invilara-primary',
          popover: {
            title: 'Guardar Cambios',
            description: 'Haz clic aquí para persistir todas las modificaciones realizadas en el informe.'
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
            title: 'Guía del módulo de Informes de Avance',
            description: 'Navega por las opciones del módulo para ver el recorrido guiado de registro, listado o edición.'
          },
          side: 'left'
        }
      ]
    });
  };
})();
