// Script para validaciones Regex Frontend y peticiones AJAX (SPA)
let todasLasSolicitudes = [];
let paginaActual = 1;
let registrosPorPagina = 5;
let busquedaActual = '';

function renderizarSolicitudes(solicitudes) {
    const tbody = document.querySelector('#tbody_solicitudes');
    tbody.innerHTML = '';

    if (solicitudes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4">No hay solicitudes registradas.</td></tr>';
        document.getElementById('widget-pendientes').innerText = 0;
        document.getElementById('widget-en-proceso').innerText = 0;
        document.getElementById('widget-completadas').innerText = 0;
        document.getElementById('widget-total').innerText = 0;
        document.getElementById('pagination_container').style.display = 'none';
        return;
    }

    const inicio = (paginaActual - 1) * registrosPorPagina;
    const fin = Math.min(inicio + registrosPorPagina, solicitudes.length);
    const paginaSolicitudes = solicitudes.slice(inicio, fin);

    let html = '';
    paginaSolicitudes.forEach(s => {
        let badgeEstatus = '';
        if (s.estatus_solicitud === 'Pendiente') {
            badgeEstatus = '<span class="badge rounded-pill bg-warning text-dark"><i class="bi bi-clock-history me-1"></i>Pendiente</span>';
        } else if (s.estatus_solicitud === 'En Proceso') {
            badgeEstatus = '<span class="badge rounded-pill bg-primary"><i class="bi bi-arrow-repeat me-1"></i>En Proceso</span>';
        } else if (s.estatus_solicitud === 'Completada' || s.estatus_solicitud === 'Procesada') {
            badgeEstatus = '<span class="badge rounded-pill bg-success"><i class="bi bi-check-circle me-1"></i>Completada</span>';
        } else {
            badgeEstatus = `<span class="badge rounded-pill bg-secondary">${s.estatus_solicitud}</span>`;
        }

        html += `<tr id="solicitud_${s.id_solicitud}">
            <td class="text-muted fw-semibold">#${s.id_solicitud}</td>
            <td>
              <div class="d-flex flex-column">
                <span class="fw-bold">${s.nombre_solicitante || '—'}</span>
                <small class="text-muted">C.I: ${s.cedula_persona || '—'}</small>
              </div>
            </td>
            <td>
              <span class="badge bg-light text-dark border"><i class="bi bi-tag me-1"></i>${s.tipo_solicitud}</span>
            </td>
            <td>
              ${badgeEstatus}
            </td>
            <td style="max-width:200px; white-space:normal;">${s.problematica}</td>
            <td>${s.fecha_formateada || s.fecha}</td>
            <td width="10px" class="text-nowrap">
              <div class="d-flex gap-1">
                <a href="/detalles-solicitud/${s.id_solicitud}" class="btn btn-info btn-sm" title="Ver detalles">
                  <i class="bi bi-eye"></i>
                </a>
                <button type="button" class="btn btn-warning btn-sm" title="Editar solicitud" onclick="abrirModalEditar(${s.id_solicitud});">
                  <i class="bi bi-pencil-square"></i>
                </button>
                <a href="javascript:void(0);" class="btn btn-danger btn-sm" title="Eliminar solicitud" onclick="eliminarSolicitudAjax(${s.id_solicitud});">
                  <i class="bi bi-trash"></i>
                </a>
              </div>
            </td>
          </tr>`;
    });

    tbody.innerHTML = html;

    const totalPaginas = Math.ceil(solicitudes.length / registrosPorPagina);
    document.getElementById('info_registros').textContent = `Mostrando ${inicio + 1} a ${fin} de ${solicitudes.length} registros`;
    renderizarControlesPaginacion(totalPaginas);
    document.getElementById('pagination_container').style.display = 'flex';
}

function renderizarControlesPaginacion(totalPaginas) {
    const controls = document.getElementById('pagination_controls');
    controls.innerHTML = '';

    const botonAnterior = document.createElement('li');
    botonAnterior.className = `page-item ${paginaActual === 1 ? 'disabled' : ''}`;
    botonAnterior.innerHTML = `<button class="page-link" onclick="cambiarPagina(${paginaActual - 1})">Anterior</button>`;
    controls.appendChild(botonAnterior);

    for (let i = 1; i <= totalPaginas; i++) {
        const li = document.createElement('li');
        li.className = `page-item ${i === paginaActual ? 'active' : ''}`;
        li.innerHTML = `<button class="page-link" onclick="cambiarPagina(${i})">${i}</button>`;
        controls.appendChild(li);
    }

    const botonSiguiente = document.createElement('li');
    botonSiguiente.className = `page-item ${paginaActual === totalPaginas ? 'disabled' : ''}`;
    botonSiguiente.innerHTML = `<button class="page-link" onclick="cambiarPagina(${paginaActual + 1})">Siguiente</button>`;
    controls.appendChild(botonSiguiente);
}

