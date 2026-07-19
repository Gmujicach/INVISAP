/**
 * Reset Password Script - Sistema INVILARA
 * Autor: David - Equipo Invilara
 * Validación de coincidencia de contraseñas y Aplicando modularidad
 */

'use strict';

document.addEventListener('DOMContentLoaded', function() {
    // ============================================
    // VARIABLES Y CONSTANTES
    // ============================================
    const newPasswordInput = document.getElementById('new_password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const passwordMatchMessage = document.getElementById('password-match-message');
    const formResetPassword = document.getElementById('formResetPassword');
    const btnResetPassword = document.getElementById('btnResetPassword');

    // ============================================
    // FUNCIONES DE VALIDACIÓN
    // ============================================
    
    /**
     * Verifica si las contraseñas coinciden
     */
    function checkPasswordMatch() {
        if (!newPasswordInput || !confirmPasswordInput || !passwordMatchMessage) {
            return;
        }

        const newPassword = newPasswordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        // Si el campo de confirmación está vacío, no mostrar nada
        if (confirmPassword === '') {
            passwordMatchMessage.classList.add('d-none');
            confirmPasswordInput.classList.remove('is-valid', 'is-invalid');
            return;
        }

        // Verificar coincidencia
        if (newPassword === confirmPassword && confirmPassword !== '') {
            // Contraseñas coinciden
            passwordMatchMessage.classList.remove('d-none');
            passwordMatchMessage.className = 'form-text text-success mt-2';
            passwordMatchMessage.innerHTML = '<i class="bi bi-check-circle-fill me-1"></i> Las contraseñas coinciden';
            
            confirmPasswordInput.classList.remove('is-invalid');
            confirmPasswordInput.classList.add('is-valid');
            
            // Habilitar botón
            if (btnResetPassword) {
                btnResetPassword.disabled = false;
            }
        } else {
            // Contraseñas no coinciden
            passwordMatchMessage.classList.remove('d-none');
            passwordMatchMessage.className = 'form-text text-danger mt-2';
            passwordMatchMessage.innerHTML = '<i class="bi bi-x-circle-fill me-1"></i> Las contraseñas no coinciden';
            
            confirmPasswordInput.classList.remove('is-valid');
            confirmPasswordInput.classList.add('is-invalid');
            
            // Deshabilitar botón
            if (btnResetPassword) {
                btnResetPassword.disabled = true;
            }
        }
    }

    /**
     * Valida el formato de la contraseña según regex del backend
     */
    function validatePasswordFormat(password) {
        // Regex: 8-12 caracteres, letras y al menos un símbolo especial
        const passwordRegex = /^(?=.*[A-Za-zÁÉÍÓÚáéíóúÑñ])(?=.*[^A-Za-z0-9ÁÉÍÓÚáéíóúÑñ]).{8,12}$/;
        return passwordRegex.test(password);
    }

    /**
     * Maneja el envío del formulario
     */
    function handleFormSubmit(event) {
        const newPassword = newPasswordInput ? newPasswordInput.value : '';
        const confirmPassword = confirmPasswordInput ? confirmPasswordInput.value : '';

        // Validar que los campos no estén vacíos
        if (!newPassword || !confirmPassword) {
            event.preventDefault();
            showAlert('Por favor, completa todos los campos', 'error');
            return false;
        }

        // Validar formato de contraseña
        if (!validatePasswordFormat(newPassword)) {
            event.preventDefault();
            showAlert('La contraseña debe tener entre 8-12 caracteres, incluir letras y al menos un símbolo especial', 'error');
            return false;
        }

        // Validar coincidencia
        if (newPassword !== confirmPassword) {
            event.preventDefault();
            showAlert('Las contraseñas no coinciden', 'error');
            return false;
        }

        // Deshabilitar botón para evitar doble envío
        if (btnResetPassword) {
            btnResetPassword.disabled = true;
            btnResetPassword.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span><span>Restableciendo...</span>';
        }

        return true;
    }

    /**
     * Muestra una alerta personalizada
     */
    function showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        alertDiv.setAttribute('role', 'alert');
        alertDiv.innerHTML = `
            <i class="bi bi-${type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        if (formResetPassword) {
            formResetPassword.parentNode.insertBefore(alertDiv, formResetPassword);
            
            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        }
    }

    // ============================================
    // INICIALIZACIÓN
    // ============================================
    
    /**
     * Inicializa todos los event listeners
     */
    function init() {
        // Event listeners para verificar coincidencia
        if (newPasswordInput) {
            newPasswordInput.addEventListener('input', checkPasswordMatch);
        }

        if (confirmPasswordInput) {
            confirmPasswordInput.addEventListener('input', checkPasswordMatch);
            confirmPasswordInput.addEventListener('blur', checkPasswordMatch);
        }

        // Event listener para el formulario
        if (formResetPassword) {
            formResetPassword.addEventListener('submit', handleFormSubmit);
        }

        console.log('✅ Reset Password inicializado correctamente');
    }

    // Ejecutar inicialización
    init();
});