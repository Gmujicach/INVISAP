/**
 * Función principal que inicializa todos los componentes del módulo
 * Se ejecuta cuando el DOM está completamente cargado
 */
function inicializarModuloInformes() {
    console.log('✓ Módulo Informe de Avance de Obra cargado correctamente');
    console.log('Inicializando componentes del módulo...');
    
    // 1. Interceptar formulario de registro
    const formInforme = document.querySelector('form[action="/form-registrar-informe-avance-obra"]');
    if (formInforme && !formInforme.dataset.fetchBound) {
        formInforme.addEventListener('submit', function(e) {
            e.preventDefault();
            registrarInformeConFetch(this);
        });
        formInforme.dataset.fetchBound = 'true';
        console.log('✓ Formulario interceptado para usar Fetch');
    }
    
    // 2. Validación en tiempo real del gerente/inspector
    const selectGerente = document.getElementById('gerente_responsable_id');
    if (selectGerente) {
        selectGerente.addEventListener('change', validarGerenteEnTiempoReal);
        console.log('✓ Validación en tiempo real activada para gerente');
    }
    
    // 3. Contador de caracteres para observaciones
    const textareaObs = document.getElementById('observaciones');
    if (textareaObs) {
        agregarContadorCaracteres(textareaObs, 500);
        console.log('✓ Contador de caracteres agregado');
    }
    
    // 4. Validación de límite de imágenes
    const inputAntes = document.getElementById('evidencias_antes');
    const inputDurante = document.getElementById('evidencias_durante');
    const inputDespues = document.getElementById('evidencias_despues');
    
    if (inputAntes) {
        validarLimiteImagenes(inputAntes, 5);
        console.log('✓ Validación de imágenes ANTES activada');
    }
    if (inputDurante) {
        validarLimiteImagenes(inputDurante, 5);
        console.log('✓ Validación de imágenes DURANTE activada');
    }
    if (inputDespues) {
        validarLimiteImagenes(inputDespues, 5);
        console.log('✓ Validación de imágenes DESPUÉS activada');
    }
    
    // 5. Botones de editar
    document.querySelectorAll('.btn-editar-informe').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const idInforme = this.dataset.id;
            window.location.href = `/editar-informe/${idInforme}`;
        });
    });
    
    // 6. Modal de detalle del informe
    const modalDetalle = document.getElementById('modalDetalleInforme');
    if (modalDetalle && !modalDetalle.dataset.detailBound) {
        modalDetalle.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const idInforme = button ? button.getAttribute('data-id') : null;
            if (idInforme) {
                abrirModalDetalle(idInforme);
            }
        });
        modalDetalle.dataset.detailBound = 'true';
        console.log('✓ Modal de detalle configurado');
    }
    
    // 6. Formulario de edición por fetch si existe en la página (usar solo en /editar-informe)
    const formEditarInforme = document.getElementById('formEditarInforme');
    if (formEditarInforme && window.location.pathname.startsWith('/editar-informe') && !formEditarInforme.dataset.fetchBound) {
        formEditarInforme.addEventListener('submit', function(e) {
            e.preventDefault();
            actualizarInformeConFetch(this);
        });
        formEditarInforme.dataset.fetchBound = 'true';
        console.log('✓ Formulario de edición conectado a Fetch');
    }
}

// Asegurar ejecución incluso si el DOM ya está listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inicializarModuloInformes);
} else {
    inicializarModuloInformes();
}