window.cambiarPagina = function(nuevaPagina) {
    const totalPaginas = Math.ceil(todasLasSolicitudes.length / registrosPorPagina);
    if (nuevaPagina < 1 || nuevaPagina > totalPaginas) return;
    paginaActual = nuevaPagina;
    aplicarBusquedaYRenderizar();
    document.getElementById('registros_por_pagina').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
};

window.buscarSolicitudes = function(termino) {
    busquedaActual = termino;
    paginaActual = 1;
    aplicarBusquedaYRenderizar();
};

function aplicarBusquedaYRenderizar() {
    let solicitudesFiltradas = todasLasSolicitudes;
    if (busquedaActual.trim()) {
        const term = busquedaActual.toLowerCase();
        solicitudesFiltradas = solicitudesFiltradas.filter(s =>
            (s.nombre_solicitante && s.nombre_solicitante.toLowerCase().includes(term)) ||
            (s.cedula_persona && s.cedula_persona.includes(term)) ||
            (s.tipo_solicitud && s.tipo_solicitud.toLowerCase().includes(term)) ||
            (s.problematica && s.problematica.toLowerCase().includes(term)) ||
            (`#${s.id_solicitud}`.includes(term))
        );
    }
    renderizarSolicitudes(solicitudesFiltradas);
}

function cargarSolicitudes() {
    fetch('/api/obtener-solicitudes-json')
        .then(res => res.json())
        .then(data => {
            todasLasSolicitudes = Array.isArray(data) ? data : [];
            paginaActual = 1;
            busquedaActual = '';
            const searchInput = document.getElementById('search');
            if (searchInput) searchInput.value = '';
            actualizarEstadisticas(todasLasSolicitudes);
            renderizarSolicitudes(todasLasSolicitudes);
        })
        .catch(err => {
            console.error('Error recargando tabla:', err);
            if (!todasLasSolicitudes.length && window.__SOLICITUDES_INICIALES__) {
                todasLasSolicitudes = window.__SOLICITUDES_INICIALES__;
                actualizarEstadisticas(todasLasSolicitudes);
                renderizarSolicitudes(todasLasSolicitudes);
            }
        });
}

function actualizarEstadisticas(solicitudes) {
    let contPendiente = 0;
    let contProceso = 0;
    let contCompletada = 0;
    solicitudes.forEach(s => {
        if (s.estatus_solicitud === 'Pendiente') contPendiente++;
        else if (s.estatus_solicitud === 'En Proceso') contProceso++;
        else if (s.estatus_solicitud === 'Completada' || s.estatus_solicitud === 'Procesada') contCompletada++;
    });
    document.getElementById('widget-pendientes').innerText = contPendiente;
    document.getElementById('widget-en-proceso').innerText = contProceso;
    document.getElementById('widget-completadas').innerText = contCompletada;
    document.getElementById('widget-total').innerText = solicitudes.length;
}

document.addEventListener("DOMContentLoaded", function() {
    const formCrearSolicitud = document.getElementById('formCrearSolicitud');
    if (formCrearSolicitud) {
        formCrearSolicitud.addEventListener("submit", async function(e) {
            e.preventDefault();
            await procesarFormulario(formCrearSolicitud, '/api/solicitudes/crear', 'POST', 'modalCrearSolicitud');
        });
    }

    const formEditarSolicitud = document.getElementById('formEditarSolicitud');
    if (formEditarSolicitud) {
        formEditarSolicitud.addEventListener("submit", async function(e) {
            e.preventDefault();
            await procesarFormulario(formEditarSolicitud, '/api/solicitudes/actualizar', 'PUT', 'modalEditarSolicitud');
        });
    }

    const selectRegistros = document.getElementById('registros_por_pagina');
    if (selectRegistros) {
        selectRegistros.value = registrosPorPagina;
        selectRegistros.addEventListener('change', function() {
            registrosPorPagina = parseInt(this.value);
            paginaActual = 1;
            aplicarBusquedaYRenderizar();
        });
    }

    cargarSolicitudes();
});

