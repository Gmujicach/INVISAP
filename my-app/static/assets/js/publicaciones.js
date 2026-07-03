/**
 * publicaciones.js - Validaciones para el módulo de publicaciones
 * Valida título, responsable, tipo y fecha antes de enviar al servidor
 */

document.addEventListener('DOMContentLoaded', function () {
    initializePublicacionValidation();
});

function initializePublicacionValidation() {
    const formPublicacion = document.querySelector('form[action*="publicacion"]');
    
    if (!formPublicacion) return;
    
    const inputTitulo = formPublicacion.querySelector('input[name="titulo_publicacion"]');
    const inputResponsable = formPublicacion.querySelector('input[name="nombre_responsable"]');
    const selectTipo = formPublicacion.querySelector('select[name="tipo_publicacion"]');
    const inputFecha = formPublicacion.querySelector('input[name="fecha_publicacion"]');
    const selectInforme = formPublicacion.querySelector('select[name*="informe"]');
    
    if (selectInforme) {
        selectInforme.addEventListener('change', validateInforme);
    }
    
    if (inputTitulo) {
        inputTitulo.addEventListener('input', validateTitulo);
    }
    
    if (inputResponsable) {
        inputResponsable.addEventListener('input', validateResponsable);
    }
    
    if (selectTipo) {
        selectTipo.addEventListener('change', validateTipo);
    }
    
    if (inputFecha) {
        inputFecha.addEventListener('change', validateFecha);
    }
}

const REGEX_TITULO = /^[a-zA-Z0-9\sÁÉÍÓÚáéíóúñÑ.,-]{5,150}$/;
const REGEX_RESPONSABLE = /^[a-zA-Z\sÁÉÍÓÚáéíóúñÑ]{3,45}$/;

function validateTitulo() {
    const input = this;
    const valor = input.value.trim();
    
    if (valor.length === 0) {
        setInvalid(input, 'El título es obligatorio.');
        return false;
    }
    
    if (valor.length < 5) {
        setInvalid(input, 'El título debe tener al menos 5 caracteres.');
        return false;
    }
    
    if (valor.length > 150) {
        setInvalid(input, 'El título no puede exceder 150 caracteres.');
        return false;
    }
    
    if (!REGEX_TITULO.test(valor)) {
        setInvalid(input, 'El título contiene caracteres inválidos.');
        return false;
    }
    
    setValid(input);
    return true;
}

function validateResponsable() {
    const input = this;
    const valor = input.value.trim();
    
    if (valor.length === 0) {
        setInvalid(input, 'El nombre del responsable es obligatorio.');
        return false;
    }
    
    if (valor.length < 3) {
        setInvalid(input, 'El nombre debe tener al menos 3 caracteres.');
        return false;
    }
    
    if (valor.length > 45) {
        setInvalid(input, 'El nombre no puede exceder 45 caracteres.');
        return false;
    }
    
    if (!REGEX_RESPONSABLE.test(valor)) {
        setInvalid(input, 'El nombre solo debe contener letras y espacios.');
        return false;
    }
    
    setValid(input);
    return true;
}

function validateTipo() {
    const select = this;
    const valor = select.value;
    
    if (!valor || valor === '') {
        setInvalid(select, 'Debe seleccionar un tipo de publicación.');
        return false;
    }
    
    setValid(select);
    return true;
}

function validateFecha() {
    const input = this;
    const valor = input.value;
    
    if (!valor) {
        setInvalid(input, 'La fecha es obligatoria.');
        return false;
    }
    
    setValid(input);
    return true;
}

function validateInforme() {
    const select = this;
    const valor = select.value;
    
    if (valor && valor !== '' && valor !== '0') {
        setValid(select);
        return true;
    }
    
    setInvalid(select, 'Debe seleccionar un informe válido.');
    return false;
}

function setValid(element) {
    element.classList.remove('is-invalid');
    element.classList.add('is-valid');
    const feedback = element.parentNode.parentNode.querySelector('.invalid-feedback');
    if (feedback) feedback.remove();
}

function setInvalid(element, message) {
    element.classList.remove('is-valid');
    element.classList.add('is-invalid');
    
    let feedback = element.parentNode.parentNode.querySelector('.invalid-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        element.parentNode.parentNode.appendChild(feedback);
    }
    feedback.textContent = message;
}

async function handlePublicacionSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const btnSubmit = form.querySelector('button[type="submit"]');
    
    const inputTitulo = form.querySelector('input[name="titulo_publicacion"]');
    const inputResponsable = form.querySelector('input[name="nombre_responsable"]');
    const selectTipo = form.querySelector('select[name="tipo_publicacion"]');
    const inputFecha = form.querySelector('input[name="fecha_publicacion"]');
    const selectInforme = form.querySelector('select[name*="informe"]');
    
    const validTitulo = inputTitulo ? validateTitulo.call(inputTitulo) : true;
    const validResponsable = inputResponsable ? validateResponsable.call(inputResponsable) : true;
    const validTipo = selectTipo ? validateTipo.call(selectTipo) : true;
    const validFecha = inputFecha ? validateFecha.call(inputFecha) : true;
    const validInforme = selectInforme ? validateInforme.call(selectInforme) : true;
    
    if (!validTitulo || !validResponsable || !validTipo || !validFecha || !validInforme) {
        mostrarError('Complete todos los campos correctamente antes de guardar.');
        return;
    }
    
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Guardando...';
    
    try {
        const formData = new FormData(form);
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData
        });
        
        if (response.redirected) {
            window.location.href = response.url;
            return;
        }
        
        const result = await response.json().catch(() => ({}));
        
        if (result.status === 'success' || response.ok) {
            mostrarExito('Publicación guardada exitosamente.');
            form.reset();
            form.querySelectorAll('.is-valid, .is-invalid').forEach(el => {
                el.classList.remove('is-valid', 'is-invalid');
            });
            setTimeout(() => {
                if (document.getElementById('contenedorFormulario')) {
                    const collapse = bootstrap.Collapse.getOrCreateInstance(document.getElementById('contenedorFormulario'));
                    collapse.hide();
                }
                location.reload();
            }, 1500);
        } else {
            throw new Error(result.message || 'Error al guardar la publicación.');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarError(error.message || 'Error de conexión con el servidor.');
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = btnSubmit.innerHTML.replace(/<span class="spinner-border[^>]*>.*?<\/span>/, '');
    }
}

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

async function eliminarPublicacionAjax(id_publicacion) {
    if (typeof Swal !== 'undefined') {
        const result = await Swal.fire({
            title: '¿Estás seguro?',
            text: 'La publicación será desactivada (borrado lógico).',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Sí, desactivar',
            cancelButtonText: 'Cancelar',
            reverseButtons: true
        });
        
        if (!result.isConfirmed) return;
    } else {
        if (!confirm('¿Estás seguro de desactivar esta publicación?')) return;
    }
    
    try {
        const response = await fetch(`/api/publicaciones/eliminar/${id_publicacion}`, {
            method: 'DELETE'
        });
        
        const result = await response.json().catch(() => ({}));
        
        if (response.ok || result.status === 'success') {
            mostrarExito('Publicación desactivada exitosamente.');
            const row = document.querySelector(`tr[data-id="${id_publicacion}"]`);
            if (row) row.remove();
            else location.reload();
        } else {
            throw new Error(result.message || 'Error al desactivar la publicación.');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarError(error.message || 'Error de conexión.');
    }
}