async function actualizarInformeConFetch(form) {
    console.log('Iniciando actualización con Fetch...');

    const formData = new FormData(form);
    const btnSubmit = form.querySelector('button[type="submit"]');
    const textoOriginal = btnSubmit.innerHTML;
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Guardando...';

    try {
        const response = await fetch('/api/informes/actualizar', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        console.log('Respuesta actualización:', result);

        if (response.ok && result.status === 'success') {
            mostrarAlerta('success', result.message);
            setTimeout(() => {
                window.location.href = '/inf_avance_obra';
            }, 1200);
        } else {
            mostrarAlerta('error', result.message || 'Error al actualizar el informe');
        }
    } catch (error) {
        console.error('Error de conexión en actualización:', error);
        mostrarAlerta('error', 'Error de conexión con el servidor.');
    } finally {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = textoOriginal;
    }
}

// =================================
// FETCH/AJAX - REGISTRO DE INFORME
// =================================

/**
 * FLUJO:
 * 1. Captura datos del formulario
 * 2. Convierte a JSON
 * 3. Envía al servidor con fetch()
 * 4. Recibe respuesta JSON
 * 5. Actualiza solo la tabla (sin recargar página)
 * 
 * @param {HTMLFormElement} form - El formulario a enviar
 */
async function registrarInformeConFetch(form) {
    console.log('Iniciando registro con Fetch...');
    
    // 1. Capturar datos del formulario
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    console.log('Datos capturados:', data);
    
    // 2. Mostrar indicador de carga (UX mejorada)
    const btnSubmit = form.querySelector('button[type="submit"]');
    const textoOriginal = btnSubmit.innerHTML;
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Guardando...';
    
    try {
        // 3. Enviar datos al servidor con Fetch
        const response = await fetch('/api/informes/crear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json', // Importante: decir que enviamos JSON
            },
            body: JSON.stringify(data) // Convertir objeto a JSON
        });
        
        // 4. Recibir respuesta del servidor
        const result = await response.json();
        console.log('Respuesta del servidor:', result);
        
        // 5. Procesar respuesta
        if (response.ok && result.status === 'success') {
            mostrarAlerta('success', result.message);
            form.reset();
            
            setTimeout(() => {
                recargarTablaInformes();
            }, 1500);
            
        } else {
            // Error: Mostrar mensaje de error
            mostrarAlerta('error', result.message || 'Error al registrar el informe');
        }
        
    } catch (error) {
        // Error de conexión
        console.error('Error de conexión:', error);
        mostrarAlerta('error', 'Error de conexión con el servidor. Verifique su red.');
    } finally {
        // Restaurar botón (siempre se ejecuta)
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = textoOriginal;
    }
}

// =========================
// VALIDACIÓN EN TIEMPO REAL
// =========================

/**
 * Valida el gerente/inspector seleccionado en tiempo real
 *
 * FLUJO:
 * 1. Usuario selecciona un gerente del dropdown
 * 2. Se dispara evento 'change'
 * 3. Fetch valida con el servidor si existe y está activo
 * 4. Verifica que tenga cargo de Gerente o Inspector
 * 5. Muestra feedback visual (✓ o ✗)
 * 
 * @param {Event} event - Evento change del select
 */
async function validarGerenteEnTiempoReal(event) {
    const selectGerente = event.target;
    const idEmpleado = selectGerente.value;
    
    if (!idEmpleado) return; // Si no hay selección, salir
    
    console.log(`Validando gerente ID: ${idEmpleado}...`);
    
    // 1. Mostrar indicador de "Validando..."
    const feedbackContainer = selectGerente.parentElement;
    let loadingIndicator = feedbackContainer.querySelector('.validating-indicator');
    
    if (!loadingIndicator) {
        loadingIndicator = document.createElement('small');
        loadingIndicator.className = 'validating-indicator text-muted d-block mt-1';
        loadingIndicator.innerHTML = '<i class="bx bx-loader-alt bx-spin"></i> Validando...';
        feedbackContainer.appendChild(loadingIndicator);
    }
    
    try {
        // 2. Consultar al servidor si el empleado existe y es válido
        const response = await fetch(`/api/informes/validar-gerente/${idEmpleado}`);
        const data = await response.json();
        console.log('Resultado validación:', data);
        
        // 3. Remover indicador de carga
        if (loadingIndicator) loadingIndicator.remove();
        
        // 4. Remover feedback anterior
        const existingFeedback = feedbackContainer.querySelector('.validation-feedback');
        if (existingFeedback) existingFeedback.remove();
        
        // 5. Validar existencia y estado activo
        if (!data.existe || !data.activo) {
            mostrarAlerta('warning', 'Este empleado ya no está disponible en el sistema');
            selectGerente.value = ''; // Limpiar selección
            return;
        }
        
        // 6. Validar cargo (Prof. Jhoanly: solo Gerente o Inspector)
        if (!data.es_gerente_o_inspector) {
            mostrarAlerta('warning', `El empleado tiene cargo de "${data.cargo}". Solo se permiten Gerentes o Inspectores.`);
            selectGerente.value = ''; // Limpiar selección
            return;
        }
        
        // 7. Todo OK: Mostrar confirmación visual
        const feedback = document.createElement('small');
        feedback.className = 'validation-feedback text-success d-block mt-1';
        feedback.innerHTML = `<i class="bx bx-check-circle"></i> ${data.nombre} - ${data.cargo}`;
        feedbackContainer.appendChild(feedback);
        console.log('✓ Validación exitosa');
        
    } catch (error) {
        console.error('Error validando gerente:', error);
        if (loadingIndicator) loadingIndicator.remove();
        mostrarAlerta('error', 'Error al validar el empleado. Intente nuevamente.');
    }
}

