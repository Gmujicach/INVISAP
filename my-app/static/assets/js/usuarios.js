/**
 * VIEW-CONTROLLED: USUARIOS
 * Encargado de la interacción del usuario y renderizado de componentes.
 */
function openDashboard(htmlContent) {
    const panel = document.getElementById('moduleDashboard');
    const overlay = document.getElementById('dashboardOverlay');
    const container = document.getElementById('dashboardInjectedContent');
    
    container.innerHTML = htmlContent;
    panel.classList.add('open');
    overlay.style.display = 'block';
}

function closeDashboard() {
    document.getElementById('moduleDashboard').classList.remove('open');
    document.getElementById('dashboardOverlay').style.display = 'none';
}

function eliminarUsuario(id) {
    if (confirm("¿Está seguro que desea eliminar este usuario de Invilara?")) {
        window.location.href = `/borrar-usuario/${id}`;
    }
}

function triggerUsuariosDashboard() {
    const usuarios = window.resp_usuariosBD || [];
    
    let rowsHtml = usuarios.length > 0 
        ? usuarios.map(u => `
            <tr>
              <td><span class="fw-semibold">${u.name_surname}</span></td>
              <td>${u.email_user}</td>
              <td class="text-center">
                <div class="d-flex justify-content-center gap-2">
                  <a href="/buscar-usuario/${u.id}" class="btn btn-warning btn-icon-only" title="Modificar">
                    <i class="bi bi-pencil-square text-white"></i>
                  </a>
                  <button type="button" onclick="eliminarUsuario('${u.id}')" class="btn btn-danger btn-icon-only" title="Eliminar">
                    <i class="bi bi-trash3"></i>
                  </button>
                </div>
              </td>
            </tr>`).join('')
        : '<tr><td colspan="3" class="text-center">No hay datos</td></tr>';

    const content = `
      <div class="dashboard-section">
        <h4 class="fw-bold mb-4" style="color: #08b324;"><i class="bi bi-person-plus-fill me-2"></i>Registrar</h4>
        <form action="/saved-register" method="POST">
          <div class="mb-3"><label class="form-label">Nombre</label><input type="text" name="name_surname" class="form-control" required></div>
          <div class="mb-3"><label class="form-label">Email</label><input type="email" name="email_user" class="form-control" required></div>
          <div class="mb-4"><label class="form-label">Clave</label><input type="password" name="pass_user" class="form-control" required></div>
          <button type="submit" class="btn w-100 text-white" style="background-color: #08b324;">Registrar</button>
        </form>
      </div>
      <div class="dashboard-section">
        <h4 class="fw-bold mb-4" style="color: #08b324;"><i class="bi bi-person-check-fill me-2"></i>Listado</h4>
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr><th>Usuario</th><th>Email</th><th class="text-center">Acciones</th></tr>
            </thead>
            <tbody>${rowsHtml}</tbody>
          </table>
        </div>
      </div>
    `;
    openDashboard(content);
}

function injectPasswordRevealStyles() {
  if (document.getElementById('password-reveal-styles')) return;
  const style = document.createElement('style');
  style.id = 'password-reveal-styles';
  style.textContent = `
    .btn-password-toggle {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 3rem;
      width: 3rem;
      border-left: 0;
      border-top-right-radius: .375rem;
      border-bottom-right-radius: .375rem;
      background: transparent;
      color: #495057;
    }
    .btn-password-toggle:hover {
      background: rgba(0, 0, 0, .04);
    }
    .password-eye {
      position: relative;
      display: inline-flex;
      width: 1.4rem;
      height: 0.95rem;
      border: 2px solid #5b5b5b;
      border-radius: 999px;
      background: radial-gradient(circle at 50% 45%, #ffffff 46%, #eef2f5 100%);
      overflow: hidden;
      transition: border-color .2s ease, background .2s ease, transform .2s ease;
    }
    .password-eye::before,
    .password-eye::after {
      content: '';
      position: absolute;
      left: 0;
      width: 100%;
      height: 50%;
      background: #5b5b5b;
      transition: transform .18s ease, opacity .18s ease;
      pointer-events: none;
    }
    .password-eye::before {
      top: 0;
      border-bottom-left-radius: 999px;
      border-bottom-right-radius: 999px;
      transform-origin: center bottom;
      transform: translateY(0) scaleY(1);
    }
    .password-eye::after {
      bottom: 0;
      border-top-left-radius: 999px;
      border-top-right-radius: 999px;
      transform-origin: center top;
      transform: translateY(0) scaleY(1);
    }
    .password-eye.open::before {
      transform: translateY(-110%) scaleY(.25);
      opacity: 0.35;
    }
    .password-eye.open::after {
      transform: translateY(110%) scaleY(.25);
      opacity: 0.35;
    }
    .password-eye .password-pupil {
      position: absolute;
      top: 50%;
      left: 50%;
      width: .45rem;
      height: .45rem;
      background: #111;
      border-radius: 50%;
      transform: translate(-50%, -50%);
      transition: transform .08s ease;
      box-shadow: inset 0 0 0 1px rgba(255,255,255,.2);
    }
    .password-eye.eye-blink::before {
      transform: translateY(0) scaleY(.2);
    }
    .password-eye.eye-blink::after {
      transform: translateY(0) scaleY(.2);
    }
    .password-eye.open {
      transform: scale(1.02);
      border-color: #0b6b2f;
    }
    .password-eye.eye-blink {
      animation: password-eye-blink .24s ease-in-out;
    }
    @keyframes password-eye-blink {
      0%,100% { transform: scaleY(1); }
      50% { transform: scaleY(.14); }
    }
  `;
  document.head.appendChild(style);
}

