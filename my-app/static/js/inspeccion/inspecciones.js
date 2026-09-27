/**
 * inspecciones.js - Modulo para Inspecciones
 * Maneja la logica de validacion y comunicacion asincrona con Fetch/Ajax
 */

document.addEventListener('DOMContentLoaded', function () {
    console.log('[DEBUG] inspecciones.js cargado');
    const formInspeccion = document.getElementById('formInspeccion');
    const formInspeccionUpdate = document.getElementById('formInspeccionUpdate');

    cargarObras();
    cargarEvidenciasModal();
    cargarInspectores();

    if (formInspeccion) {
        formInspeccion.addEventListener('submit', function (event) {
            console.log('[DEBUG] Submit del formulario de inspeccion detectado');
            if (!validarEvidenciaSeleccionada()) {
                event.preventDefault();
                mostrarError('Seleccione una evidencia fotográfica.');
                return;
            }
            registrarInspeccionFetch(event).catch(err => {
                console.error('[DEBUG] Error en submit inspeccion:', err);
            });
        });
    }

    if (formInspeccionUpdate) {
        formInspeccionUpdate.addEventListener('submit', function (event) {
            console.log('[DEBUG] Submit del formulario de edicion detectado');
            if (!validarEvidenciaSeleccionada()) {
                event.preventDefault();
                mostrarError('Seleccione una evidencia fotográfica.');
                return;
            }
            actualizarInspeccionFetch(event).catch(err => {
                console.error('[DEBUG] Error en submit edicion:', err);
            });
        });
    }

    const inputObra = document.querySelector('select[name="obra_id_obra"]');
    if (inputObra) {
        inputObra.addEventListener('change', function () {
            if (this.value) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            }
        });
    }

    const inputInspector = document.querySelector('select[name="inspector"]');
    if (inputInspector) {
        inputInspector.addEventListener('change', function () {
            if (this.value) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            }
        });
    }

    var evidenciaInput = document.querySelector('input[name="evidencia_id_evidencia"]');
    if (evidenciaInput) {
        evidenciaInput.addEventListener('change', function () {
            if (this.value) {
                this.classList.remove('is-invalid');
            } else {
                this.classList.add('is-invalid');
            }
        });
    }
});

window.EVIDENCIA_PLACEHOLDER = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIwIiBoZWlnaHQ9IjEyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTIwIiBoZWlnaHQ9IjEyMCIgZmlsbD0iI2Y4ZjlmYSIvPjxudGV4dCB4PSI2MCIgeT0iNjUiIGZvbnQtZmFtaWx5PSJBcmlhbCxzYW5zLXNlcmlmIiBmb250LXNpemU9IjEyIiBmaWxsPSIjN2M4NzhjIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5TaW5fZXZpZGVuY2lhPC90ZXh0Pjwvc3ZnPg==';

