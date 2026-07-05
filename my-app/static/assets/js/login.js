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

    // --- Organismo Adicional: Modo Oscuro LocalStorage ---
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

    // --- CAPTCHA: No Soy Robot con detección de comportamiento ---
    const formLogin = document.getElementById('formAuthentication');
    const captchaCheckbox = document.getElementById('captcha-checkbox');
    const imageChallenge = document.getElementById('image-challenge');
    const captchaError = document.getElementById('captcha-error');
    
    // Análisis de comportamiento del usuario
    const behavior = {
        mouseMovements: [],
        startTime: Date.now(),
        keystrokes: 0,
        isSuspicious: false
    };
    
    // Variable global para verificación del CAPTCHA
    let captchaVerified = false;
    
    // Capturar movimientos del mouse
    document.addEventListener('mousemove', function(e) {
        behavior.mouseMovements.push({
            x: e.clientX,
            y: e.clientY,
            time: Date.now()
        });
        if (behavior.mouseMovements.length > 100) {
            behavior.mouseMovements.shift();
        }
    });
    
    // Capturar teclas presionadas
    document.addEventListener('keydown', function() {
        behavior.keystrokes++;
    });
    
    // Analizar comportamiento sospechoso
    function analyzeBehavior() {
        const movements = behavior.mouseMovements;
        if (movements.length < 10) {
            behavior.isSuspicious = true;
            return;
        }
        
        // Detectar patrones robóticos: movimientos lineales, muy rápidos o muy lentos
        const distances = [];
        for (let i = 1; i < movements.length; i++) {
            const dx = movements[i].x - movements[i-1].x;
            const dy = movements[i].y - movements[i-1].y;
            const dist = Math.sqrt(dx*dx + dy*dy);
            distances.push(dist);
        }
        
        // Si todos los movimientos son iguales (línea recta perfecta) = robot
        const avgDist = distances.reduce((a,b) => a+b, 0) / distances.length;
        const sameDistances = distances.filter(d => d > avgDist * 0.8 && d < avgDist * 1.2).length;
        if (sameDistances > distances.length * 0.8) {
            behavior.isSuspicious = true;
        }
        
        // Si muy pocos movimientos en mucho tiempo = robot
        const elapsed = Date.now() - behavior.startTime;
        if (movements.length < 20 && elapsed > 3000) {
            behavior.isSuspicious = true;
        }
    }
    
    // Generar imágenes SVG dinámicamente
    function generateCaptchaImages() {
        const themes = [
            { name: 'infraestructura', correct: ['🏗️', '🛣️', '🏢', '🌉', '🚧'], wrong: ['🚗', '🐕', '🌳', '🐱', '🍕'] },
            { name: 'agua', correct: ['💧', '🌊', '🚰', '🚿'], wrong: ['🔥', '🌪️', '⛄', '🌵'] },
            { name: 'obras', correct: ['🔨', '🪛', '🧰', '🏗️'], wrong: ['🎮', '🎸', '🎹', '🎤'] }
        ];
        
        const theme = themes[Math.floor(Math.random() * themes.length)];
        const grid = document.querySelector('.image-grid');
        grid.innerHTML = '';
        
        const colors = ['#4CAF50', '#2196F3', '#9C27B0', '#f44336', '#FF9800', '#795548'];
        const allImages = [...theme.correct, ...theme.wrong].sort(() => Math.random() - 0.5).slice(0, 6);
        
        allImages.forEach((emoji, index) => {
            const isCorrect = theme.correct.includes(emoji);
            const color = colors[index % colors.length];
            const div = document.createElement('div');
            div.className = 'image-option';
            div.dataset.type = isCorrect ? 'correct' : 'wrong';
            div.innerHTML = `<img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect fill='%23${color.substring(1)}' width='100' height='100'/%3E%3Ctext x='50' y='55' font-size='40' text-anchor='middle'%3E${emoji}%3C/text%3E%3C/svg%3E" alt="${emoji}">`;
            grid.appendChild(div);
        });
        
        // Actualizar título del desafío
        const challengeTitle = document.querySelector('.challenge-title');
        challengeTitle.innerHTML = `Selecciona todas las imágenes con <strong>${theme.name}</strong>`;
    }
    
    // Inicializar CAPTCHA
    generateCaptchaImages();
    
    // Actualizar event listeners para imágenes dinámicas
    function updateImageListeners() {
        document.querySelectorAll('.image-option').forEach(img => {
            img.replaceWith(img.cloneNode(true)); // Clonar para eliminar listeners previos
        });
    }
    
    if (formLogin && captchaCheckbox) {
        formLogin.addEventListener('submit', function(e) {
            analyzeBehavior();
            
            // Si comportamiento sospechoso, requiere verificación de imágenes
            if (behavior.isSuspicious && !captchaVerified) {
                e.preventDefault();
                generateCaptchaImages();
                updateImageListeners();
                imageChallenge.classList.add('active');
                if (captchaError) captchaError.style.display = 'none';
                return false;
            }
            
            // Si el checkbox no está marcado
            if (!captchaCheckbox.checked) {
                e.preventDefault();
                if (captchaError) {
                    captchaError.style.display = 'block';
                    captchaError.textContent = 'Por favor, confirma que no eres un robot marcando la casilla.';
                }
                return false;
            }
            
            return true;
        });
    }
    
    // Usar event delegation para imágenes dinámicas
    document.addEventListener('click', function(e) {
        if (e.target.closest('.image-option')) {
            const option = e.target.closest('.image-option');
            option.classList.toggle('selected');
        }
    });
    
    // Botón de verificación del captcha de imágenes
    const verifyCaptchaBtn = document.getElementById('verify-captcha');
    const requiredSelections = 2;
    const imageChallengeError = document.getElementById('image-challenge-error');
    
    if (verifyCaptchaBtn) {
        verifyCaptchaBtn.addEventListener('click', function() {
            const correctSelected = document.querySelectorAll('.image-option.selected[data-type="correct"]').length;
            const incorrectSelected = document.querySelectorAll('.image-option.selected[data-type="wrong"]').length;
            
            // Validar que seleccione solo imágenes correctas
            if (correctSelected >= requiredSelections && incorrectSelected === 0) {
                captchaVerified = true;
                imageChallenge.classList.remove('active');
                captchaCheckbox.checked = true;
                
                // Limpiar selección
                document.querySelectorAll('.image-option').forEach(img => img.classList.remove('selected'));
                
                // Enviar formulario
                setTimeout(function() {
                    formLogin.submit();
                }, 300);
            } else {
                if (imageChallengeError) {
                    imageChallengeError.style.display = 'block';
                    if (incorrectSelected > 0) {
                        imageChallengeError.textContent = 'Selecciona solo imágenes correctas. Evita las imágenes incorrectas.';
                    } else {
                        imageChallengeError.textContent = `Selecciona al menos ${requiredSelections} imágenes correctas.`;
                    }
                }
            }
        });
    }
});