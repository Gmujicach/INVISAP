/**
 * INVISAP - Login Logic (Atomic UI)
 * Manages Password Strength Checker and Visibility Toggle
 */

'use strict';

document.addEventListener('DOMContentLoaded', function () {
    // Buscar todas las moléculas de password en la página
    const passwordFields = document.querySelectorAll('.molecule-password-field');

    passwordFields.forEach(field => {
        const passwordInput = field.querySelector('.password-input');
        const toggleBtn = field.querySelector('.password-toggle-btn');
        const strengthWidget = field.querySelector('.password-strength-widget');

        // --- Átomo: Toggle de Visibilidad ---
        if (passwordInput && toggleBtn) {
            const icon = toggleBtn.querySelector('.toggle-icon');
            
            toggleBtn.addEventListener('click', function() {
                const isPassword = passwordInput.type === 'password';
                passwordInput.type = isPassword ? 'text' : 'password';
                
                icon.classList.toggle('bi-eye', isPassword);
                icon.classList.toggle('bi-eye-slash', !isPassword);
                passwordInput.focus();
            });
        }

        // --- Organismo: Password Strength Checker ---
        if (passwordInput && strengthWidget) {
            const meter = strengthWidget.querySelector('.strength-meter');
            const label = strengthWidget.querySelector('.strength-label');
            const helpText = field.querySelector('#passwordHelp');
            
            const rules = {
                length: strengthWidget.querySelector('[data-rule="length"]'),
                upperLower: strengthWidget.querySelector('[data-rule="upper-lower"]'),
                symbol: strengthWidget.querySelector('[data-rule="symbol"]')
            };

            const updateRuleUI = (element, isValid) => {
                const icon = element.querySelector('.icon-rule');
                if (isValid) {
                    element.classList.replace('text-danger', 'text-success');
                    if (icon) icon.className = 'bi bi-check-circle-fill me-2 icon-rule';
                } else {
                    element.classList.replace('text-success', 'text-danger');
                    if (icon) icon.className = 'bi bi-circle me-2 icon-rule';
                }
            };

            passwordInput.addEventListener('input', function() {
                const val = passwordInput.value;
                
                if (val.length > 0) {
                    if (strengthWidget.classList.contains('d-none')) {
                        strengthWidget.classList.remove('d-none');
                        // Trigger Entry Animation (Atomic Logic)
                        strengthWidget.classList.add('animate__animated', 'animate__fadeInDown');
                        
                        setTimeout(() => {
                            strengthWidget.classList.remove('animate__fadeInDown');
                        }, 500);
                    }
                    if (helpText) helpText.classList.add('d-none');
                } else {
                    strengthWidget.classList.add('d-none');
                    if (helpText) helpText.classList.remove('d-none');
                }

                const checks = {
                    length: val.length >= 8 && val.length <= 12,
                    upperLower: /[a-z]/.test(val) && /[A-Z]/.test(val),
                    symbol: /[^A-Za-z0-9]/.test(val)
                };

                updateRuleUI(rules.length, checks.length);
                updateRuleUI(rules.upperLower, checks.upperLower);
                updateRuleUI(rules.symbol, checks.symbol);

                let score = 0;
                if (checks.length) score += 33.3;
                if (checks.upperLower) score += 33.3;
                if (checks.symbol) score += 33.4;

                meter.style.width = `${score}%`;
                
                if (score < 40) {
                    meter.className = 'progress-bar bg-danger';
                    label.textContent = 'Débil';
                    label.className = 'badge bg-label-danger';
                } else if (score < 80) {
                    meter.className = 'progress-bar bg-warning';
                    label.textContent = 'Media';
                    label.className = 'badge bg-label-warning';
                } else {
                    meter.className = 'progress-bar bg-success';
                    label.textContent = 'Fuerte';
                    label.className = 'badge bg-label-success';
                }
            });
        }
    });

    // --- Dark Mode & Profile Molecule Logic ---
    const darkModeSwitch = document.getElementById('dark-mode-switch');
    const themeIcon = document.getElementById('theme-icon');

    if (darkModeSwitch) {
        const loadTheme = () => {
            if (localStorage.getItem('theme') === 'dark') {
                document.body.classList.add('dark-mode');
                darkModeSwitch.checked = true;
                if (themeIcon) themeIcon.className = 'bi bi-moon-stars-fill me-2 fs-5 text-info';
            }
        };
        loadTheme();

        darkModeSwitch.addEventListener('change', () => {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            if (themeIcon) themeIcon.className = isDark ? 'bi bi-moon-stars-fill me-2 fs-5 text-info' : 'bi bi-sun-fill me-2 fs-5 text-warning';
        });
    }

    // Avatar Preview Logic
    const avatarInput = document.getElementById('profile_img');
    const avatarPreview = document.getElementById('avatar-preview');
    if (avatarInput && avatarPreview) {
        avatarInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    avatarPreview.setAttribute('src', e.target.result);
                }
                reader.readAsDataURL(file);
            }
        });
    }
});