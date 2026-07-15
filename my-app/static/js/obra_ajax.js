/**
 * Lógica AJAX para el módulo de Gestión de Obras.
 * Evita la recarga de página y maneja respuestas asíncronas en formato JSON.
 */
document.addEventListener('DOMContentLoaded', function() {
    const formObra = document.getElementById('formNuevaObra');
    const formEditarObra = document.getElementById('formEditarObra');
    const modalEditarObra = document.getElementById('modalEditarObra');

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
            const idObra = document.getElementById('edit_id_obra').value;
            const btnSubmit = formEditarObra.querySelector('button[type="submit"]');
            const textoOriginal = btnSubmit.innerHTML;
            btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Actualizando...';
            btnSubmit.disabled = true;

            const formData = new FormData(formEditarObra);
            formData.delete('semaforo_id_semaforo_locked');
            formData.delete('contratacion_id_contratacion_locked');
            formData.delete('gestionar_proyectos_codigo_proyecto_locked');

            fetch(`/obra/actualizar/${idObra}`, {
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

    document.querySelectorAll('.btn-ver-obra').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const idObra = this.getAttribute('data-id');
            window.location.href = `/obra/detalle/${idObra}`;
        });
    });

    document.querySelectorAll('.btn-editar-obra').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const idObra = this.getAttribute('data-id');
            fetch(`/obra/editar/${idObra}`)
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success' && data.data) {
                        const obra = data.data;
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
                        document.getElementById('edit_semaforo_id_semaforo').value = obra.semaforo_id_semaforo || '';
                        document.getElementById('edit_contratacion_id_contratacion').value = obra.contratacion_id_contratacion || '';
                        document.getElementById('edit_gestionar_proyectos_codigo_proyecto').value = obra.gestionar_proyectos_codigo_proyecto || '';

                        var modal = new bootstrap.Modal(document.getElementById('modalEditarObra'));
                        modal.show();
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: data.message || 'No se pudo cargar la obra.',
                            confirmButtonText: 'Aceptar'
                        });
                    }
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
        });
    });

    document.querySelectorAll('.btn-eliminar-obra').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const idObra = this.getAttribute('data-id');
            Swal.fire({
                title: '¿Eliminar obra?',
                text: 'Se aplicará borrado lógico',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#dc3545',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Eliminar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    fetch(`/obra/eliminar/${idObra}`)
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
                            console.error('Error al eliminar obra:', error);
                            Swal.fire({
                                icon: 'error',
                                title: 'Error de red',
                                text: 'No se pudo comunicar con el servidor.',
                                confirmButtonText: 'Aceptar'
                            });
                        });
                }
            });
        });
    });
});