// ============================================================================
// VALIDACIÓN DE LÍMITE DE IMÁGENES (Prof. Cadenas - Máximo 5)
// ============================================================================

/**
 * Valida que no se suban más de 5 imágenes por etapa
 * 
 * @param {HTMLInputElement} inputFile - Input type="file"
 * @param {number} maxImagenes - Máximo de imágenes permitidas (default: 5)
 */
function validarLimiteImagenes(inputFile, maxImagenes = 5) {
    inputFile.addEventListener('change', function() {
        console.log(`Imágenes seleccionadas: ${this.files.length}`);
        
        // 1. Validar límite
        if (this.files.length > maxImagenes) {
            mostrarAlerta('warning', `Solo se permiten máximo ${maxImagenes} imágenes por etapa`);
            this.value = ''; // Limpiar selección
            
            // 2. Mostrar feedback visual temporal
            const feedback = document.createElement('small');
            feedback.className = 'text-danger d-block mt-1';
            feedback.textContent = `Límite excedido: ${maxImagenes} imágenes máximo`;
            
            const existingFeedback = this.parentElement.querySelector('.text-danger');
            if (existingFeedback) existingFeedback.remove();
            
            this.parentElement.appendChild(feedback);
            
            // Remover feedback después de 3 segundos
            setTimeout(() => feedback.remove(), 3000);
            
        } else if (this.files.length > 0) {
            // 3. Si está dentro del límite, mostrar preview
            mostrarPreviewImagenes(this);
        }
    });
}

/**
 * Muestra preview de las imágenes seleccionadas
 * 
 * @param {HTMLInputElement} input - Input type="file"
 */
function mostrarPreviewImagenes(input) {
    const previewContainer = input.parentElement.querySelector('.preview-imagenes') || 
                            crearContenedorPreview(input.parentElement);
    
    previewContainer.innerHTML = ''; // Limpiar previews anteriores
    
    // Iterar sobre cada archivo seleccionado
    Array.from(input.files).forEach((file, index) => {
        if (file.type.startsWith('image/')) {
            // FileReader: API del navegador para leer archivos locales
            const reader = new FileReader();
            
            reader.onload = function(e) {
                // Crear miniatura de la imagen
                const imgWrapper = document.createElement('div');
                imgWrapper.className = 'preview-img-wrapper d-inline-block me-2 mb-2 position-relative';
                imgWrapper.style.width = '80px';
                imgWrapper.style.height = '80px';
                
                const img = document.createElement('img');
                img.src = e.target.result; // Data URL de la imagen
                img.className = 'img-thumbnail';
                img.style.width = '100%';
                img.style.height = '100%';
                img.style.objectFit = 'cover';
                
                const badge = document.createElement('span');
                badge.className = 'badge bg-primary position-absolute top-0 start-0 m-1';
                badge.textContent = index + 1; // Número de imagen
                
                imgWrapper.appendChild(img);
                imgWrapper.appendChild(badge);
                previewContainer.appendChild(imgWrapper);
            };
            
            reader.readAsDataURL(file); // Leer archivo como Data URL
        }
    });
}

