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
                window.location.href = `/empleados/delete/${id_empleado}`;
            }
        });
    } else {
        if (confirm("¿Estás seguro de desactivar este empleado?")) {
            window.location.href = `/empleados/delete/${id_empleado}`;
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