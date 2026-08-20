/**
 * inspecciones.js - Modulo para Inspecciones
 * Maneja la logica de validacion y comunicacion asincrona con Fetch/Ajax
 */

document.addEventListener('DOMContentLoaded', function () {
    console.log('[DEBUG] inspecciones.js cargado');
    const formInspeccion = document.getElementById('formInspeccion');
    const formInspeccionUpdate = document.getElementById('formInspeccionUpdate');

    cargarObras();
    cargarEvidencias();
    cargarInspectores();

    if (formInspeccion) {
        formInspeccion.addEventListener('submit', function (event) {
            console.log('[DEBUG] Submit del formulario de inspeccion detectado');
            registrarInspeccionFetch(event).catch(err => {
                console.error('[DEBUG] Error en submit inspeccion:', err);
            });
        });
    }

    if (formInspeccionUpdate) {
        formInspeccionUpdate.addEventListener('submit', function (event) {
            console.log('[DEBUG] Submit del formulario de edicion detectado');
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

    const inputEvidencia = document.querySelector('select[name="evidencia_id_evidencia"]');
    if (inputEvidencia) {
        inputEvidencia.addEventListener('change', function () {
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
});

async function cargarEvidencias() {
    const selectEvidencia = document.querySelector('select[name="evidencia_id_evidencia"]');
    if (!selectEvidencia) {
        console.warn('[EVIDENCIAS] select evidencia no encontrado en el DOM');
        return;
    }

    try {
        const response = await fetch('/inspecciones/api/evidencias/listar');
        console.log('[EVIDENCIAS] Response status:', response.status);

        if (!response.ok) {
            const text = await response.text();
            console.error('[EVIDENCIAS] Response error:', response.status, text);
            selectEvidencia.innerHTML = '<option value="" disabled selected>Error de conexion</option>';
            selectEvidencia.disabled = true;
            return;
        }

        const evidencias = await response.json();
        console.log('[EVIDENCIAS] Datos recibidos:', evidencias);

        selectEvidencia.innerHTML = '<option value="" disabled selected>Seleccione evidencia...</option>';

        if (!evidencias || evidencias.length === 0) {
            const option = document.createElement('option');
            option.value = "";
            option.textContent = "No hay evidencias disponibles";
            option.disabled = true;
            selectEvidencia.appendChild(option);
            selectEvidencia.disabled = true;
            return;
        }

        evidencias.forEach(evidencia => {
            const option = document.createElement('option');
            option.value = evidencia.id_evidencia;
            option.textContent = `#${evidencia.id_evidencia} - ${evidencia.etapa || 'Sin etapa'}`;
            selectEvidencia.appendChild(option);
        });

        const evidenciaActual = selectEvidencia.getAttribute('data-value');
        if (evidenciaActual) {
            selectEvidencia.value = evidenciaActual;
        }

        selectEvidencia.disabled = false;
        console.log('[EVIDENCIAS] Select poblado con', evidencias.length, 'evidencias');
    } catch (error) {
        console.error('[EVIDENCIAS] Error al cargar evidencias:', error);
        selectEvidencia.innerHTML = '<option value="" disabled selected>Error al cargar evidencias</option>';
        selectEvidencia.disabled = true;
    }
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
        cargarEvidencias
    };
}