/**
 * Crea el contenedor para los previews de imágenes
 */
function crearContenedorPreview(parentElement) {
    const container = document.createElement('div');
    container.className = 'preview-imagenes mt-2';
    parentElement.appendChild(container);
    return container;
}

// ======================================
// CONTADOR DE CARACTERES (UX Mejorada)
// ======================================

/**
 * Agrega un contador de caracteres a un textarea
 * 
 * @param {HTMLTextAreaElement} textarea - El textarea a monitorear
 * @param {number} maxCaracteres - Máximo de caracteres permitidos
 */
function agregarContadorCaracteres(textarea, maxCaracteres) {
    // 1. Crear elemento contador
    const contador = document.createElement('small');
    contador.className = 'form-text text-muted';
    contador.id = `contador-${textarea.id}`;
    textarea.parentElement.appendChild(contador);
    
    // 2. Función para actualizar el contador
    function actualizarContador() {
        const restantes = maxCaracteres - textarea.value.length;
        contador.textContent = `${restantes} caracteres restantes`;
        
        // 3. Cambiar color según caracteres restantes
        if (restantes < 0) {
            // Rojo: Excedió el límite
            contador.classList.remove('text-muted', 'text-warning');
            contador.classList.add('text-danger');
        } else if (restantes < 50) {
            // Amarillo: Cerca del límite
            contador.classList.remove('text-muted', 'text-danger');
            contador.classList.add('text-warning');
        } else {
            // Gris: Normal
            contador.classList.remove('text-warning', 'text-danger');
            contador.classList.add('text-muted');
        }
    }
    
    // 4. Actualizar en cada tecla presionada
    textarea.addEventListener('input', actualizarContador);
    actualizarContador(); // Inicializar
}

// ====================================
// RECARGAR TABLA SIN RECARGAR PÁGINA
// ====================================

/**
 * Recarga solo la tabla de informes sin recargar toda la página
 * 
 * FLUJO:
 * 1. Fetch obtiene lista actualizada de informes (JSON)
 * 2. Limpia el tbody de la tabla
 * 3. Crea nuevas filas con los datos actualizados
 * 4. Actualiza contadores
 */
