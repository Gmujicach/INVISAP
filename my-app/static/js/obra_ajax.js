/**
 * Lógica AJAX para el módulo de Gestión de Obras.
 * Evita la recarga de página y maneja respuestas asíncronas en formato JSON.
 */
document.addEventListener('DOMContentLoaded', function() {
    const formObra = document.getElementById('formNuevaObra');
    const formEditarObra = document.getElementById('formEditarObra');
    const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminar');
    let idObraEliminar = null;

    function cargarSelect(url, selectId, valueKey, textKey, placeholderText) {
        return fetch(url)
            .then(response => response.json())
            .then(data => {
                console.log(`[obra_ajax] ${selectId} response:`, data);
                const select = document.getElementById(selectId);
                if (!select) return;
                const placeholder = placeholderText || (select.options[0] ? select.options[0].textContent : 'Seleccione...');
                const placeholderValue = select.options[0] ? select.options[0].value : '';
                if (!Array.isArray(data) || data.length === 0) {
                    select.innerHTML = '<option value="">' + placeholder + ' (sin registros)</option>';
                    return;
                }
                select.innerHTML = '<option value="">' + placeholder + '</option>';
                data.forEach(item => {
                    const option = document.createElement('option');
                    option.value = item[valueKey];
                    option.textContent = item[textKey];
                    select.appendChild(option);
                });
            })
            .catch(err => console.error(`[obra_ajax] Error cargando ${selectId}:`, err));
    }

    function cargarCatalogosNueva() {
        return Promise.all([
            cargarSelect('/api/obra/semaforos', 'semaforo_id_semaforo', 'id_semaforo', 'descripcion'),
            cargarSelect('/api/obra/contrataciones', 'contratacion_id_contratacion', 'id_contratacion', 'numero_contrato'),
            cargarSelect('/api/obra/proyectos', 'gestionar_proyectos_codigo_proyecto', 'codigo_proyecto', 'codigo_proyecto')
        ]);
    }

    function cargarCatalogosEditar() {
        return Promise.all([
            cargarSelect('/api/obra/semaforos', 'edit_semaforo_id_semaforo', 'id_semaforo', 'descripcion'),
            cargarSelect('/api/obra/contrataciones', 'edit_contratacion_id_contratacion', 'id_contratacion', 'numero_contrato'),
            cargarSelect('/api/obra/proyectos', 'edit_gestionar_proyectos_codigo_proyecto', 'codigo_proyecto', 'codigo_proyecto')
        ]);
    }

    const modalNueva = document.getElementById('modalNuevaObra');
    if (modalNueva) {
        modalNueva.addEventListener('show.bs.modal', function() {
            cargarCatalogosNueva();
        });
    }

    const modalEditar = document.getElementById('modalEditarObra');
    if (modalEditar) {
        modalEditar.addEventListener('show.bs.modal', function() {
            // Ya no recarga catálogos aquí; lo hace cargarDatosEditar().
        });
    }

    const btnEditarDesdeDetalle = document.getElementById('btnEditarDesdeDetalle');
    if (btnEditarDesdeDetalle) {
        btnEditarDesdeDetalle.addEventListener('click', function() {
            const id = document.getElementById('ver_id_obra').value;
            if (!id) return;
            const modalVer = bootstrap.Modal.getInstance(document.getElementById('modalVerObra'));
            if (modalVer) modalVer.hide();
            cargarDatosEditar(id).then(() => {
                const modalEditar = new bootstrap.Modal(document.getElementById('modalEditarObra'));
                modalEditar.show();
            });
        });
    }

    if (formObra) {
        formObra.addEventListener('submit', function(evento) {
            evento.preventDefault();

            const btnSubmit = formObra.querySelector('button[type="submit"]');
            const textoOriginal = btnSubmit.innerHTML;
            btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Guardando...';
            btnSubmit.disabled = true;

            const formData = new FormData(formObra);

            fetch(formObra.action, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    Swal.fire({
                        icon: 'success',
                        title: '¡Excelente!',
                        text: data.message,
                        confirmButtonText: 'Entendido'
                    }).then(() => {
                        window.location.reload();
                    });
                    
                    formObra.reset();
                    
                    var modalEl = document.getElementById('modalNuevaObra');
                    var modal = bootstrap.Modal.getInstance(modalEl);
                    if (modal) { modal.hide(); }

                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error en la operación',
                        text: data.message,
                        confirmButtonText: 'Aceptar'
                    });
                }
            })
            .catch(error => {
                console.error('Error en la petición fetch:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error de red',
                    text: 'No se pudo comunicar con el servidor.',
                    confirmButtonText: 'Aceptar'
                });
            })
            .finally(() => {
                btnSubmit.innerHTML = textoOriginal;
                btnSubmit.disabled = false;
            });
        });
    }

    if (formEditarObra) {
        formEditarObra.addEventListener('submit', function(evento) {
            evento.preventDefault();

            const btnSubmit = formEditarObra.querySelector('button[type="submit"]');
            const textoOriginal = btnSubmit.innerHTML;
            btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Actualizando...';
            btnSubmit.disabled = true;

            const formData = new FormData(formEditarObra);

            fetch(formEditarObra.action, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    Swal.fire({
                        icon: 'success',
                        title: '¡Excelente!',
                        text: data.message,
                        confirmButtonText: 'Entendido'
                    }).then(() => {
                        window.location.reload();
                    });
                    
                    formEditarObra.reset();
                    
                    var modalEl = document.getElementById('modalEditarObra');
                    var modal = bootstrap.Modal.getInstance(modalEl);
                    if (modal) { modal.hide(); }

                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error en la operación',
                        text: data.message,
                        confirmButtonText: 'Aceptar'
                    });
                }
            })
            .catch(error => {
                console.error('Error en la petición fetch:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error de red',
                    text: 'No se pudo comunicar con el servidor.',
                    confirmButtonText: 'Aceptar'
                });
            })
            .finally(() => {
                btnSubmit.innerHTML = textoOriginal;
                btnSubmit.disabled = false;
            });
        });
    }

    if (btnConfirmarEliminar) {
        btnConfirmarEliminar.addEventListener('click', function() {
            if (!idObraEliminar) return;

            btnConfirmarEliminar.disabled = true;
            const textoOriginal = btnConfirmarEliminar.innerHTML;
            btnConfirmarEliminar.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Eliminando...';

            fetch(`/eliminar-obra/${idObraEliminar}`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    Swal.fire({
                        icon: 'success',
                        title: 'Eliminado',
                        text: data.message,
                        confirmButtonText: 'Entendido'
                    }).then(() => {
                        window.location.reload();
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: data.message,
                        confirmButtonText: 'Aceptar'
                    });
                }
            })
            .catch(error => {
                console.error('Error al eliminar:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error de red',
                    text: 'No se pudo comunicar con el servidor.',
                    confirmButtonText: 'Aceptar'
                });
            })
            .finally(() => {
                btnConfirmarEliminar.innerHTML = textoOriginal;
                btnConfirmarEliminar.disabled = false;
                idObraEliminar = null;
                
                var modalEl = document.getElementById('modalEliminarObra');
                var modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) { modal.hide(); }
            });
        });
    }

    document.querySelectorAll('.btn-eliminar-obra').forEach(function(btn) {
        btn.addEventListener('click', function() {
            idObraEliminar = this.getAttribute('data-id');
            const nombreObra = this.getAttribute('data-nombre');
            document.getElementById('nombre_obra_eliminar').textContent = nombreObra;
        });
    });
});

