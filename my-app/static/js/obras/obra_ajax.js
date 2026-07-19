function validarFormularioObra(form) {
    const titulo = form.querySelector('[name="titulo_obra"]').value.trim();
    const ubicacion = form.querySelector('[name="ubicacion_obra"]').value.trim();
    const periodo = form.querySelector('[name="periodo_ejecucion"]').value.trim();
    const fechaInicio = form.querySelector('[name="fecha_inicio"]').value.trim();
    const fechaFin = form.querySelector('[name="fecha_fin"]').value.trim();
    const mediciones = form.querySelector('[name="mediciones_obra"]').value.trim();
    const valuaciones = form.querySelector('[name="valuaciones"]').value.trim();
    const avance = form.querySelector('[name="porcentaje_avance_obra"]').value.trim();
    const numeroContrato = form.querySelector('[name="numero_contrato"]').value.trim();
    const modificaciones = form.querySelector('[name="modificaciones_contrato"]').value.trim();
    const certificaciones = form.querySelector('[name="certificaciones_obras_ejecutadas"]').value.trim();
    const semaforo = form.querySelector('[name="semaforo_id_semaforo"]').value.trim();
    const contratacion = form.querySelector('[name="contratacion_id_contratacion"]').value.trim();
    const proyecto = form.querySelector('[name="gestionar_proyectos_codigo_proyecto"]').value.trim();

    if (!titulo || titulo.length < 3) {
        Swal.fire({ icon: 'error', title: 'Validación', text: 'El título debe tener al menos 3 caracteres.', confirmButtonText: 'Aceptar' });
        return false;
    }
    if (!ubicacion || ubicacion.length < 3) {
        Swal.fire({ icon: 'error', title: 'Validación', text: 'La ubicación debe tener al menos 3 caracteres.', confirmButtonText: 'Aceptar' });
        return false;
    }
    if (periodo === '' || periodo.length > 10) {
        Swal.fire({ icon: 'error', title: 'Validación', text: 'Período de ejecución es obligatorio (máximo 10 caracteres, ej. "2 meses").', confirmButtonText: 'Aceptar' });
        return false;
    }
    if (!fechaInicio) {
        Swal.fire({ icon: 'error', title: 'Validación', text: 'Debe seleccionar la fecha de inicio.', confirmButtonText: 'Aceptar' });
        return false;
    }
    if (!fechaFin) {
        Swal.fire({ icon: 'error', title: 'Validación', text: 'Debe seleccionar la fecha de fin.', confirmButtonText: 'Aceptar' });
        return false;
    }
    if (new Date(fechaFin) < new Date(fechaInicio)) {
        Swal.fire({ icon: 'error', title: 'Validación', text: 'La fecha de fin no puede ser anterior a la fecha de inicio.', confirmButtonText: 'Aceptar' });
        return false;
    }
    if (!mediciones) {
        Swal.fire({ icon: 'error', title: 'Validación', text: 'Debe ingresar las mediciones de obra.', confirmButtonText: 'Aceptar' });
        return false;
    }
    if (!valuaciones) {
        Swal.fire({ icon: 'error', title: 'Validación', text: 'Debe ingresar las valuaciones.', confirmButtonText: 'Aceptar' });
        return false;
    }
    if (avance === '' || isNaN(avance) || parseInt(avance) < 0 || parseInt(avance) > 100) {
        Swal.fire({ icon: 'error', title: 'Validación', text: 'El porcentaje de avance debe estar entre 0 y 100.', confirmButtonText: 'Aceptar' });
        return false;
    }
    if (!numeroContrato || numeroContrato.length < 3) {
        Swal.fire({ icon: 'error', title: 'Validación', text: 'El número de contrato debe tener al menos 3 caracteres.', confirmButtonText: 'Aceptar' });
        return false;
    }
    if (!modificaciones) {
        Swal.fire({ icon: 'error', title: 'Validación', text: 'Debe ingresar las modificaciones de contrato.', confirmButtonText: 'Aceptar' });
        return false;
    }
    if (certificaciones === '' || isNaN(certificaciones) || parseInt(certificaciones) < 0) {
        Swal.fire({ icon: 'error', title: 'Validación', text: 'Certificaciones ejecutadas debe ser un número mayor o igual a 0.', confirmButtonText: 'Aceptar' });
        return false;
    }
    if (!semaforo) {
        Swal.fire({ icon: 'error', title: 'Validación', text: 'Debe seleccionar un semáforo.', confirmButtonText: 'Aceptar' });
        return false;
    }
    if (!contratacion) {
        Swal.fire({ icon: 'error', title: 'Validación', text: 'Debe seleccionar una contratación.', confirmButtonText: 'Aceptar' });
        return false;
    }
    if (!proyecto) {
        Swal.fire({ icon: 'error', title: 'Validación', text: 'Debe seleccionar un proyecto.', confirmButtonText: 'Aceptar' });
        return false;
    }
    return true;
}