async function procesarFormulario(form, url, method, modalId) {
    const cedulaInputs = form.querySelectorAll('input[name$="_cedula"]');
    const telefonoInputs = form.querySelectorAll('input[name$="_telefono"]');
    const problematicaInput = form.querySelector('textarea[name="problematica"]');
    
    let cedulaValida = true;
    cedulaInputs.forEach(input => {
        if (!input.disabled && input.value) {
            if (!/^\d{7,10}$/.test(input.value)) {
                if (typeof Swal !== 'undefined') {
                    Swal.fire('Atención', 'Cédula inválida. Debe tener entre 7 y 10 dígitos numéricos.', 'warning');
                } else {
                    alert("Cédula inválida. Debe tener entre 7 y 10 dígitos numéricos.");
                }
                input.focus();
                cedulaValida = false;
            }
        }
    });
    if (!cedulaValida) return;

    let telValido = true;
    telefonoInputs.forEach(input => {
        if (!input.disabled && input.value) {
                    if (!/^(0414|0424|0412|0416|0426|0251|0212)-?\d{7}$/.test(input.value)) {
                        if (typeof Swal !== 'undefined') {
                            Swal.fire('Teléfono Inválido', 'Formato inválido. Use 0424-1234567 o 04241234567.', 'warning');
                        } else {
                            alert("Teléfono inválido. Use Ej.: 0424-1234567 o 04241234567");
                        }
                input.focus();
                telValido = false;
            }
        }
    });
    if (!telValido) return;

    if (problematicaInput && problematicaInput.value.trim().length < 15) {
        if (typeof Swal !== 'undefined') {
            Swal.fire('Atención', 'La problemática debe tener al menos 15 caracteres para ser descriptiva.', 'warning');
        } else {
            alert("La problemática debe tener al menos 15 caracteres.");
        }
        problematicaInput.focus();
        return;
    }

    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    try {
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Procesando...';
        submitBtn.disabled = true;

        const response = await fetch(url, {
            method: method,
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok && result.status === 'success') {
            var myModalEl = document.getElementById(modalId);
            var modal = bootstrap.Modal.getInstance(myModalEl);
            if (modal) {
                modal.hide();
            }
            
            if(modalId === 'modalCrearSolicitud') form.reset();

            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    icon: 'success',
                    title: '¡Éxito!',
                    text: result.message,
                    timer: 2000,
                    showConfirmButton: false
                });
            } else {
                alert("¡Éxito! " + result.message);
            }
            
            await cargarSolicitudes();
            
        } else {
            if (typeof Swal !== 'undefined') {
                Swal.fire('Error', result.message, 'error');
            } else {
                alert("Error: " + result.message);
            }
        }
    } catch (error) {
        console.error("Error en la petición:", error);
        alert("Ocurrió un error inesperado al enviar la solicitud.");
    } finally {
        if (submitBtn) {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }
}

// 3. Función para eliminar vía AJAX
window.eliminarSolicitudAjax = async function(id_solicitud) {
    if (typeof Swal !== 'undefined') {
        const result = await Swal.fire({
            title: '¿Estás seguro?',
            text: "Esta acción no se puede deshacer.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar'
        });
        
        if (!result.isConfirmed) return;
    } else {
        if (!confirm('¿Estás seguro de que deseas eliminar esta solicitud? Esta acción no se puede deshacer.')) return;
    }

    try {
        const response = await fetch(`/api/solicitudes/eliminar/${id_solicitud}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok && result.status === 'success') {
            if (typeof Swal !== 'undefined') {
                Swal.fire('Eliminada', result.message, 'success');
            } else {
                alert(result.message);
            }
            await cargarSolicitudes();
        } else {
            if (typeof Swal !== 'undefined') {
                Swal.fire('Error', result.message, 'error');
            } else {
                alert("Error: " + result.message);
            }
        }
    } catch (error) {
        console.error("Error al eliminar:", error);
        alert("Ocurrió un error inesperado al intentar eliminar la solicitud.");
    }
}

// 4. Función para cargar datos al Modal de Editar
window.abrirModalEditar = async function(id_solicitud) {
    try {
        const response = await fetch(`/api/solicitudes/${id_solicitud}`);
        const result = await response.json();
        
        if (response.ok && result.status === 'success') {
            const data = result.data;
            document.getElementById('edit_id_solicitud').value = data.id_solicitud;
            document.getElementById('edit_solicitud_id_title').innerText = `#${data.id_solicitud}`;
            document.getElementById('edit_estatus_solicitud').value = data.estatus_solicitud;
            document.getElementById('edit_problematica').value = data.problematica;
            
            var editModal = new bootstrap.Modal(document.getElementById('modalEditarSolicitud'));
            editModal.show();
        } else {
            alert("No se pudo cargar la información de la solicitud.");
        }
    } catch(err) {
        console.error(err);
        alert("Error de conexión.");
    }
}
