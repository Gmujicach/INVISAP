document.addEventListener('DOMContentLoaded', () => {
  const tipoSolicitudSelect = document.getElementById('tipo_solicitud');
  const form = document.querySelector('form');

  const secciones = {
    'Comunidad': document.getElementById('seccion_comunidad'),
    'Institucion': document.getElementById('seccion_institucion'),
    'Particular': document.getElementById('seccion_particular')
  };

  const toggleSecciones = () => {
    const seleccion = tipoSolicitudSelect.value;
    for (const [key, section] of Object.entries(secciones)) {
      if (key === seleccion) {
        section.style.display = 'block';
        section.querySelectorAll('input, select, textarea').forEach(el => el.disabled = false);
      } else {
        section.style.display = 'none';
        section.querySelectorAll('input, select, textarea').forEach(el => {
          el.disabled = true;
          clearFeedback(el);
        });
      }
    }
  };

  tipoSolicitudSelect.addEventListener('change', toggleSecciones);

  const regexTexto = /^[a-zA-ZÁÉÍÓÚáéíóúÑñ\s]+$/;
  const regexCedula = /^\d{7,10}$/;
  const regexTelefono = /^(0414|0424|0412|0416|0426|0251|0212)-?\d{7}$/;
  const regexCorreo = /^[a-zA-Z0-9._%+-ñÑáéíóúÁÉÍÓÚ]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

  const getParent = (input) => {
    return input.closest('.col-md-12, .col-md-8, .col-md-6, .col-md-5, .col-md-4, .col-md-3') || input.parentElement;
  };

  const showError = (input, message) => {
    input.classList.add('is-invalid');
    input.classList.remove('is-valid');
    const parent = getParent(input);
    if (parent) {
      const feedback = parent.querySelector('.invalid-feedback');
      if (feedback) {
        feedback.textContent = message;
        feedback.style.display = 'block';
      }
      const validFeedback = parent.querySelector('.valid-feedback');
      if (validFeedback) {
        validFeedback.style.display = 'none';
      }
    }
  };

  const showSuccess = (input, message) => {
    input.classList.add('is-valid');
    input.classList.remove('is-invalid');
    const parent = getParent(input);
    if (parent) {
      const feedback = parent.querySelector('.invalid-feedback');
      if (feedback) {
        feedback.style.display = 'none';
      }
      const validFeedback = parent.querySelector('.valid-feedback');
      if (validFeedback) {
        validFeedback.textContent = message || 'Correcto';
        validFeedback.style.display = 'block';
      }
    }
  };

  const clearFeedback = (input) => {
    input.classList.remove('is-invalid', 'is-valid');
    const parent = getParent(input);
    if (parent) {
      const feedback = parent.querySelector('.invalid-feedback');
      if (feedback) {
        feedback.style.display = 'none';
        feedback.textContent = '';
      }
      const validFeedback = parent.querySelector('.valid-feedback');
      if (validFeedback) {
        validFeedback.style.display = 'none';
      }
    }
  };

  const validateField = (input) => {
    if (input.disabled) return true;

    const name = input.name;
    const value = input.value.trim();

    if (input.tagName === 'SELECT') {
      if (!value) {
        showError(input, 'Debe seleccionar una opción');
        return false;
      }
      showSuccess(input);
      return true;
    }

    if (input.hasAttribute('required') && !value) {
      showError(input, 'Este campo es obligatorio');
      return false;
    }

    if (!value) {
      showSuccess(input);
      return true;
    }

    if (input.type === 'email') {
      if (!regexCorreo.test(value)) {
        showError(input, 'Correo electrónico inválido');
        return false;
      }
      showSuccess(input);
      return true;
    }

    if (name.includes('cedula')) {
      if (!regexCedula.test(value)) {
        showError(input, 'Cédula inválida (7 a 10 dígitos)');
        return false;
      }
      showSuccess(input);
      return true;
    }

    if (input.type === 'tel' || name.includes('telefono')) {
      if (!regexTelefono.test(value)) {
        showError(input, 'Teléfono inválido (ej: 04121234567)');
        return false;
      }
      showSuccess(input);
      return true;
    }

    if (input.hasAttribute('pattern')) {
      const pattern = input.getAttribute('pattern');
      if (!new RegExp(pattern).test(value)) {
        showError(input, 'Formato inválido');
        return false;
      }
    }

    if (name.includes('problematica')) {
      if (value.length < 15) {
        showError(input, 'Describa la problemática (mínimo 15 caracteres)');
        return false;
      }
    }

    if (input.hasAttribute('minlength') && value.length < parseInt(input.getAttribute('minlength'))) {
      showError(input, `Mínimo ${input.getAttribute('minlength')} caracteres`);
      return false;
    }

    if (input.hasAttribute('maxlength') && value.length > parseInt(input.getAttribute('maxlength'))) {
      showError(input, `Máximo ${input.getAttribute('maxlength')} caracteres`);
      return false;
    }

    showSuccess(input);
    return true;
  };

  form.querySelectorAll('input, select, textarea').forEach(input => {
    input.addEventListener('input', () => validateField(input));
    input.addEventListener('change', () => validateField(input));
  });

  form.addEventListener('submit', (e) => {
    let isValid = true;
    const tipo = tipoSolicitudSelect.value;

    clearFeedback(tipoSolicitudSelect);

    if (!tipo) {
      showError(tipoSolicitudSelect, 'Debe seleccionar un tipo de solicitante');
      isValid = false;
    } else {
      showSuccess(tipoSolicitudSelect);
    }

    if (tipo === 'Comunidad') {
      const nombre = document.querySelector('input[name="com_nombre"]');
      const muni = document.querySelector('select[name="com_municipio"]');
      const sector = document.querySelector('input[name="com_sector"]');
      const ced = document.querySelector('input[name="com_cedula"]');
      const tel = document.querySelector('input[name="com_telefono"]');
      const correo = document.querySelector('input[name="com_correo"]');

      if (!comprobarInput(nombre, v => v.trim().length >= 5, 'Ingrese un nombre válido (mínimo 5 caracteres)')) isValid = false;
      if (!comprobarSelect(muni, 'Seleccione un municipio')) isValid = false;
      if (!comprobarInput(sector, v => v.trim().length >= 3, 'Ingrese el sector (mínimo 3 caracteres)')) isValid = false;
      if (!comprobarCedula(ced)) isValid = false;
      if (!comprobarTelefono(tel)) isValid = false;
      if (!comprobarCorreo(correo)) isValid = false;
    }

    if (tipo === 'Institucion') {
      const nombre = document.querySelector('input[name="inst_nombre"]');
      const muni = document.querySelector('select[name="inst_municipio"]');
      const correo = document.querySelector('input[name="inst_correo"]');
      const tel = document.querySelector('input[name="inst_telefono"]');
      const dirNombre = document.querySelector('input[name="inst_director_nombre"]');
      const dirCed = document.querySelector('input[name="inst_director_cedula"]');

      if (!comprobarInput(nombre, v => v.trim().length >= 3, 'Ingrese la razón social (mínimo 3 caracteres)')) isValid = false;
      if (!comprobarSelect(muni, 'Seleccione un municipio')) isValid = false;
      if (!comprobarCorreo(correo)) isValid = false;
      if (!comprobarTelefono(tel)) isValid = false;
      if (!comprobarInput(dirNombre, v => regexTexto.test(v.trim()), 'Nombre de representante inválido (solo letras)')) isValid = false;
      if (!comprobarCedula(dirCed)) isValid = false;
    }

    if (tipo === 'Particular') {
      const nombre = document.querySelector('input[name="part_nombre"]');
      const apellido = document.querySelector('input[name="part_apellido"]');
      const ced = document.querySelector('input[name="part_cedula"]');
      const correo = document.querySelector('input[name="part_correo"]');
      const tel = document.querySelector('input[name="part_telefono"]');

      if (!comprobarInput(nombre, v => regexTexto.test(v.trim()), 'Ingrese el nombre (solo letras)')) isValid = false;
      if (!comprobarInput(apellido, v => regexTexto.test(v.trim()), 'Ingrese el apellido (solo letras)')) isValid = false;
      if (!comprobarCedula(ced)) isValid = false;
      if (!comprobarCorreo(correo)) isValid = false;
      if (!comprobarTelefono(tel)) isValid = false;
    }

    const problematica = document.querySelector('textarea[name="problematica"]');
    if (problematica) {
      if (!comprobarInput(problematica, v => v.trim().length >= 15, 'Describa la problemática (mínimo 15 caracteres)')) isValid = false;
    }

    if (!isValid) e.preventDefault();
  });

  function comprobarInput(input, validar, mensajeError) {
    if (!input) return true;
    if (input.disabled) { clearFeedback(input); return true; }
    const value = input.value.trim();
    if (!validar(value)) {
      showError(input, mensajeError);
      return false;
    }
    showSuccess(input);
    return true;
  }

  function comprobarSelect(select, mensajeError) {
    if (!select) return true;
    if (select.disabled) { clearFeedback(select); return true; }
    const value = (select.value || '').trim();
    if (!value || value === '0') {
      showError(select, mensajeError);
      return false;
    }
    showSuccess(select);
    return true;
  }

  function comprobarCedula(input) {
    if (!input) return true;
    if (input.disabled) { clearFeedback(input); return true; }
    if (!regexCedula.test(input.value.trim())) {
      showError(input, 'Cédula inválida (7 a 10 dígitos)');
      return false;
    }
    showSuccess(input);
    return true;
  }

  function comprobarTelefono(input) {
    if (!input) return true;
    if (input.disabled) { clearFeedback(input); return true; }
    if (!regexTelefono.test(input.value.trim())) {
      showError(input, 'Teléfono inválido (ej: 04121234567)');
      return false;
    }
    showSuccess(input);
    return true;
  }

  function comprobarCorreo(input) {
    if (!input) return true;
    if (input.disabled) { clearFeedback(input); return true; }
    if (!regexCorreo.test(input.value.trim())) {
      showError(input, 'Correo electrónico inválido');
      return false;
    }
    showSuccess(input);
    return true;
  }
});