document.addEventListener('DOMContentLoaded', function() {
    const formObra = document.getElementById('formNuevaObra');
    const formEditarObra = document.getElementById('formEditarObra');
    const modalEditarObra = document.getElementById('modalEditarObra');
    const btnConfirmarEliminar = document.getElementById('btnConfirmarEliminar');
    let idObraEliminar = null;

    function cargarSelect(url, selectId, valueKey, textKey, placeholderText) {
        return fetch(url)
            .then(response => response.json())
            .then(data => {
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
            .catch(err => console.error('[obra_ajax] Error cargando ' + selectId + ':', err));
    }

    function cargarCatalogosNueva() {
        return Promise.all([
            cargarSelect('/api/obra/semaforos', 'semaforo_id_semaforo', 'id_semaforo', 'nombre'),
            cargarSelect('/api/obra/contrataciones', 'contratacion_id_contratacion', 'id_contratacion', 'numero_contrato'),
            cargarSelect('/api/obra/proyectos', 'gestionar_proyectos_codigo_proyecto', 'codigo_proyecto', 'codigo_proyecto')
        ]);
    }

    function cargarCatalogosEditar() {
        return Promise.all([
            cargarSelect('/api/obra/semaforos', 'edit_semaforo_id_semaforo', 'id_semaforo', 'nombre'),
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
            if (!validarFormularioObra(formObra)) {
                return;
            }
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
            if (!validarFormularioObra(formEditarObra)) {
                return;
            }

            const idObra = document.getElementById('edit_id_obra').value;
            const btnSubmit = formEditarObra.querySelector('button[type="submit"]');
            const textoOriginal = btnSubmit.innerHTML;
            btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Actualizando...';
            btnSubmit.disabled = true;

            const formData = new FormData(formEditarObra);
            formData.delete('semaforo_id_semaforo_locked');
            formData.delete('contratacion_id_contratacion_locked');
            formData.delete('gestionar_proyectos_codigo_proyecto_locked');

            const actionUrl = formEditarObra.action || `/obra/actualizar/${idObra}`;
            fetch(actionUrl, {
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
                        window.location.href = "/gestionar-obras";
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

    // Delegación de eventos: robusto ante recreación del DOM (DataTables, paginación, etc.)
    document.addEventListener('click', function(evento) {
        const btn = evento.target.closest('.btn-eliminar-obra');
        if (!btn) return;
        idObraEliminar = btn.getAttribute('data-id');
        const nombreObra = btn.getAttribute('data-nombre') || '';
        const spanNombre = document.getElementById('nombre_obra_eliminar');
        if (spanNombre) spanNombre.textContent = nombreObra;
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
                option.textContent = selectId === 'edit_gestionar_proyectos_codigo_proyecto' ? (item['codigo_proyecto'] + ' - ' + (item['descripcion_tecnica'] || '')).trim() : item[tKey];
                if (String(option.value) === String(selectedValue)) {
                    option.selected = true;
                }
                select.appendChild(option);
            });
        };

        populateSelect('edit_semaforo_id_semaforo', 'id_semaforo', 'nombre', obra.semaforo_id_semaforo);
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
        document.getElementById('ver_semaforo').value = obra.color || '';
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
