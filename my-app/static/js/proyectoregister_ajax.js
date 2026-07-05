// --- FUNCIÓN DE REGISTRO ---
document.getElementById('btnGuardarProyecto').addEventListener('click', function() {
    const form = document.getElementById('formRegistrarProyecto');
    if (!form.checkValidity()) { form.reportValidity(); return; }

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
                        <td>${p.fecha_planificacion}</td>
                        <td class="text-uppercase">${p.nombre_solicitante || '—'}</td>
                        <td>${p.descripcion_tecnica || '—'}</td>
                        <td>${p.problematica || '—'}</td>
                        <td><span class="badge bg-dark">${p.nombre_maquinaria || 'PENDIENTE'}</span></td>
                        <td class="text-success fw-bold">${p.estimacion_costo}</td>
                        <td class="text-center">
                            <div class="d-flex justify-content-center gap-1">
                                <a href="/ver-proyecto/${p.codigo_proyecto}" class="btn btn-sm btn-outline-info"><i class="bx bx-show"></i></a>
                                <a href="/editar-proyecto/${p.codigo_proyecto}" class="btn btn-sm btn-outline-warning"><i class="bx bx-edit"></i></a>
                                <button type="button" class="btn btn-sm btn-outline-danger" onclick="confirmarEliminacion(this)" data-delete-url="/eliminar-proyecto/${p.codigo_proyecto}"><i class="bx bx-trash"></i></button>
                            </div>
                        </td>
                    </tr>`;
                
                tableBody.insertAdjacentHTML('beforeend', newRow);
                form.reset();
                actualizarContador(1);
            });
        } else {
            Swal.fire('Error', data.message, 'error');
        }
    });
});
function confirmarEliminacion(btn) {
    event.preventDefault();
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