function cargarDatosEditar(id_obra) {
    return Promise.all([
        fetch(`/api/obra/obtener/${id_obra}`).then(r => r.json()),
        fetch('/api/obra/semaforos').then(r => r.json()),
        fetch('/api/obra/contrataciones').then(r => r.json()),
        fetch('/api/obra/proyectos').then(r => r.json())
    ]).then(([obraResp, semaforos, contrataciones, proyectos]) => {
        if (obraResp.status !== 'success' || !obraResp.data) {
            throw new Error('No se pudo cargar la obra');
        }

        const obra = obraResp.data;

        document.getElementById('edit_id_obra').value = obra.id_obra;
        document.getElementById('edit_titulo_obra').value = obra.titulo_obra || '';
        document.getElementById('edit_ubicacion_obra').value = obra.ubicacion_obra || '';
        document.getElementById('edit_periodo_ejecucion').value = obra.periodo_ejecucion || '';
        document.getElementById('edit_fecha_inicio').value = obra.fecha_inicio || '';
        document.getElementById('edit_fecha_fin').value = obra.fecha_fin || '';
        document.getElementById('edit_mediciones_obra').value = obra.mediciones_obra || '';
        document.getElementById('edit_valuaciones').value = obra.valuaciones || '';
        document.getElementById('edit_porcentaje_avance_obra').value = obra.porcentaje_avance_obra || '';
        document.getElementById('edit_numero_contrato').value = obra.numero_contrato || '';
        document.getElementById('edit_modificaciones_contrato').value = obra.modificaciones_contrato || '';
        document.getElementById('edit_certificaciones_obras_ejecutadas').value = obra.certificaciones_obras_ejecutadas || '';

        const populateSelect = (selectId, valueKey, textKey, selectedValue) => {
            const select = document.getElementById(selectId);
            if (!select) return;
            select.innerHTML = '<option value="">Seleccione...</option>';
            const lista = selectId === 'edit_semaforo_id_semaforo' ? semaforos : (selectId === 'edit_contratacion_id_contratacion' ? contrataciones : proyectos);
            const vKey = valueKey || 'id_semaforo';
            const tKey = textKey || 'descripcion';
            lista.forEach(item => {
                const option = document.createElement('option');
                option.value = selectId === 'edit_gestionar_proyectos_codigo_proyecto' ? item['codigo_proyecto'] : item[vKey];
                option.textContent = selectId === 'edit_gestionar_proyectos_codigo_proyecto' ? `${item['codigo_proyecto']} - ${item['descripcion_tecnica'] || ''}`.trim() : item[tKey];
                if (String(option.value) === String(selectedValue)) {
                    option.selected = true;
                }
                select.appendChild(option);
            });
        };

        populateSelect('edit_semaforo_id_semaforo', 'id_semaforo', 'descripcion', obra.semaforo_id_semaforo);
        populateSelect('edit_contratacion_id_contratacion', 'id_contratacion', 'numero_contrato', obra.contratacion_id_contratacion);
        populateSelect('edit_gestionar_proyectos_codigo_proyecto', 'codigo_proyecto', 'codigo_proyecto', obra.gestionar_proyectos_codigo_proyecto);
    })
    .catch(error => {
        console.error('Error al cargar obra:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error de red',
            text: 'No se pudo comunicar con el servidor.',
            confirmButtonText: 'Aceptar'
        });
    });
}