function getEvidenciaImageUrl(path) {
    if (!path) return '';
    const strPath = String(path).trim();
    if (/^https?:\/\//i.test(strPath)) return strPath;
    if (strPath.includes('..') || strPath.includes('\x00') || strPath.includes('%00')) {
        console.warn('[SECURITY] Ruta de evidencia bloqueada:', strPath);
        return '';
    }
    let cleanPath = strPath.replace(/^\/+/, '').replace(/^static\//, '');
    if (!/^[a-zA-Z0-9_\-./]+$/.test(cleanPath)) {
        console.warn('[SECURITY] Ruta de evidencia con caracteres no permitidos:', strPath);
        return '';
    }
    return `/static/${cleanPath}`;
}

function escapeHtml(str) {
    if (str == null) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}

function escapeJs(str) {
    return String(str).replace(/\\/g, '\\\\').replace(/'/g, '\\\'');
}

async function cargarEvidenciasModal() {
    const evidenciaInput = document.getElementById('evidencia_id_evidencia');
    if (!evidenciaInput) return;

    window.__evidencias_inspeccion = [];
    window.__evidencias_seleccionadas = [];

    try {
        const response = await fetch('/inspecciones/api/evidencias/listar');
        if (!response.ok) {
            console.error('[EVIDENCIAS] Response error:', response.status);
            return;
        }
        const evidencias = await response.json();
        window.__evidencias_inspeccion = Array.isArray(evidencias) ? evidencias : [];
        renderizarEvidenciasEnModal();

        const evidenciaActual = evidenciaInput.value;
        const adicionalesInput = document.getElementById('evidencias_adicionales');
        const adicionalesValue = adicionalesInput ? adicionalesInput.value : '';

        const allIds = [];
        if (evidenciaActual) {
            allIds.push(parseInt(evidenciaActual, 10));
        }
        if (adicionalesValue) {
            adicionalesValue.split(',').forEach(v => {
                const n = parseInt(v, 10);
                if (!isNaN(n)) allIds.push(n);
            });
        }
        allIds.filter((v, i, a) => a.indexOf(v) === i);

        if (allIds.length > 0) {
            window.__evidencias_seleccionadas = allIds;
            actualizarDisplayEvidencias();
            actualizarPreviewEvidencia();
        }
    } catch (error) {
        console.error('[EVIDENCIAS] Error al cargar evidencias:', error);
        window.__evidencias_inspeccion = [];
    }
}

function renderizarEvidenciasEnModal() {
    const container = document.getElementById('listaEvidenciasInspeccion');
    if (!container) return;
    const evidencias = window.__evidencias_inspeccion || [];
    const seleccionadas = window.__evidencias_seleccionadas || [];

    if (evidencias.length === 0) {
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="bi bi-image-alt" style="font-size: 3rem;" class="text-muted mb-3"></i>
                <p class="text-muted">No hay evidencias registradas en el sistema.</p>
                <small class="text-muted">Registre evidencias en el módulo de Evidencias.</small>
            </div>`;
        return;
    }

    container.innerHTML = evidencias.map(ev => {
        const isSelected = seleccionadas.includes(ev.id_evidencia);
        return `
            <div class="col-md-3 mb-3">
              <div class="card modal-evidencia-item h-100 ${isSelected ? 'selected' : ''}"
                   data-id="${ev.id_evidencia}"
                   onclick="seleccionarEvidenciaModal(${ev.id_evidencia})">
                <div class="position-relative">
                  <img src="${getEvidenciaImageUrl(ev.url_archivos)}"
                       alt="${escapeHtml(ev.fotos)}" class="card-img-top"
                       onerror="this.src=window.EVIDENCIA_PLACEHOLDER; this.onerror=null;" />
                  <span class="badge bg-info text-dark position-absolute top-0 start-0 m-2"
                        style="font-size:0.7rem;">
                    <i class="bi bi-tag"></i> ${escapeHtml(ev.etapa || 'Sin etapa')}
                  </span>
                  <i class="bi bi-check-circle-fill text-success position-absolute top-0 end-0 m-2 ${isSelected ? '' : 'd-none'}"
                     style="font-size:1.5rem;"></i>
                </div>
                <div class="card-body p-2">
                  <p class="mb-1 small text-truncate" title="${escapeHtml(ev.fotos)}">
                    <i class="bi bi-file-earmark me-1"></i>#${ev.id_evidencia} - ${escapeHtml(ev.fotos || 'Sin nombre')}
                  </p>
                  <small class="text-muted d-block">
                    <i class="bi bi-calendar me-1"></i>${ev.fecha_registro ? new Date(ev.fecha_registro).toLocaleDateString('es-VE') : 'N/A'}
                  </small>
                </div>
              </div>
            </div>`;
    }).join('');
}

window.__evidencias_seleccionadas = [];
window.__evidencias_inspeccion = [];

function seleccionarEvidenciaModal(id) {
    const evidencias = window.__evidencias_inspeccion || [];
    const evidencia = evidencias.find(e => e.id_evidencia === id);
    if (!evidencia) return;

    const MAX = 10;
    const index = window.__evidencias_seleccionadas.indexOf(id);
    if (index > -1) {
        window.__evidencias_seleccionadas.splice(index, 1);
    } else {
        if (window.__evidencias_seleccionadas.length >= MAX) {
            Swal.fire({
                icon: 'warning',
                title: 'Limite alcanzado',
                text: `Solo puede seleccionar un maximo de ${MAX} evidencias.`,
            });
            return;
        }
        window.__evidencias_seleccionadas.push(id);
    }

    const input = document.getElementById('evidencia_id_evidencia');
    const adicionalesInput = document.getElementById('evidencias_adicionales');
    if (input) {
        input.value = window.__evidencias_seleccionadas[0] || '';
        input.classList.toggle('is-invalid', !input.value);
    }
    if (adicionalesInput) {
        adicionalesInput.value = window.__evidencias_seleccionadas.slice(1).join(',');
    }

    const card = document.querySelector(`.modal-evidencia-item[data-id="${id}"]`);
    if (card) {
        card.classList.toggle('selected');
        const icon = card.querySelector('.bi-check-circle-fill');
        if (icon) {
            if (window.__evidencias_seleccionadas.includes(id)) {
                icon.classList.remove('d-none');
            } else {
                icon.classList.add('d-none');
            }
        }
    }

    actualizarDisplayEvidencias();
    actualizarPreviewEvidencia();
}

function actualizarDisplayEvidencias() {
    const display = document.getElementById('evidenciaDisplay');
    const seleccionadas = window.__evidencias_seleccionadas || [];
    if (!display) return;

    if (seleccionadas.length === 0) {
        display.value = '';
        return;
    }

    const evidencias = window.__evidencias_inspeccion || [];
    const labels = seleccionadas.map(id => {
        const ev = evidencias.find(e => e.id_evidencia === id);
        return ev ? `#${ev.id_evidencia}` : `#${id}`;
    });
    display.value = `${seleccionadas.length} evidencia(s) seleccionada(s): ${labels.join(', ')}`;
}

function actualizarPreviewEvidencia() {
    const container = document.getElementById('previewEvidenciaInspeccion');
    if (!container) return;
    const evidencias = window.__evidencias_inspeccion || [];
    const seleccionadas = window.__evidencias_seleccionadas || [];

    if (seleccionadas.length === 0) {
        container.innerHTML = '';
        return;
    }

    container.innerHTML = '';
    seleccionadas.forEach(id => {
        const evidencia = evidencias.find(e => e.id_evidencia === id);
        if (!evidencia) return;
        const item = document.createElement('div');
        item.className = 'preview-evidencia-item';
        item.innerHTML = `
            <img src="${getEvidenciaImageUrl(evidencia.url_archivos)}"
                 alt="${escapeHtml(evidencia.fotos)}"
                 onerror="this.src=window.EVIDENCIA_PLACEHOLDER; this.onerror=null;" />
            <div class="remove-btn" onclick="removerEvidenciaSeleccionada(${id})">
                <i class="bi bi-x"></i>
            </div>`;
        container.appendChild(item);
    });
}

function removerEvidenciaSeleccionada(id) {
    const index = window.__evidencias_seleccionadas.indexOf(id);
    if (index > -1) {
        window.__evidencias_seleccionadas.splice(index, 1);

        const input = document.getElementById('evidencia_id_evidencia');
        const adicionalesInput = document.getElementById('evidencias_adicionales');
        if (input) {
            input.value = window.__evidencias_seleccionadas[0] || '';
            input.classList.toggle('is-invalid', !input.value);
        }
        if (adicionalesInput) {
            adicionalesInput.value = window.__evidencias_seleccionadas.slice(1).join(',');
        }

        document.querySelectorAll('.modal-evidencia-item').forEach(card => {
            card.classList.remove('selected');
            const icon = card.querySelector('.bi-check-circle-fill');
            if (icon) icon.classList.add('d-none');
        });
        window.__evidencias_seleccionadas.forEach(selId => {
            const card = document.querySelector(`.modal-evidencia-item[data-id="${selId}"]`);
            if (card) {
                card.classList.add('selected');
                const icon = card.querySelector('.bi-check-circle-fill');
                if (icon) icon.classList.remove('d-none');
            }
        });

        actualizarDisplayEvidencias();
        actualizarPreviewEvidencia();
    }
}

function validarEvidenciaSeleccionada() {
    const input = document.getElementById('evidencia_id_evidencia');
    if (!input || !input.value) {
        const feedback = document.getElementById('evidenciaFeedback');
        if (feedback) feedback.style.display = 'block';
        return false;
    }
    const feedback = document.getElementById('evidenciaFeedback');
    if (feedback) feedback.style.display = 'none';
    return true;
}

function cerrarModalEvidencia() {
    const modalEl = document.getElementById('modalEvidenciasInspeccion');
    if (modalEl) {
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
    }
}

function confirmarEvidenciaSeleccionada() {
    if (!window.__evidencias_seleccionadas || window.__evidencias_seleccionadas.length === 0) {
        Swal.fire({
            icon: 'warning',
            title: 'Sin seleccion',
            text: 'Debe seleccionar al menos una evidencia antes de confirmar.',
        });
        return;
    }
    cerrarModalEvidencia();
}

async function cargarObras() {
    const selectObra = document.querySelector('select[name="obra_id_obra"]');
    if (!selectObra) return;

    try {
        const response = await fetch('/inspecciones/api/obras/listar');
        const obras = await response.json();

        selectObra.innerHTML = '<option value="" disabled selected>Seleccione obra...</option>';

        obras.forEach(obra => {
            const option = document.createElement('option');
            option.value = obra.id_obra;
            option.textContent = `#${obra.id_obra} - ${obra.titulo_obra} (${obra.ubicacion_obra})`;
            selectObra.appendChild(option);
        });

        const obraActual = selectObra.getAttribute('data-value');
        if (obraActual) {
            selectObra.value = obraActual;
        }

        selectObra.disabled = false;
    } catch (error) {
        console.error('Error al cargar obras:', error);
        selectObra.innerHTML = '<option value="" disabled selected>Error al cargar obras</option>';
    }
}

async function cargarInspectores() {
    const selectInspector = document.querySelector('select[name="inspector"]');
    if (!selectInspector) {
        console.warn('[INSPECTORES] select inspector no encontrado en el DOM');
        return;
    }

    try {
        const response = await fetch('/inspecciones/api/inspectores/listar');
        console.log('[INSPECTORES] Response status:', response.status);

        if (!response.ok) {
            const text = await response.text();
            console.error('[INSPECTORES] Response error:', response.status, text);
            selectInspector.innerHTML = '<option value="" disabled selected>Error de conexion</option>';
            selectInspector.disabled = true;
            return;
        }

        const inspectores = await response.json();
        console.log('[INSPECTORES] Datos recibidos:', inspectores);

        selectInspector.innerHTML = '<option value="" disabled selected>Seleccione inspector...</option>';

        if (!inspectores || inspectores.length === 0) {
            const option = document.createElement('option');
            option.value = "";
            option.textContent = "No hay inspectores disponibles";
            option.disabled = true;
            selectInspector.appendChild(option);
            selectInspector.disabled = true;
            return;
        }

        inspectores.forEach(inspector => {
            const option = document.createElement('option');
            option.value = inspector.id_empleados;
            option.textContent = inspector.nombre_empleado;
            selectInspector.appendChild(option);
        });

        const inspectorActual = selectInspector.getAttribute('data-value');
        if (inspectorActual) {
            selectInspector.value = inspectorActual;
        }

        selectInspector.disabled = false;
        console.log('[INSPECTORES] Select poblado con', inspectores.length, 'inspectores');
    } catch (error) {
        console.error('[INSPECTORES] Error al cargar inspectores:', error);
        selectInspector.innerHTML = '<option value="" disabled selected>Error al cargar inspectores</option>';
        selectInspector.disabled = true;
    }
}

async function registrarInspeccionFetch(event) {
    event.preventDefault();
    console.log('[DEBUG] registrarInspeccionFetch llamado');

    const form = event.target;

    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        const primerCampoInvalido = form.querySelector(':invalid');
        if (primerCampoInvalido) {
            primerCampoInvalido.focus();
        }
        mostrarError('Complete todos los campos correctamente.');
        return;
    }

    const btnGuardar = document.getElementById('btnGuardarInspeccion');
    const formData = new FormData(form);
    console.log('[DEBUG] FormData listo para enviar');

    btnGuardar.disabled = true;
    btnGuardar.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Guardando...';

    try {
        const response = await fetch('/inspecciones/api/crear', {
            method: 'POST',
            body: formData
        });
        console.log('[DEBUG] Response status:', response.status);
        const result = await response.json();
        console.log('[DEBUG] Response body:', result);

        if (result.status === 'success') {
            mostrarExito(result.message);
            setTimeout(() => {
                window.location.href = '/inspecciones/';
            }, 1500);
        } else {
            mostrarError('Error: ' + result.message);
            btnGuardar.disabled = false;
            btnGuardar.innerHTML = '<i class="bi bi-check-circle me-1"></i>Registrar Inspeccion';
        }
    } catch (error) {
        console.error('[DEBUG] Error al registrar inspeccion:', error);
        mostrarError('Error de conexion con el servidor.');
        btnGuardar.disabled = false;
        btnGuardar.innerHTML = '<i class="bi bi-check-circle me-1"></i>Registrar Inspeccion';
    }
}

