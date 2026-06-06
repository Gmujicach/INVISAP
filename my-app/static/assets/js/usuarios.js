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


function blinkPasswordEye(eye) {
  eye.classList.add('eye-blink');
  setTimeout(() => eye.classList.remove('eye-blink'), 240);
}

function installPasswordReveal(passwordInput) {
  const inputGroup = passwordInput.closest('.input-group, .password-input-wrapper');
  if (!inputGroup) return;
  let toggleButton = inputGroup.querySelector('.btn-password-toggle');
  if (!toggleButton) {
    toggleButton = document.createElement('button');
    toggleButton.type = 'button';
    toggleButton.className = 'btn btn-outline-secondary btn-password-toggle';
    toggleButton.setAttribute('aria-label', 'Mostrar contraseña');
    toggleButton.tabIndex = -1;
    toggleButton.innerHTML = `
      <span class="password-eye" aria-hidden="true">
        <svg class="button-password-svg" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path class="lid lid--upper" d="M1 12C1 12 5 4 12 4C19 4 23 12 23 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
          <path class="lid lid--lower" d="M1 12C1 12 5 20 12 20C19 20 23 12 23 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
          <g class="eye">
            <circle cy="12" cx="12" r="4" fill="currentColor" />
            <circle cy="11" cx="13" r="1" fill="#000" />
          </g>
        </svg>
      </span>
      <span class="sr-only visually-hidden">Mostrar contraseña</span>
    `;
    inputGroup.appendChild(toggleButton);
  }

  const eye = toggleButton.querySelector('.password-eye');
  if (!eye) return;

  setupPasswordEyeBlink(eye);

  toggleButton.addEventListener('click', function () {
    const willShow = passwordInput.type === 'password';
    // animar cierre de párpados al hacer click
    eye.classList.add('closing');
    // espera la animación y luego alterna el tipo
    setTimeout(() => {
      passwordInput.type = willShow ? 'text' : 'password';
      toggleButton.setAttribute('aria-label', willShow ? 'Ocultar contraseña' : 'Mostrar contraseña');
      eye.classList.toggle('open', willShow);
      // quitar clase de cierre para permitir la animación inversa
      eye.classList.remove('closing');
      blinkPasswordEye(eye);
    }, 220);
  });
}


function setupPasswordEyeBlink(eye) {
  if (eye._blinkInterval) return;
  eye._blinkInterval = setInterval(() => {
    blinkPasswordEye(eye);
  }, 5000 + Math.floor(Math.random() * 6000));
}

document.addEventListener('DOMContentLoaded', function () {
  const forms = document.querySelectorAll('form');
  const passwordRegex = /^(?=.*[A-Za-zÁÉÍÓÚáéíóúÑñ])(?=.*[^A-Za-z0-9ÁÉÍÓÚáéíóúÑñ]).{8,12}$/;

  forms.forEach(form => {
    const passwordInput = form.querySelector('input[name="pass_user"]');
    if (!passwordInput) return;

    installPasswordReveal(passwordInput);
    passwordInput.setAttribute('minlength', '8');
    passwordInput.setAttribute('maxlength', '12');
    passwordInput.setAttribute('pattern', '(?=.*[A-Za-zÁÉÍÓÚáéíóúÑñ])(?=.*[^A-Za-z0-9ÁÉÍÓÚáéíóúÑñ]).{8,12}');
    const feedbackId = `${passwordInput.name}_feedback`;
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
        showPasswordError('La clave debe tener entre 8 y 12 caracteres, incluir letras y al menos un carácter especial.');
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