function setPasswordPupilPosition(eye, mouseEvent) {
  const pupil = eye.querySelector('.password-pupil');
  if (!pupil) return;
  const rect = eye.getBoundingClientRect();
  const centerX = rect.left + rect.width / 2;
  const centerY = rect.top + rect.height / 2;
  const deltaX = mouseEvent.clientX - centerX;
  const deltaY = mouseEvent.clientY - centerY;
  const maxDistance = Math.min(rect.width, rect.height) * 0.18;
  const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
  const ratio = distance > maxDistance ? maxDistance / distance : 1;
  const moveX = deltaX * ratio;
  const moveY = deltaY * ratio;
  pupil.style.transform = `translate(calc(-50% + ${moveX}px), calc(-50% + ${moveY}px))`;
}

function resetPasswordPupil(eye) {
  const pupil = eye.querySelector('.password-pupil');
  if (!pupil) return;
  pupil.style.transform = 'translate(-50%, -50%)';
}

function blinkPasswordEye(eye) {
  eye.classList.add('eye-blink');
  setTimeout(() => eye.classList.remove('eye-blink'), 240);
}

const passwordEyes = [];
let passwordEyeFollowInitialized = false;

function installPasswordReveal(passwordInput) {
  const inputGroup = passwordInput.closest('.input-group');
  if (!inputGroup) return;
  let toggleButton = inputGroup.querySelector('.btn-password-toggle');
  if (!toggleButton) {
    toggleButton = document.createElement('button');
    toggleButton.type = 'button';
    toggleButton.className = 'btn btn-outline-secondary btn-password-toggle';
    toggleButton.setAttribute('aria-label', 'Mostrar contraseña');
    toggleButton.tabIndex = -1;
    toggleButton.innerHTML = '<span class="password-eye" aria-hidden="true"><span class="password-pupil"></span></span>';
    inputGroup.appendChild(toggleButton);
  }

  const eye = toggleButton.querySelector('.password-eye');
  if (!eye) return;

  passwordEyes.push(eye);
  ensurePasswordEyeFollowListener();
  setupPasswordEyeBlink(eye);

  toggleButton.addEventListener('click', function () {
    const showPassword = passwordInput.type === 'password';
    passwordInput.type = showPassword ? 'text' : 'password';
    toggleButton.setAttribute('aria-label', showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña');
    eye.classList.toggle('open', showPassword);
    blinkPasswordEye(eye);
  });
}

function ensurePasswordEyeFollowListener() {
  if (passwordEyeFollowInitialized) return;
  passwordEyeFollowInitialized = true;
  document.addEventListener('mousemove', function (event) {
    passwordEyes.forEach(eye => setPasswordPupilPosition(eye, event));
  });
}

function setupPasswordEyeBlink(eye) {
  if (eye._blinkInterval) return;
  eye._blinkInterval = setInterval(() => {
    blinkPasswordEye(eye);
  }, 5000 + Math.floor(Math.random() * 6000));
}

document.addEventListener('DOMContentLoaded', function () {
  injectPasswordRevealStyles();
  const forms = document.querySelectorAll('form');
  const passwordRegex = /^(?=.*[A-Za-z])(?=.*[^A-Za-z0-9]).{8,12}$/;

  forms.forEach(form => {
    const passwordInput = form.querySelector('input[name="pass_user"]');
    if (!passwordInput) return;

    installPasswordReveal(passwordInput);
    passwordInput.setAttribute('minlength', '8');
    passwordInput.setAttribute('maxlength', '12');
    passwordInput.setAttribute('autocomplete', 'new-password');

    const feedbackId = passwordInput.name + '_feedback';
    let feedback = document.getElementById(feedbackId);
    if (!feedback) {
      feedback = document.createElement('div');
      feedback.id = feedbackId;
      feedback.className = 'invalid-feedback';
      passwordInput.parentNode.appendChild(feedback);
    }

    function showPasswordError(message) {
      passwordInput.classList.add('is-invalid');
      passwordInput.classList.remove('is-valid');
      feedback.textContent = message;
    }

    function clearPasswordError() {
      passwordInput.classList.remove('is-invalid');
      passwordInput.classList.add('is-valid');
      feedback.textContent = '';
    }

    passwordInput.addEventListener('input', function () {
      const value = passwordInput.value;
      if (!value) {
        passwordInput.classList.remove('is-valid', 'is-invalid');
        feedback.textContent = '';
        return;
      }
      if (!passwordRegex.test(value)) {
        showPasswordError('La clave debe tener entre 8 y 12 caracteres, incluir letras y al menos un símbolo.');
      } else {
        clearPasswordError();
      }
    });

    form.addEventListener('submit', function (event) {
      const value = passwordInput.value;
      if (!value && passwordInput.hasAttribute('required')) {
        showPasswordError('La contraseña es obligatoria.');
        event.preventDefault();
        return;
      }
      if (value && !passwordRegex.test(value)) {
        showPasswordError('La clave debe tener entre 8 y 12 caracteres, incluir letras y al menos un símbolo.');
        event.preventDefault();
      }
    });
  });
});