async function actualizarInspeccionFetch(event) {
    event.preventDefault();
    console.log('[DEBUG] actualizarInspeccionFetch llamado');

    const form = event.target;

    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        const primerCampoInvalido = form.querySelector(':invalid');
        if (primerCampoInvalido) {
            primerCampoInvalido.focus();
        }
        mostrarError('Complete todos los campos correctamente.');
        return;
    }

    const btnActualizar = document.getElementById('btnActualizarInspeccion');
    const formData = new FormData(form);
    const idInspeccion = formData.get('id_inspeccion');
    console.log('[DEBUG] Actualizando inspeccion ID:', idInspeccion);

    try {
        const existeResponse = await fetch(`/inspecciones/api/validar/${idInspeccion}`);
        const existeData = await existeResponse.json();
        console.log('[DEBUG] Validacion existencia:', existeData);

        if (!existeData.existe) {
            mostrarError('La inspeccion no existe o fue eliminada.');
            return;
        }
    } catch (error) {
        console.error('[DEBUG] Error al validar inspeccion:', error);
        mostrarError('Error de conexion.');
        return;
    }

    btnActualizar.disabled = true;
    btnActualizar.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Actualizando...';

    try {
        const response = await fetch(`/inspecciones/api/actualizar/${idInspeccion}`, {
            method: 'POST',
            body: formData
        });
        console.log('[DEBUG] Response status:', response.status);
        const result = await response.json();
        console.log('[DEBUG] Response body:', result);

        if (result.status === 'success') {
            mostrarExito(result.message);
            setTimeout(() => {
                window.location.href = '/inspecciones/';
            }, 1500);
        } else {
            mostrarError('Error: ' + result.message);
            btnActualizar.disabled = false;
            btnActualizar.innerHTML = '<i class="bi bi-arrow-repeat me-1"></i>Actualizar Informacion';
        }
    } catch (error) {
        console.error('[DEBUG] Error al actualizar inspeccion:', error);
        mostrarError('Error de conexion con el servidor.');
        btnActualizar.disabled = false;
        btnActualizar.innerHTML = '<i class="bi bi-arrow-repeat me-1"></i>Actualizar Informacion';
    }
}

