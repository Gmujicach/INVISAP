/**
 * OTP Verification Script - Sistema INVILARA
 * Autor: David - Equipo Invilara
 * Manejo de inputs OTP con validación y temporizador y Aplicando modularidad
 */

'use strict';

document.addEventListener('DOMContentLoaded', function() {
    // ============================================
    // VARIABLES Y CONSTANTES
    // ============================================
    const otpInputs = document.querySelectorAll('.otp-input');
    const otpCodeHidden = document.getElementById('otp_code');
    const formVerifyOTP = document.getElementById('formVerifyOTP');
    const btnVerifyOTP = document.getElementById('btnVerifyOTP');
    const countdownElement = document.getElementById('countdown');
    
    // Configuración del temporizador (15 minutos)
    const TIMER_DURATION = 15 * 60; // 15 minutos en segundos
    let timeRemaining = TIMER_DURATION;
    let timerInterval = null;

    // ============================================
    // FUNCIONES DEL TEMPORIZADOR
    // ============================================
    
    /**
     * Formatea el tiempo en formato MM:SS
     */
    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    /**
     * Actualiza el display del temporizador
     */
    function updateTimer() {
        if (countdownElement) {
            countdownElement.textContent = formatTime(timeRemaining);
            
            // Cambiar color cuando quedan menos de 2 minutos
            if (timeRemaining <= 120) {
                countdownElement.classList.add('warning');
            }
            
            // Tiempo expirado
            if (timeRemaining <= 0) {
                clearInterval(timerInterval);
                handleTimerExpired();
            }
            
            timeRemaining--;
        }
    }

    /**
     * Maneja la expiración del temporizador
     */
    function handleTimerExpired() {
        // Deshabilitar inputs
        otpInputs.forEach(input => {
            input.disabled = true;
            input.classList.add('error');
        });
        
        // Deshabilitar botón
        if (btnVerifyOTP) {
            btnVerifyOTP.disabled = true;
            btnVerifyOTP.innerHTML = '<i class="bi bi-x-circle me-2"></i><span>Código Expirado</span>';
            btnVerifyOTP.classList.remove('btn-primary');
            btnVerifyOTP.classList.add('btn-danger');
        }
        
        // Mostrar alerta
        showAlert('El código ha expirado. Por favor, solicita uno nuevo.', 'error');
    }

    /**
     * Inicia el temporizador
     */
    function startTimer() {
        if (countdownElement) {
            timerInterval = setInterval(updateTimer, 1000);
            updateTimer(); // Actualizar inmediatamente
        }
    }

    // ============================================
    // FUNCIONES DE MANEJO DE OTP
    // ============================================
    
    /**
     * Maneja el input en los campos OTP
     */
    function handleOTPInput(event) {
        const input = event.target;
        const value = input.value;
        const index = parseInt(input.dataset.index);
        
        // Solo permitir números
        if (!/^\d$/.test(value)) {
            input.value = '';
            return;
        }
        
        // Marcar como lleno
        input.classList.add('filled');
        input.classList.remove('error');
        
        // Mover al siguiente input
        if (value && index < otpInputs.length - 1) {
            otpInputs[index + 1].focus();
        }
        
        // Verificar si todos los campos están llenos
        checkAllFieldsFilled();
    }

    /**
     * Maneja el evento keydown para navegación
     */
    function handleOTPKeydown(event) {
        const input = event.target;
        const index = parseInt(input.dataset.index);
        
        // Backspace: borrar y mover al anterior
        if (event.key === 'Backspace') {
            if (!input.value && index > 0) {
                otpInputs[index - 1].focus();
                otpInputs[index - 1].value = '';
                otpInputs[index - 1].classList.remove('filled');
            } else {
                input.value = '';
                input.classList.remove('filled');
            }
        }
        
        // Flecha izquierda
        if (event.key === 'ArrowLeft' && index > 0) {
            otpInputs[index - 1].focus();
        }
        
        // Flecha derecha
        if (event.key === 'ArrowRight' && index < otpInputs.length - 1) {
            otpInputs[index + 1].focus();
        }
    }

/**
      * Maneja el evento paste para pegar código completo
      */
    function handleOTPPaste(event) {
        event.preventDefault();
        const pastedData = event.clipboardData.getData('text').trim();
        
        // Validar que sean 4 dígitos
        if (/^\d{4}$/.test(pastedData)) {
            // Distribuir los dígitos en los inputs
            pastedData.split('').forEach((digit, index) => {
                if (otpInputs[index]) {
                    otpInputs[index].value = digit;
                    otpInputs[index].classList.add('filled');
                }
            });
            
            // Enfocar el último input
            otpInputs[otpInputs.length - 1].focus();
            
            // Verificar campos llenos
            checkAllFieldsFilled();
        } else {
            showAlert('El código debe contener exactamente 4 dígitos', 'error');
        }
    }

    /**
     * Verifica si todos los campos están llenos
     */
    function checkAllFieldsFilled() {
        const allFilled = Array.from(otpInputs).every(input => input.value !== '');
        
        if (allFilled) {
            // Construir el código completo
            const otpCode = Array.from(otpInputs).map(input => input.value).join('');
            
            // Asignar al input oculto
            if (otpCodeHidden) {
                otpCodeHidden.value = otpCode;
            }
            
            // Habilitar botón con animación
            if (btnVerifyOTP) {
                btnVerifyOTP.disabled = false;
                btnVerifyOTP.classList.add('pulse');
                setTimeout(() => btnVerifyOTP.classList.remove('pulse'), 600);
            }
        } else {
            // Deshabilitar botón
            if (btnVerifyOTP) {
                btnVerifyOTP.disabled = true;
            }
            
            // Limpiar input oculto
            if (otpCodeHidden) {
                otpCodeHidden.value = '';
            }
        }
    }

    /**
     * Muestra una alerta personalizada
     */
    function showAlert(message, type = 'info') {
        // Crear elemento de alerta
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        alertDiv.setAttribute('role', 'alert');
        alertDiv.innerHTML = `
            <i class="bi bi-${type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Insertar antes del formulario
        if (formVerifyOTP) {
            formVerifyOTP.parentNode.insertBefore(alertDiv, formVerifyOTP);
            
            // Auto-remover después de 5 segundos
            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        }
    }

    /**
     * Maneja el envío del formulario
     */
    function handleFormSubmit(event) {
        // Verificar que todos los campos estén llenos
        const allFilled = Array.from(otpInputs).every(input => input.value !== '');
        
        if (!allFilled) {
            event.preventDefault();
            showAlert('Por favor, completa todos los dígitos del código', 'error');
            
            // Marcar inputs vacíos como error
            otpInputs.forEach(input => {
                if (!input.value) {
                    input.classList.add('error');
                }
            });
            
            return false;
        }
        
        // Deshabilitar botón para evitar doble envío
        if (btnVerifyOTP) {
            btnVerifyOTP.disabled = true;
            btnVerifyOTP.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span><span>Verificando...</span>';
        }
        
        return true;
    }

    // ============================================
    // INICIALIZACIÓN
    // ============================================
    
    /**
     * Inicializa todos los event listeners
     */
    function init() {
        // Event listeners para inputs OTP
        otpInputs.forEach((input, index) => {
            input.dataset.index = index;
            input.addEventListener('input', handleOTPInput);
            input.addEventListener('keydown', handleOTPKeydown);
            input.addEventListener('paste', handleOTPPaste);
        });
        
        // Event listener para el formulario
        if (formVerifyOTP) {
            formVerifyOTP.addEventListener('submit', handleFormSubmit);
        }
        
        // Enfocar el primer input
        if (otpInputs.length > 0) {
            otpInputs[0].focus();
        }
        
        // Iniciar temporizador
        startTimer();
        
        console.log('✅ OTP Verification inicializado correctamente');
    }

    // Ejecutar inicialización
    init();
});