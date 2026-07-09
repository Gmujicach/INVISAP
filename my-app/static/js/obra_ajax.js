/**
 * Lógica AJAX para el módulo de Gestión de Obras.
 * Evita la recarga de página y maneja respuestas asíncronas en formato JSON.
 */
document.addEventListener('DOMContentLoaded', function() {
    // 1. Capturamos el formulario por su ID
    const formObra = document.getElementById('formNuevaObra');

    if (formObra) {
        formObra.addEventListener('submit', function(evento) {
            // 2. Prevenimos el comportamiento por defecto (recargar la vista)
            evento.preventDefault(); 

            // 3. Modificamos el botón para mostrar un estado de "Cargando"
            const btnSubmit = formObra.querySelector('button[type="submit"]');
            const textoOriginal = btnSubmit.innerHTML;
            btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Guardando...';
            btnSubmit.disabled = true; // Evitamos envíos duplicados

            // 4. Empaquetamos automáticamente todos los inputs del formulario
            const formData = new FormData(formObra);

            // 5. Enviamos la petición AJAX
            fetch(formObra.action, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json()) // Parseamos la respuesta a JSON
            .then(data => {
                // 6. Evaluamos la respuesta del controlador
                if (data.status === 'success') {
                    // Alerta de éxito usando SweetAlert2
                    Swal.fire({
                        icon: 'success',
                        title: '¡Excelente!',
                        text: data.message,
                        confirmButtonText: 'Entendido'
                    }).then(() => {
                        // Recargamos para actualizar la tabla (o puedes agregar la fila vía JS)
                        window.location.reload();
                    });
                    
                    formObra.reset(); // Limpiamos los campos
                    
                    // Cerramos el modal de Bootstrap
                    var modalEl = document.getElementById('modalNuevaObra');
                    var modal = bootstrap.Modal.getInstance(modalEl);
                    if (modal) { modal.hide(); }

                } else {
                    // Alerta de error (ej: falló una llave foránea en la BD)
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
                // 7. Restauramos el botón a su estado normal, pase lo que pase
                btnSubmit.innerHTML = textoOriginal;
                btnSubmit.disabled = false;
            });
        });
    }
});