function verObra(id_obra) {
    const modalVer = document.getElementById('modalVerObra');
    if (!modalVer) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'El modal de detalle no está disponible en esta vista.',
            confirmButtonText: 'Aceptar'
        });
        return;
    }

    fetch(`/api/obra/obtener/${id_obra}`)
    .then(response => {
        if (response.status === 401) {
            return response.json().then(data => {
                throw new Error(data.message || 'Sesión no válida');
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.status !== 'success' || !data.data) {
            const mensaje = data.message || 'Obra no encontrada';
            throw new Error(mensaje);
        }
        const obra = data.data;
        document.getElementById('ver_id_obra').value = obra.id_obra || '';
        document.getElementById('ver_titulo_obra').value = obra.titulo_obra || '';
        document.getElementById('ver_ubicacion_obra').value = obra.ubicacion_obra || '';
        document.getElementById('ver_periodo_ejecucion').value = obra.periodo_ejecucion || '';
        document.getElementById('ver_fecha_inicio').value = obra.fecha_inicio || '';
        document.getElementById('ver_fecha_fin').value = obra.fecha_fin || '';
        document.getElementById('ver_mediciones_obra').value = obra.mediciones_obra || '';
        document.getElementById('ver_valuaciones').value = obra.valuaciones || '';
        document.getElementById('ver_porcentaje_avance_obra').value = obra.porcentaje_avance_obra ? obra.porcentaje_avance_obra + '%' : '';
        document.getElementById('ver_numero_contrato').value = obra.numero_contrato || '';
        document.getElementById('ver_modificaciones_contrato').value = obra.modificaciones_contrato || '';
        document.getElementById('ver_certificaciones_obras_ejecutadas').value = obra.certificaciones_obras_ejecutadas || '';
        document.getElementById('ver_semaforo').value = obra.descripcion || ('Color: ' + (obra.color || ''));
        document.getElementById('ver_contratacion').value = obra.contratacion_id_contratacion || '';
        document.getElementById('ver_proyecto').value = obra.gestionar_proyectos_codigo_proyecto || '';
        const modal = new bootstrap.Modal(document.getElementById('modalVerObra'));
        modal.show();
    })
    .catch(error => {
        console.error('Error al cargar detalle obra:', error);
        const mensaje = error.message || 'No se pudo cargar el detalle de la obra.';
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: mensaje,
            confirmButtonText: 'Aceptar'
        });
    });
}
