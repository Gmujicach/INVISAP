/**
 * empleados_validation.js - Módulo independiente para validación y registro de empleados
 * Implementa comunicación asíncrona con Fetch/Ajax
 */

document.addEventListener('DOMContentLoaded', function () {
    const formEmpleado = document.getElementById('formEmpleado');
    const formEmpleadoUpdate = document.getElementById('formEmpleadoUpdate');
    
    // Validar cédula en tiempo real
    const inputCedula = document.querySelector('input[name="cedula_empleado"]');
    if (inputCedula) {
        inputCedula.addEventListener('change', function() {
            const cedula = this.value.trim();
            if (cedula.length >= 7 && cedula.length <= 8) {
                console.log('Validando cédula:', cedula);
            }
        });
    }
    
    // Validar cargo seleccionado
    const selectCargo = document.querySelector('select[name="cargo"]');
    if (selectCargo) {
        selectCargo.addEventListener('change', function() {
            if (this.value) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            }
        });
    }
    
    // Validar teléfono en tiempo real (solo números, máximo 11 dígitos)
    const inputTelefono = document.querySelector('input[name="telefono"]');
    if (inputTelefono) {
        inputTelefono.addEventListener('input', function() {
            this.value = this.value.replace(/[^\d]/g, '').slice(0, 11);
            const longitudValida = this.value.length >= 10 && this.value.length <= 11;
            if (longitudValida) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } else if (this.value.length > 0) {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-valid', 'is-invalid');
            }
        });
    }
    
    // Asignar manejadores de submit
    if (formEmpleado) {
        formEmpleado.addEventListener('submit', registrarEmpleadoFetch);
    }
    
    if (formEmpleadoUpdate) {
        formEmpleadoUpdate.addEventListener('submit', actualizarEmpleadoFetch);
    }
});

/**
 * Función para registrar empleado mediante Fetch
 */
async function registrarEmpleadoFetch(event) {
    event.preventDefault();
    
    const form = event.target;
    
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        
        // Encontrar el primer campo inválido
        const primerCampoInvalido = form.querySelector(':invalid');
        if (primerCampoInvalido) {
            primerCampoInvalido.focus();
        }
        
        mostrarError('Complete todos los campos requeridos correctamente.');
        return;
    }
    
    const btnGuardar = document.getElementById('btnGuardar');
    const formData = new FormData(form);
    
    btnGuardar.disabled = true;
    btnGuardar.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Guardando...';
    
    try {
        const response = await fetch('/empleados/api/create', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            mostrarExito(result.message);
            setTimeout(() => {
                window.location.href = '/empleados/';
            }, 1500);
        } else {
            form.classList.add('was-validated');
            mostrarError('Error: ' + result.message);
            btnGuardar.disabled = false;
            btnGuardar.innerHTML = '<i class="bi bi-check-circle me-1"></i>Guardar Empleado';
        }
    } catch (error) {
        console.error('Error al registrar empleado:', error);
        mostrarError('Error de conexión con el servidor.');
        btnGuardar.disabled = false;
        btnGuardar.innerHTML = '<i class="bi bi-check-circle me-1"></i>Guardar Empleado';
    }
}

/**
 * Función para actualizar empleado
 */
async function actualizarEmpleadoFetch(event) {
    event.preventDefault();
    
    const form = event.target;
    
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        
        const primerCampoInvalido = form.querySelector(':invalid');
        if (primerCampoInvalido) {
            primerCampoInvalido.focus();
        }
        
        mostrarError('Complete todos los campos requeridos correctamente.');
        return;
    }
    
    const btnActualizar = document.getElementById('btnActualizar');
    const formData = new FormData(form);
    const idEmpleado = formData.get('id_empleado');
    
    try {
        const existeResponse = await fetch(`/empleados/api/validar/${idEmpleado}`);
        const existeData = await existeResponse.json();
        
        if (!existeData.existe) {
            mostrarError('El empleado no existe o fue eliminado.');
            return;
        }
    } catch (error) {
        console.error('Error al validar empleado:', error);
        mostrarError('Error de conexión.');
        return;
    }
    
    btnActualizar.disabled = true;
    btnActualizar.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Actualizando...';
    
    try {
        const response = await fetch('/empleados/api/update', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            mostrarExito(result.message);
            setTimeout(() => {
                window.location.href = '/empleados/';
            }, 1500);
        } else {
            form.classList.add('was-validated');
            mostrarError('Error: ' + result.message);
            btnActualizar.disabled = false;
            btnActualizar.innerHTML = '<i class="bi bi-arrow-repeat me-1"></i>Actualizar Información';
        }
    } catch (error) {
        console.error('Error al actualizar empleado:', error);
        mostrarError('Error de conexión con el servidor.');
        btnActualizar.disabled = false;
        btnActualizar.innerHTML = '<i class="bi bi-arrow-repeat me-1"></i>Actualizar Información';
    }
}

/**
 * Función para eliminar empleado
 */
function eliminarEmpleadoJS(id_empleado) {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: '¿Estás seguro?',
            text: "El empleado será desactivado (borrado lógico).",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Sí, desactivar',
            cancelButtonText: 'Cancelar',
            reverseButtons: true
        }).then((result) => {
            if (result.isConfirmed) {
                fetch(`/empleados/delete/${id_empleado}`)
                    .then(function(response) { return response.json(); })
                    .then(function(data) {
                        if (data && data.status === 'success') {
                            Swal.fire({
                                icon: 'success',
                                title: '¡Éxito!',
                                text: data.message || 'Empleado desactivado correctamente.',
                                timer: 1500,
                                showConfirmButton: false
                            });
                            var row = document.querySelector(`tr[data-id-empleado="${id_empleado}"]`);
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
                                text: (data && data.message) || 'No se pudo desactivar el empleado.'
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
        if (confirm("¿Estás seguro de desactivar este empleado?")) {
            fetch(`/empleados/delete/${id_empleado}`)
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    if (data && data.status === 'success') {
                        alert('Empleado desactivado correctamente.');
                        var row = document.querySelector(`tr[data-id-empleado="${id_empleado}"]`);
                        if (row) {
                            row.style.transition = 'opacity 0.4s';
                            row.style.opacity = '0';
                            setTimeout(function() { row.remove(); }, 400);
                        } else {
                            setTimeout(function() { location.reload(); }, 800);
                        }
                    } else {
                        alert((data && data.message) || 'No se pudo desactivar el empleado.');
                    }
                })
                .catch(function() {
                    alert('Error de conexión');
                });
        }
    }
}

/**
 * Funciones de notificación
 */
function mostrarExito(mensaje) {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            icon: 'success',
            title: '¡Éxito!',
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