async function recargarTablaInformes() {
    console.log('Recargando tabla de informes...');
    
    try {
        // 1. Obtener datos actualizados del servidor
        const response = await fetch('/api/informes/listar-json');
        const informes = await response.json();
        console.log(`Informes obtenidos: ${informes.length}`);
        
        // 2. Obtener tbody de la tabla
        const tbody = document.querySelector('#tablaInformes tbody');
        if (!tbody) {
            // Si no existe la tabla, recargar página completa
            window.location.reload();
            return;
        }
        
        // 3. Limpiar tabla
        tbody.innerHTML = '';
        
        // 4. Llenar tabla con nuevos datos
        if (informes.length === 0) {
            // Sin informes: Mostrar mensaje
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center text-muted py-4">
                        <i class="bx bx-info-circle bx-lg"></i><br>
                        No hay informes registrados en el sistema.
                    </td>
                </tr>
            `;
        } else {
            // Con informes: Crear filas
            informes.forEach(informe => {
                const fila = crearFilaInforme(informe);
                tbody.appendChild(fila);
            });
            
            // Re-inicializar event listeners de los nuevos botones
            inicializarModuloInformes();
        }
        
        // 5. Actualizar contadores
        actualizarContadorInformes();
        console.log('✓ Tabla recargada exitosamente');
        
    } catch (error) {
        console.error('Error recargando tabla:', error);
        // Si falla, recargar página completa como fallback
        window.location.reload();
    }
}

/**
 * Crea una fila HTML para un informe
 */
function crearFilaInforme(informe) {
    const tr = document.createElement('tr');
    const porcentaje = informe.porcentaje_avance || 0;
    const badgeClass = getBadgeClass(informe.estado);
    
    tr.innerHTML = `
        <td>${informe.id_informe}</td>
        <td>${informe.tipo_informe}</td>
        <td><span class="badge ${badgeClass}">${informe.estado}</span></td>
        <td>${informe.poblacion_beneficiada || 'N/A'}</td>
        <td>
            <div class="progress" style="height: 20px;">
                <div class="progress-bar bg-success" role="progressbar" 
                     style="width: ${porcentaje}%;" 
                     aria-valuenow="${porcentaje}" 
                     aria-valuemin="0" aria-valuemax="100">
                    ${porcentaje}%
                </div>
            </div>
        </td>
        <td>${informe.gerente_nombre || 'No asignado'}</td>
        <td>${formatearFecha(informe.fecha)}</td>
        <td class="text-center">
            <button type="button" class="btn btn-outline-info btn-sm btn-ver-informe" data-id="${informe.id_informe}" data-bs-toggle="modal" data-bs-target="#modalDetalleInforme" title="Ver detalle">
                <i class="bx bx-show"></i>
            </button>
            <a href="/editar-informe/${informe.id_informe}" class="btn btn-outline-warning btn-sm" title="Editar">
                <i class="bx bx-edit"></i>
            </a>
            <button class="btn btn-outline-danger btn-sm btn-eliminar-informe" data-id="${informe.id_informe}" title="Eliminar">
                <i class="bx bx-trash"></i>
            </button>
        </td>
    `;
    
    return tr;
}

// ======================
// DETALLE EN MODAL
// ======================

async function abrirModalDetalle(idInforme) {
    const body = document.getElementById('detalleInformeBody');
    if (!body) return;

    body.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-success" role="status"></div>
            <p class="text-muted mt-2">Cargando información...</p>
        </div>
    `;

    try {
        const response = await fetch(`/api/informes/detalle/${idInforme}`);
        const result = await response.json();

        if (!response.ok || result.status !== 'success') {
            body.innerHTML = `<div class="alert alert-danger">${result.message || 'No se pudo cargar el detalle.'}</div>`;
            return;
        }

        const informe = result.data;
        const evidencias = informe.evidencias || [];
        const etapas = ['antes', 'durante', 'despues'];

        function getEvidenciaImageUrl(path) {
            if (!path) return '';
            if (/^https?:\/\//i.test(path)) return path;
            const cleanPath = String(path).replace(/^\/+/, '').replace(/^static\//, '');
            return `/static/${cleanPath}`;
        }

        const htmlEvidencias = etapas.map(etapa => {
            const items = evidencias.filter(item => item.etapa === etapa);
            if (!items.length) return '';
            return `
                <div class="mt-3">
                    <h6 class="text-capitalize text-invilara-verde"><i class="bx bx-image me-1"></i>${etapa}</h6>
                    <div class="row g-2">
                        ${items.map(item => `
                            <div class="col-md-4">
                                <div class="card modal-detail-card h-100">
                                    <img src="${getEvidenciaImageUrl(item.url_archivos)}" class="card-img-top" style="height: 140px; object-fit: cover;" alt="${item.fotos}" />
                                    <div class="card-body p-2">
                                        <small class="fw-bold d-block">${item.fotos || 'Evidencia'}</small>
                                        <small class="text-muted">${item.fecha_registro ? new Date(item.fecha_registro).toLocaleDateString('es-VE') : ''}</small>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }).join('');

        body.innerHTML = `
            <div class="row g-3">
                <div class="col-12">
                    <div class="card modal-detail-card">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
                                <h5 class="mb-0 text-invilara-verde">${informe.tipo_informe || 'Sin tipo'}</h5>
                                <span class="badge bg-success">${informe.estado || 'Sin estado'}</span>
                            </div>
                            <div class="row mt-3">
                                <div class="col-md-6">
                                    <p class="mb-1"><strong>Fecha:</strong> ${formatearFecha(informe.fecha)}</p>
                                    <p class="mb-1"><strong>Población beneficiada:</strong> ${informe.poblacion_beneficiada || 'No especificado'}</p>
                                    <p class="mb-1"><strong>Avance:</strong> ${informe.porcentaje_avance || 0}%</p>
                                </div>
                                <div class="col-md-6">
                                    <p class="mb-1"><strong>Inspector / gerente:</strong> ${informe.gerente_nombre || 'No asignado'}</p>
                                    <p class="mb-1"><strong>Observaciones:</strong> ${informe.observaciones || 'Sin observaciones'}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-12">
                    <div class="card modal-detail-card">
                        <div class="card-body">
                            <h6 class="text-invilara-verde"><i class="bx bx-camera me-1"></i>Evidencias registradas</h6>
                            ${htmlEvidencias || '<p class="text-muted mb-0">No hay evidencias registradas para este informe.</p>'}
                        </div>
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error al cargar detalle:', error);
        body.innerHTML = '<div class="alert alert-danger">No se pudo cargar el detalle del informe.</div>';
    }
}

// ======================
// FUNCIONES AUXILIARES
// ======================

/**
 * Obtiene la clase CSS del badge según el estado
 */
function getBadgeClass(estado) {
    const clases = {
        'Aprobado': 'bg-success',
        'En Ejecucion': 'bg-warning text-dark',
        'Culminado': 'bg-info',
        'Paralizado': 'bg-danger'
    };
    return clases[estado] || 'bg-secondary';
}

/**
 * Formatea una fecha para mostrar en formato DD/MM/YYYY
 */
function formatearFecha(fecha) {
    if (!fecha) return 'N/A';
    
    try {
        const date = new Date(fecha);
        return date.toLocaleDateString('es-VE', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    } catch (error) {
        return fecha;
    }
}

/**
 * Actualiza el contador de informes en las tarjetas de estadísticas
 */
function actualizarContadorInformes() {
    const filas = document.querySelectorAll('#tablaInformes tbody tr');
    const totalInformes = filas.length;
    
    const cardTotal = document.querySelector('.card-body h3.text-primary');
    if (cardTotal) {
        cardTotal.textContent = totalInformes;
    }
}

// =========================================================
// ALERTAS Y CONFIRMACIONES (100% LOCAL - SIN SWEETALERT2)
// =========================================================

/**
 * Muestra una alerta al usuario
 * 
 * @param {string} tipo - 'success', 'error', 'warning', 'info'
 * @param {string} mensaje - Mensaje a mostrar
 */
function mostrarAlerta(tipo, mensaje) {
    console.log(`[${tipo.toUpperCase()}] ${mensaje}`);
    
    // Opción 1: Intentar usar Bootstrap Toast (si está disponible)
    if (typeof bootstrap !== 'undefined') {
        crearToastBootstrap(tipo, mensaje);
    } else {
        // Opción 2: Fallback a alert() nativo
        const iconos = {
            'success': '✓',
            'error': '✗',
            'warning': '⚠',
            'info': 'ℹ'
        };
        
        const prefijo = iconos[tipo] || 'ℹ';
        alert(`${prefijo} ${mensaje}`);
    }
}

/**
 * Crea un Toast de Bootstrap (alternativa local a SweetAlert2)
 * 
 */
function crearToastBootstrap(tipo, mensaje) {
    const colores = {
        'success': 'bg-success',
        'error': 'bg-danger',
        'warning': 'bg-warning',
        'info': 'bg-info'
    };
    
    const iconos = {
        'success': 'bx-check-circle',
        'error': 'bx-x-circle',
        'warning': 'bx-error',
        'info': 'bx-info-circle'
    };
    
    // 1. Crear contenedor de toasts si no existe
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    // 2. Crear toast
    const toastId = 'toast-' + Date.now();
    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center text-white ${colores[tipo] || 'bg-secondary'} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bx ${iconos[tipo] || 'bx-info-circle'} me-2"></i>
                    ${mensaje}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    // 3. Mostrar toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 3000 // 3 segundos
    });
    
    toast.show();
    
    // 4. Eliminar del DOM después de ocultarse
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

// ==================
// EXPORTAR MÓDULO
// ==================

window.InformeAvanceModule = {
    registrarInformeConFetch,
    validarGerenteEnTiempoReal,
    validarLimiteImagenes,
    recargarTablaInformes,
    mostrarAlerta
};

console.log('✓✓✓ Módulo InformeAvanceModule exportado globalmente');