function eliminarInspeccionJS(id_inspeccion) {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: 'Estas seguro?',
            text: "La inspeccion sera desactivada (borrado logico).",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Si, desactivar',
            cancelButtonText: 'Cancelar',
            reverseButtons: true
        }).then((result) => {
            if (result.isConfirmed) {
                fetch(`/inspecciones/eliminar/${id_inspeccion}`)
                    .then(function(response) { return response.json(); })
                    .then(function(data) {
                        if (data && data.status === 'success') {
                            Swal.fire({
                                icon: 'success',
                                title: '¡Éxito!',
                                text: data.message || 'Inspección desactivada.',
                                timer: 1500,
                                showConfirmButton: false
                            });
                            var row = document.querySelector(`tr[data-id-inspeccion="${id_inspeccion}"]`);
                            if (row) {
                                row.style.transition = 'opacity 0.4s';
                                row.style.opacity = '0';
                                setTimeout(function() { row.remove(); }, 400);
                            } else if (window.INVISAP_AJAX) {
                                window.INVISAP_AJAX.refrescarListadoActual('tablaInspecciones', { origen: 'inspecciones' });
                            } else {
                                setTimeout(function() { location.reload(); }, 1200);
                            }
                        } else {
                            Swal.fire({
                                icon: 'error',
                                title: 'Error',
                                text: (data && data.message) || 'No se pudo desactivar.'
                            });
                        }
                    })
                    .catch(function() {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: 'Error de conexión con el servidor.'
                        });
                    });
            }
        });
    } else {
        if (confirm("Estas seguro de desactivar esta inspeccion?")) {
            fetch(`/inspecciones/eliminar/${id_inspeccion}`)
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    if (data && data.status === 'success') {
                        alert('Inspección desactivada correctamente.');
                        var row = document.querySelector(`tr[data-id-inspeccion="${id_inspeccion}"]`);
                        if (row) {
                            row.style.transition = 'opacity 0.4s';
                            row.style.opacity = '0';
                            setTimeout(function() { row.remove(); }, 400);
                        } else if (window.INVISAP_AJAX) {
                            window.INVISAP_AJAX.refrescarListadoActual('tablaInspecciones', { origen: 'inspecciones' });
                        } else {
                            setTimeout(function() { location.reload(); }, 800);
                        }
                    } else {
                        alert((data && data.message) || 'No se pudo desactivar.');
                    }
                })
                .catch(function() {
                    alert('Error de conexión');
                });
        }
    }
}

function mostrarExito(mensaje) {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            icon: 'success',
            title: 'Exito!',
            text: mensaje,
            timer: 2000,
            showConfirmButton: false
        });
    } else {
        alert(mensaje);
    }
}

function mostrarError(mensaje) {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: mensaje
        });
    } else {
        alert(mensaje);
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        registrarInspeccionFetch,
        actualizarInspeccionFetch,
        eliminarInspeccionJS,
        cargarObras,
        cargarEvidenciasModal,
        getEvidenciaImageUrl,
        escapeHtml,
        escapeJs
    };
}
