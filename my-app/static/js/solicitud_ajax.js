// Script para validaciones Regex Frontend y peticiones AJAX (SPA)
document.addEventListener("DOMContentLoaded", function() {

    // 1. Manejo del formulario de crear solicitud
    const formCrearSolicitud = document.getElementById('formCrearSolicitud');
    if (formCrearSolicitud) {
        formCrearSolicitud.addEventListener("submit", async function(e) {
            e.preventDefault();
            await procesarFormulario(formCrearSolicitud, '/api/solicitudes/crear', 'POST', 'modalCrearSolicitud');
        });
    }

    // 2. Manejo del formulario de editar solicitud
    const formEditarSolicitud = document.getElementById('formEditarSolicitud');
    if (formEditarSolicitud) {
        formEditarSolicitud.addEventListener("submit", async function(e) {
            e.preventDefault();
            await procesarFormulario(formEditarSolicitud, '/api/solicitudes/actualizar', 'PUT', 'modalEditarSolicitud');
        });
    }

    async function procesarFormulario(form, url, method, modalId) {
        // Validaciones Regex Frontend 
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
                // Cerrar modal actual
                var myModalEl = document.getElementById(modalId);
                var modal = bootstrap.Modal.getInstance(myModalEl);
                if (modal) {
                    modal.hide();
                }
                
                // Limpiar formulario si es crear
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
                
                // Recargar tabla
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

});

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
            
            // Mostrar modal
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

// 5. Función para recargar la tabla dinámicamente
window.cargarSolicitudes = async function() {
    try {
        const response = await fetch('/api/obtener-solicitudes-json');
        const solicitudes = await response.json();
        
        // Actualizar estadísticas (Widgets)
        let contPendiente = 0;
        let contProceso = 0;
        let contCompletada = 0;
        
        const tbody = document.querySelector('#tbl_solicitudes tbody');
        tbody.innerHTML = '';
        
        if (solicitudes.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4">No hay solicitudes registradas.</td></tr>';
            document.getElementById('widget-pendientes').innerText = 0;
            document.getElementById('widget-en-proceso').innerText = 0;
            document.getElementById('widget-completadas').innerText = 0;
            document.getElementById('widget-total').innerText = 0;
            return;
        }
        
        let html = '';
        solicitudes.forEach(s => {
            // Contar para widgets
            if (s.estatus_solicitud === 'Pendiente') contPendiente++;
            else if (s.estatus_solicitud === 'En Proceso') contProceso++;
            else if (s.estatus_solicitud === 'Completada' || s.estatus_solicitud === 'Procesada') contCompletada++;

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
        
        // Renderizar valores en el DOM
        document.getElementById('widget-pendientes').innerText = contPendiente;
        document.getElementById('widget-en-proceso').innerText = contProceso;
        document.getElementById('widget-completadas').innerText = contCompletada;
        document.getElementById('widget-total').innerText = solicitudes.length;
        
    } catch(err) {
        console.error('Error recargando tabla:', err);
    }
}
