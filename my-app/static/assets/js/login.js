/**
 * Login del Sistema Invilara
 */

'use strict';

document.addEventListener('DOMContentLoaded', function () {
    // Buscar todas las moléculas de password en la página
    const passwordFields = document.querySelectorAll('.molecule-password-field');

    passwordFields.forEach(field => {
        const passwordInput = field.querySelector('.password-input');
        const toggleBtn = field.querySelector('.password-toggle-btn');
        const strengthWidget = field.querySelector('.password-strength-widget');

        // --- Átomo: Toggle de Visibilidad (Protección contra Duplicados y Conflictos) ---
        if (passwordInput && toggleBtn) {
            
            // Reemplazar el botón por un clon limpio para purgar cualquier listener duplicado de la plantilla
            const cleanToggleBtn = toggleBtn.cloneNode(true);
            toggleBtn.parentNode.replaceChild(cleanToggleBtn, toggleBtn);
            const cleanIcon = cleanToggleBtn.querySelector('.toggle-icon');

            cleanToggleBtn.addEventListener('click', function(event) {
                event.preventDefault();
                event.stopPropagation(); // Evita que scripts nativos de la plantilla base interfieran
                
                const isPassword = passwordInput.type === 'password';
                passwordInput.type = isPassword ? 'text' : 'password';
                
                // Alternar las clases del ícono de Bootstrap
                if (isPassword) {
                    cleanIcon.classList.remove('bi-eye-slash');
                    cleanIcon.classList.add('bi-eye');
                } else {
                    cleanIcon.classList.remove('bi-eye');
                    cleanIcon.classList.add('bi-eye-slash');
                }
                
                passwordInput.focus();
            });
        }

        // --- Organismo: Password Strength Checker ---
        if (passwordInput && strengthWidget) {
            const meter = strengthWidget.querySelector('.strength-meter');
            const label = strengthWidget.querySelector('.strength-label');
            const helpText = field.querySelector('.form-text');

            passwordInput.addEventListener('input', function () {
                const val = passwordInput.value;
                
                if (val.length === 0) {
                    strengthWidget.classList.add('d-none');
                    if (helpText) helpText.classList.add('d-none');
                    return;
                }

                strengthWidget.classList.remove('d-none');
                if (helpText) helpText.classList.remove('d-none');

                // Lógica de evaluación de reglas regex backend (8-12 carac, letras y símbolo)
                const hasLength = val.length >= 8 && val.length <= 12;
                const hasSymbol = /[^A-Za-z0-9ÁÉÍÓÚáéíóúÑñ]/.test(val);

                const ruleLength = strengthWidget.querySelector('[data-rule="length"]');
                const ruleSymbol = strengthWidget.querySelector('[data-rule="symbol"]');

                let score = 0;

                if (hasLength) {
                    score++;
                    if (ruleLength) {
                        ruleLength.className = 'rule-item text-success mb-1';
                        ruleLength.querySelector('i').className = 'bi bi-check-circle-fill me-2';
                    }
                } else {
                    if (ruleLength) {
                        ruleLength.className = 'rule-item text-danger mb-1';
                        ruleLength.querySelector('i').className = 'bi bi-x-circle-fill me-2';
                    }
                }

                if (hasSymbol) {
                    score++;
                    if (ruleSymbol) {
                        ruleSymbol.className = 'rule-item text-success mb-1';
                        ruleSymbol.querySelector('i').className = 'bi bi-check-circle-fill me-2';
                    }
                } else {
                    if (ruleSymbol) {
                        ruleSymbol.className = 'rule-item text-danger mb-1';
                        ruleSymbol.querySelector('i').className = 'bi bi-x-circle-fill me-2';
                    }
                }

                // Actualizar UI del medidor de seguridad
                if (score === 0) {
                    meter.style.width = '25%';
                    meter.className = 'strength-meter progress-bar bg-danger';
                    label.textContent = 'Insegura';
                    label.className = 'strength-label badge bg-label-danger';
                } else if (score === 1) {
                    meter.style.width = '60%';
                    meter.className = 'strength-meter progress-bar bg-warning';
                    label.textContent = 'Media';
                    label.className = 'strength-label badge bg-label-warning';
                } else if (score === 2) {
                    meter.style.width = '100%';
                    meter.className = 'strength-meter progress-bar bg-success';
                    label.textContent = 'Fuerte (Válida)';
                    label.className = 'strength-label badge bg-label-success';
                }
            });
        }
    });

    // --- Organismo Adicional: Vista previa de Avatar ---
    const avatarInput = document.getElementById('profile_img');
    const avatarPreview = document.getElementById('avatar-preview');
    if (avatarInput && avatarPreview) {
        avatarInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    avatarPreview.setAttribute('src', e.target.result);
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // --- Google reCAPTCHA v2: el widget genera g-recaptcha-response
    //     y se valida en el servidor (verificar_recaptcha). ---
    const formLogin = document.getElementById('formAuthentication');
    const captchaError = document.getElementById('captcha-error');
    const recaptchaWidget = document.querySelector('.g-recaptcha');

    if (formLogin) {
        formLogin.addEventListener('submit', function (e) {
            const response = (typeof grecaptcha !== 'undefined')
                ? grecaptcha.getResponse()
                : '';
            if (!response) {
                e.preventDefault();
                if (captchaError) {
                    captchaError.style.display = 'block';
                    captchaError.textContent = 'Por favor, confirma que no eres un robot.';
                }
                if (recaptchaWidget) recaptchaWidget.scrollIntoView({ behavior: 'smooth', block: 'center' });
                return false;
            }
            if (captchaError) captchaError.style.display = 'none';
            return true;
        });
    }
});