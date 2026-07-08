/* ============================================================
   INVISAP - perfil.js
   Guardado manual con confirmación vía Fetch/AJAX
   ============================================================ */
(function () {
  'use strict';

  const avatarInput = document.getElementById('profile_img');
  const avatarPreview = document.getElementById('avatar-preview');
  const btnChangeAvatar = document.getElementById('btn-change-avatar');

  const nameInput = document.getElementById('name_surname');
  const emailInput = document.getElementById('email_user');
  const newPassInput = document.getElementById('new_pass_user');
  const repetirPassInput = document.getElementById('repetir_pass_user');

  const fbName = document.getElementById('fb-name');
  const fbEmail = document.getElementById('fb-email');
  const fbPass = document.getElementById('fb-pass');
  const statusEl = document.getElementById('perfil-status');

  const btnGuardar = document.getElementById('btn-guardar');
  const btnCancelar = document.getElementById('btn-cancelar');
  const btnConfirmar = document.getElementById('btn-confirmar-guardar');
  const modalConfirmar = document.getElementById('modalConfirmarPerfil');

  const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  const PASSWORD_REGEX = /^(?=.*[A-Za-zÁÉÍÓÚáéíóúÑñ])(?=.*[^A-Za-z0-9ÁÉÍÓÚáéíóúÑñ]).{8,12}$/;

  /* Valores originales para detectar cambios y poder cancelar */
  const original = {
    nombre: nameInput ? nameInput.value.trim() : '',
    correo: emailInput ? emailInput.value.trim() : '',
    avatar: avatarPreview ? avatarPreview.src : ''
  };
  let avatarPendiente = null;

  /* ---------- Utilidades ---------- */
  function setStatus(text, type) {
    if (!statusEl) return;
    statusEl.textContent = text || '';
    statusEl.className = 'perfil-status' + (type ? ' ' + type : '');
  }

  function setFeedback(el, msg, type) {
    if (!el) return;
    el.textContent = msg || '';
    el.className = 'perfil-feedback' + (type ? ' ' + type : '');
  }

  function showToast(message, type) {
    const area = document.getElementById('notification-area');
    if (!area) return;
    const alert = document.createElement('div');
    alert.className = `alert alert-${type === 'error' ? 'danger' : type} alert-molecule alert-dismissible fade show bg-white`;
    alert.setAttribute('role', 'alert');
    alert.innerHTML = `
      <div class="d-flex align-items-center">
        <i class="bi bi-${type === 'success' ? 'check-circle-fill text-success' : 'exclamation-triangle-fill text-danger'} fs-4 me-3"></i>
        <div class="text-dark small fw-semibold">${message}</div>
      </div>
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;
    area.appendChild(alert);
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert.close();
    }, 5000);
  }

  function hayCambios() {
    const nombre = nameInput.value.trim();
    const correo = emailInput.value.trim();
    const passLlena = newPassInput.value || repetirPassInput.value;
    return (
      nombre !== original.nombre ||
      correo !== original.correo ||
      avatarPendiente !== null ||
      !!passLlena
    );
  }

  function actualizarBotones() {
    const activo = hayCambios();
    if (btnGuardar) btnGuardar.disabled = !activo;
    if (btnCancelar) btnCancelar.disabled = !activo;
  }

  /* ---------- Validación en vivo ---------- */
  function validarNombre() {
    const val = nameInput.value.trim();
    if (!val) {
      nameInput.classList.add('is-invalid');
      setFeedback(fbName, 'El nombre es obligatorio.', 'error');
      return false;
    }
    if (val.length < 3) {
      nameInput.classList.add('is-invalid');
      nameInput.classList.remove('is-valid');
      setFeedback(fbName, 'Mínimo 3 caracteres.', 'error');
      return false;
    }
    nameInput.classList.remove('is-invalid');
    nameInput.classList.add('is-valid');
    setFeedback(fbName, '', '');
    return true;
  }

  function validarEmail() {
    const val = emailInput.value.trim();
    if (!val) {
      emailInput.classList.add('is-invalid');
      setFeedback(fbEmail, 'El correo es obligatorio.', 'error');
      return false;
    }
    if (!EMAIL_REGEX.test(val)) {
      emailInput.classList.add('is-invalid');
      emailInput.classList.remove('is-valid');
      setFeedback(fbEmail, 'Correo no válido.', 'error');
      return false;
    }
    emailInput.classList.remove('is-invalid');
    emailInput.classList.add('is-valid');
    setFeedback(fbEmail, '', '');
    return true;
  }

  function validarPassword() {
    const nueva = newPassInput.value;
    const repetir = repetirPassInput.value;
    if (!nueva && !repetir) {
      newPassInput.classList.remove('is-invalid', 'is-valid');
      repetirPassInput.classList.remove('is-invalid', 'is-valid');
      setFeedback(fbPass, '', '');
      return true; // contraseña opcional
    }
    if (nueva && !PASSWORD_REGEX.test(nueva)) {
      newPassInput.classList.add('is-invalid');
      newPassInput.classList.remove('is-valid');
      setFeedback(fbPass, 'Debe tener 8-12 caracteres, letras y un símbolo.', 'error');
      return false;
    }
    if (nueva !== repetir) {
      repetirPassInput.classList.add('is-invalid');
      repetirPassInput.classList.remove('is-valid');
      setFeedback(fbPass, 'Las contraseñas no coinciden.', 'error');
      return false;
    }
    newPassInput.classList.remove('is-invalid');
    newPassInput.classList.add('is-valid');
    repetirPassInput.classList.remove('is-invalid');
    repetirPassInput.classList.add('is-valid');
    setFeedback(fbPass, '', '');
    return true;
  }

  function validarTodo() {
    const okNombre = validarNombre();
    const okEmail = validarEmail();
    const okPass = validarPassword();
    return okNombre && okEmail && okPass;
  }

  /* ---------- Avatar (preview local, se sube al guardar) ---------- */
  function manejarAvatar(file) {
    if (!file) return;
    const permitidas = ['image/png', 'image/jpeg', 'image/gif', 'image/webp'];
    if (!permitidas.includes(file.type)) {
      showToast('Formato de imagen no permitido.', 'error');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      showToast('La imagen supera los 5 MB.', 'error');
      return;
    }
    const reader = new FileReader();
    reader.onload = e => { avatarPreview.src = e.target.result; };
    reader.readAsDataURL(file);
    avatarPendiente = file;
    actualizarBotones();
  }

  function actualizarAvatarSidebar(rutaRelativa) {
    const img = document.getElementById('corner-profile-img');
    if (img) img.src = '/static/' + rutaRelativa;
  }

  function actualizarNombreSidebar(nombre) {
    const el = document.getElementById('corner-profile-name');
    if (el && nombre) el.textContent = nombre;
  }

  /* ---------- Guardar ---------- */
  function guardarPerfil(callback) {
    const fd = new FormData();
    fd.append('name_surname', nameInput.value.trim());
    fd.append('email_user', emailInput.value.trim());
    if (avatarPendiente) fd.append('profile_img', avatarPendiente);

    setStatus('Guardando...', 'saving');
    fetch('/actualizar-perfil-ajax', { method: 'POST', body: fd })
      .then(res => res.json().then(b => ({ ok: res.ok, b })))
      .then(({ ok, b }) => {
        if (ok && b.success) {
          if (b.avatar) {
            avatarPreview.src = '/static/' + b.avatar;
            actualizarAvatarSidebar(b.avatar);
          }
          actualizarNombreSidebar(nameInput.value.trim());
          showToast(b.message || 'Perfil actualizado.', 'success');
          callback && callback(true);
        } else {
          showToast(b.message || 'No se pudo guardar el perfil.', 'error');
          callback && callback(false);
        }
      })
      .catch(() => {
        showToast('Error de conexión al guardar.', 'error');
        callback && callback(false);
      });
  }

  function guardarPassword(callback) {
    const fd = new FormData();
    fd.append('new_pass_user', newPassInput.value);
    fd.append('repetir_pass_user', repetirPassInput.value);
    fetch('/actualizar-clave-perfil-ajax', { method: 'POST', body: fd })
      .then(res => res.json().then(b => ({ ok: res.ok, b })))
      .then(({ ok, b }) => {
        if (ok && b.success) {
          newPassInput.value = '';
          repetirPassInput.value = '';
          newPassInput.classList.remove('is-valid');
          repetirPassInput.classList.remove('is-valid');
          setFeedback(fbPass, '', '');
          showToast(b.message || 'Contraseña actualizada.', 'success');
          callback && callback(true);
        } else {
          showToast(b.message || 'No se pudo cambiar la contraseña.', 'error');
          callback && callback(false);
        }
      })
      .catch(() => {
        showToast('Error de conexión al cambiar la contraseña.', 'error');
        callback && callback(false);
      });
  }

  function confirmarGuardado() {
    if (!validarTodo()) {
      showToast('Corrige los campos marcados antes de guardar.', 'error');
      return;
    }
    const cambiaPass = !!(newPassInput.value || repetirPassInput.value);

    guardarPerfil(perfilOk => {
      if (!perfilOk) {
        setStatus('Error', 'error');
        setTimeout(() => setStatus(''), 2500);
        return;
      }
      const finalizar = () => {
        // Sincronizar valores originales
        original.nombre = nameInput.value.trim();
        original.correo = emailInput.value.trim();
        avatarPendiente = null;
        actualizarBotones();
        setStatus('Guardado', 'success');
        setTimeout(() => setStatus(''), 2500);
      };
      if (cambiaPass) {
        guardarPassword(finalizar);
      } else {
        finalizar();
      }
    });
  }

  function cancelarCambios() {
    nameInput.value = original.nombre;
    emailInput.value = original.correo;
    avatarPreview.src = original.avatar;
    avatarPendiente = null;
    newPassInput.value = '';
    repetirPassInput.value = '';
    nameInput.classList.remove('is-invalid', 'is-valid');
    emailInput.classList.remove('is-invalid', 'is-valid');
    newPassInput.classList.remove('is-invalid', 'is-valid');
    repetirPassInput.classList.remove('is-invalid', 'is-valid');
    setFeedback(fbName, '', '');
    setFeedback(fbEmail, '', '');
    setFeedback(fbPass, '', '');
    setStatus('', '');
    actualizarBotones();
  }

  /* ---------- Eventos ---------- */
  if (nameInput) nameInput.addEventListener('input', () => { validarNombre(); actualizarBotones(); });
  if (emailInput) emailInput.addEventListener('input', () => { validarEmail(); actualizarBotones(); });
  if (newPassInput) newPassInput.addEventListener('input', () => { validarPassword(); actualizarBotones(); });
  if (repetirPassInput) repetirPassInput.addEventListener('input', () => { validarPassword(); actualizarBotones(); });

  if (avatarInput) {
    avatarInput.addEventListener('change', e => {
      const file = e.target.files && e.target.files[0];
      manejarAvatar(file);
      e.target.value = '';
    });
  }
  if (btnChangeAvatar) {
    btnChangeAvatar.addEventListener('click', () => avatarInput && avatarInput.click());
  }

  if (btnGuardar) {
    btnGuardar.addEventListener('click', () => {
      if (modalConfirmar && window.bootstrap) {
        bootstrap.Modal.getOrCreateInstance(modalConfirmar).show();
      } else {
        confirmarGuardado();
      }
    });
  }
  if (btnConfirmar) {
    btnConfirmar.addEventListener('click', () => {
      if (modalConfirmar && window.bootstrap) {
        bootstrap.Modal.getOrCreateInstance(modalConfirmar).hide();
      }
      confirmarGuardado();
    });
  }
  if (btnCancelar) btnCancelar.addEventListener('click', cancelarCambios);

  /* ---------- Revelar contraseña (botones ojo) ---------- */
  document.querySelectorAll('.perfil-field .password-toggle-btn').forEach(btn => {
    const group = btn.closest('.input-group');
    const input = group && group.querySelector('.password-input');
    const icon = btn.querySelector('.toggle-icon');
    if (!input || !icon) return;
    btn.addEventListener('click', e => {
      e.preventDefault();
      const mostrar = input.type === 'password';
      input.type = mostrar ? 'text' : 'password';
      icon.classList.toggle('bi-eye', mostrar);
      icon.classList.toggle('bi-eye-slash', !mostrar);
    });
  });

  actualizarBotones();
})();
