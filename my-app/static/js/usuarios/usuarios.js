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
        fetch(`/users/delete/${id}`)
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data && data.status === 'success') {
                    var row = document.querySelector(`tr[data-id-usuario="${id}"]`);
                    if (row) {
                        row.style.transition = 'opacity 0.4s';
                        row.style.opacity = '0';
                        setTimeout(function() { row.remove(); }, 400);
                    } else {
                        setTimeout(function() { location.reload(); }, 800);
                    }
                } else {
                    alert(data && data.message ? data.message : 'Error al eliminar');
                }
            })
            .catch(function() {
                alert('Error de conexión');
            });
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
                  <a href="/users/edit/${u.id}" class="btn btn-warning btn-icon-only" title="Modificar">
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

document.addEventListener('DOMContentLoaded', () => {
    /**
     * Componente Molécula: Inicialización de revelación de contraseña
     * Busca todos los elementos compatibles con el diseño atómico
     */
    const initPasswordToggles = () => {
        const toggleButtons = document.querySelectorAll('.password-toggle-btn');
        
        toggleButtons.forEach(btn => {
            const container = btn.closest('.input-group');
            const input = container ? container.querySelector('.password-input') : null;
            const icon = btn.querySelector('.toggle-icon');
            const molecule = btn.closest('.molecule-password-field');
            const helpText = molecule ? molecule.querySelector('#passwordHelp') : null;

            if (!input || !icon) return;

            // Funcionalidad de Revelación Fija
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const isPassword = input.type === 'password';
                input.type = isPassword ? 'text' : 'password';
                
                // Actualización Atómica del Icono
                icon.classList.toggle('bi-eye', isPassword);
                icon.classList.toggle('bi-eye-slash', !isPassword);
                
                // Accesibilidad y estado visual
                btn.setAttribute('aria-label', isPassword ? 'Ocultar contraseña' : 'Mostrar contraseña');
            });

            // Feedback dinámico de validación (Mivel Molécula)
            if (helpText) {
                input.addEventListener('input', () => {
                    helpText.classList.toggle('d-none', input.value.trim() === '');
                });
            }
        });
    };

    initPasswordToggles();


    // Lógica de validación Regex (Nivel Organismo/Formulario)
    const passwordRegex = /^(?=.*[A-Za-zÁÉÍÓÚáéíóúÑñ])(?=.*[^A-Za-z0-9ÁÉÍÓÚáéíóúÑñ]).{8,12}$/;
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        const passwordInput = form.querySelector('.password-input');
        if (!passwordInput) return;

        passwordInput.addEventListener('input', () => {
            const value = passwordInput.value;
            if (value && !passwordRegex.test(value)) {
                passwordInput.classList.add('is-invalid');
            } else {
                passwordInput.classList.remove('is-invalid');
            }
        });
    });
  });
