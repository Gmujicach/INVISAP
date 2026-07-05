// --- FUNCIÓN DE REGISTRO ---
function formatFecha(fecha) {
    if (!fecha) return '—';
    if (typeof fecha === 'string' && fecha.includes('-')) {
        return fecha;
    }
    const d = new Date(fecha);
    if (isNaN(d.getTime())) return fecha;
    const año = d.getFullYear();
    const mes = String(d.getMonth() + 1).padStart(2, '0');
    const dia = String(d.getDate()).padStart(2, '0');
    const hora = String(d.getHours()).padStart(2, '0');
    const min = String(d.getMinutes()).padStart(2, '0');
    const seg = String(d.getSeconds()).padStart(2, '0');
    return `${año}-${mes}-${dia} ${hora}:${min}:${seg}`;
}

document.getElementById('btnGuardarProyecto').addEventListener('click', function() {
    const form = document.getElementById('formRegistrarProyecto');
    if (!form) return;

    const solicitudId = document.getElementById('solicitud_id_p');
    const errorSolicitudDiv = document.getElementById('solicitud_error_message');
    const fechaPlan = document.getElementById('fecha_p');
    const observaciones = document.getElementById('observaciones');
    const codigoProyecto = document.getElementById('Codigo_p');
    const maquinaria = document.getElementById('maquinaria_p');
    const computos = document.getElementById('computos_p');
    const estimacion = document.getElementById('estimacion_p');

    function marcarInvalidoCustom(input, mensaje) {
        if (!input) return;
        input.classList.add('is-invalid');
        let cont = input.parentElement;
        while (cont && !cont.classList.contains('col-md-6') && !cont.classList.contains('col-md-4') && !cont.classList.contains('form-group') && cont !== form) {
            cont = cont.parentElement;
        }
        if (cont && cont.classList.contains('input-group')) cont = cont.parentElement;
        let fb = cont && cont.querySelector('.invalid-feedback');
        if (!fb) { fb = document.createElement('div'); fb.className = 'invalid-feedback d-block'; cont.appendChild(fb); }
        fb.textContent = mensaje;
    }

    let tieneErrores = false;

    if (!solicitudId.value) {
        if (errorSolicitudDiv) {
            errorSolicitudDiv.classList.remove('d-none');
            errorSolicitudDiv.textContent = 'Debe seleccionar una solicitud.';
        }
        tieneErrores = true;
    } else {
        if (errorSolicitudDiv) errorSolicitudDiv.classList.add('d-none');
    }

    if (!fechaPlan || !fechaPlan.value) {
        marcarInvalidoCustom(fechaPlan, 'Debe seleccionar una fecha de planificación.');
        tieneErrores = true;
    } else {
        fechaPlan.classList.remove('is-invalid');
        fechaPlan.classList.add('is-valid');
    }

    if (!observaciones || observaciones.value.trim().length < 10) {
        marcarInvalidoCustom(observaciones, 'La descripción técnica debe tener al menos 10 caracteres.');
        tieneErrores = true;
    } else {
        observaciones.classList.remove('is-invalid');
        observaciones.classList.add('is-valid');
    }

    if (!codigoProyecto || codigoProyecto.value.trim() === '' || codigoProyecto.value.trim().length < 5) {
        marcarInvalidoCustom(codigoProyecto, 'El código del proyecto es obligatorio (Ej: PRY-001).');
        tieneErrores = true;
    } else {
        codigoProyecto.classList.remove('is-invalid');
        codigoProyecto.classList.add('is-valid');
    }

    if (!maquinaria || !maquinaria.value || maquinaria.value === '' || maquinaria.value === null) {
        marcarInvalidoCustom(maquinaria, 'Debe seleccionar una maquinaria.');
        tieneErrores = true;
    } else {
        maquinaria.classList.remove('is-invalid');
        maquinaria.classList.add('is-valid');
    }

    if (!computos || computos.value.trim() === '') {
        marcarInvalidoCustom(computos, 'Los cômputos métricos son obligatorios.');
        tieneErrores = true;
    } else {
        computos.classList.remove('is-invalid');
        computos.classList.add('is-valid');
    }

    if (!estimacion || estimacion.value.trim() === '') {
        marcarInvalidoCustom(estimacion, 'La estimación de costo es obligatoria.');
        tieneErrores = true;
    } else {
        estimacion.classList.remove('is-invalid');
        estimacion.classList.add('is-valid');
    }

    if (tieneErrores) {
        const primerError = form.querySelector('.is-invalid');
        if (primerError) primerError.focus();
        return;
    }

    if (estimacion && estimacion.value.trim() !== "") {
        estimacion.value = estimacion.value.replace(/\./g, "").replace(",", ".");
    }

    const formData = new FormData(form);
    fetch(form.action, { method: 'POST', body: formData })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('modalRegistrarProyecto')).hide();

            Swal.fire('¡Éxito!', data.message, 'success').then(() => {
                const p = data.data;
                const tableBody = document.querySelector('table tbody');
                const msgVacio = document.getElementById('mensaje-vacio');
                if (msgVacio) msgVacio.remove();

                const newRow = `
                    <tr>
                        <td>${tableBody.rows.length + 1}</td>
                        <td class="fw-bold text-secondary">${p.codigo_proyecto}</td>
                        <td>${formatFecha(p.fecha_planificacion)}</td>
                        <td class="text-uppercase">${p.nombre_solicitante || '—'}</td>
                        <td>${p.descripcion_tecnica || '—'}</td>
                        <td>${p.computos_metricos || '—'}</td>
                        <td>${p.problematica || '—'}</td>
                        <td><span class="badge bg-dark">${p.nombre_maquinaria || 'PENDIENTE'}</span></td>
                        <td class="text-success fw-bold">${p.estimacion_costo}</td>
                        <td class="text-center">
                            <div class="d-flex gap-1 justify-content-center">
                                <a href="/ver-proyecto/${p.codigo_proyecto}" class="btn btn-sm btn-outline-info"><i class="bx bx-show"></i></a>
                                <a href="/editar-proyecto/${p.codigo_proyecto}" class="btn btn-sm btn-outline-warning"><i class="bx bx-edit"></i></a>
                                <button type="button" class="btn btn-sm btn-outline-danger" onclick="confirmarEliminacion(this)" data-delete-url="/eliminar-proyecto/${p.codigo_proyecto}"><i class="bx bx-trash"></i></button>
                            </div>
                        </td>
                    </tr>`;
                
                tableBody.insertAdjacentHTML('beforeend', newRow);
                form.reset();
                const allInvalids = form.querySelectorAll('.is-invalid');
                allInvalids.forEach(el => el.classList.remove('is-invalid'));
                actualizarContador(1);
            });
        } else {
            Swal.fire('Error', data.message, 'error');
        }
    });
});

function confirmarEliminacion(btn) {
    const url = btn.getAttribute('data-delete-url');
    const row = btn.closest('tr');
    const tableBody = row.parentNode;

    Swal.fire({
        title: '¿Estás seguro?',
        text: "¡No podrás revertir esta acción!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        confirmButtonText: 'Sí, eliminar'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(url, { method: 'GET' })
            .then(response => {
                if (response.ok) {
                    row.remove();
                    actualizarContador(-1);
                    if (tableBody.querySelectorAll('tr').length === 0) {
                        tableBody.insertAdjacentHTML('beforeend', 
                            '<tr id="mensaje-vacio"><td colspan="9" class="text-center text-muted py-4">NO SE ENCUENTRAN PROYECTOS GESTIONADOS</td></tr>');
                    }
                    Swal.fire('Eliminado', 'Proyecto eliminado.', 'success');
                }
            });
        }
    });
}

function actualizarContador(cambio) {
    const contadorEl = document.getElementById('contador-total');
    if (contadorEl) {
        let actual = parseInt(contadorEl.innerText) || 0;
        contadorEl.innerText = actual + cambio;
    }
}