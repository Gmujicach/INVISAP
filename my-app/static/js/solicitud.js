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
          removeError(el);
        });
      }
    }
  };

  tipoSolicitudSelect.addEventListener('change', toggleSecciones);

  const regexTexto = /^[a-zA-ZÁÉÍÓÚáéíóúÑñ\s]+$/; 
  const regexCedula = /^\d{7,10}$/; 
  const regexTelefono = /^(0414|0424|0412|0416|0426|0251|0212)-?\d{7}$/;
  const regexCorreo = /^[a-zA-Z0-9._%+-ñÑáéíóúÁÉÍÓÚ]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

  const setError = (input, message) => {
    input.classList.add('is-invalid');
    let parent = input.closest('.col-md-12, .col-md-8, .col-md-6, .col-md-5, .col-md-4, .col-md-3');
    if (!parent) parent = input.parentElement;

    let feedback = parent.querySelector('.invalid-feedback');
    if (!feedback) {
      feedback = document.createElement('div');
      feedback.className = 'invalid-feedback d-block';
      parent.appendChild(feedback);
    } else {
      feedback.classList.add('d-block');
      feedback.style.display = 'block';
    }
    feedback.textContent = message;
  };

  const removeError = (input) => {
    input.classList.remove('is-invalid');
    let parent = input.closest('.col-md-12, .col-md-8, .col-md-6, .col-md-5, .col-md-4, .col-md-3');
    if (!parent) parent = input.parentElement;
    
    const feedback = parent.querySelector('.invalid-feedback');
    if (feedback) {
      feedback.classList.remove('d-block');
      feedback.style.display = 'none';
    }
  };

  form.querySelectorAll('input, select, textarea').forEach(input => {
    input.addEventListener('input', () => removeError(input));
    input.addEventListener('change', () => removeError(input));
  });

  form.addEventListener('submit', (e) => {
    let isValid = true;
    const tipo = tipoSolicitudSelect.value;

    if (!tipo) {
      setError(tipoSolicitudSelect, 'Debe seleccionar un perfil.');
      isValid = false;
    }

    if (tipo === 'Comunidad') {
      const nombre = document.querySelector('input[name="com_nombre"]');
      const muni = document.querySelector('select[name="com_municipio"]');
      const sector = document.querySelector('input[name="com_sector"]');
      const ced = document.querySelector('input[name="com_cedula"]');
      const tel = document.querySelector('input[name="com_telefono"]');
      const correo = document.querySelector('input[name="com_correo"]');

      if (nombre.value.trim().length < 5) { setError(nombre, 'Ingrese un nombre válido.'); isValid = false; }
      if (!muni.value) { setError(muni, 'Seleccione un municipio.'); isValid = false; }
      if (sector.value.trim().length < 3) { setError(sector, 'Ingrese el sector.'); isValid = false; }
      if (!regexCedula.test(ced.value.trim())) { setError(ced, 'Cédula inválida (7 a 10 dígitos).'); isValid = false; }
      if (!regexTelefono.test(tel.value.trim())) { setError(tel, 'Teléfono inválido.'); isValid = false; }
      if (!regexCorreo.test(correo.value.trim())) { setError(correo, 'Correo electrónico inválido.'); isValid = false; }
    }

    if (tipo === 'Institucion') {
      const nombre = document.querySelector('input[name="inst_nombre"]');
      const muni = document.querySelector('select[name="inst_municipio"]');
      const correo = document.querySelector('input[name="inst_correo"]');
      const tel = document.querySelector('input[name="inst_telefono"]');
      const dirNombre = document.querySelector('input[name="inst_director_nombre"]');
      const dirCed = document.querySelector('input[name="inst_director_cedula"]');

      if (nombre.value.trim().length < 3) { setError(nombre, 'Ingrese la razón social.'); isValid = false; }
      if (!muni.value) { setError(muni, 'Seleccione un municipio.'); isValid = false; }
      if (!regexCorreo.test(correo.value.trim())) { setError(correo, 'Correo electrónico inválido.'); isValid = false; }
      if (!regexTelefono.test(tel.value.trim())) { setError(tel, 'Teléfono inválido.'); isValid = false; }
      if (!regexTexto.test(dirNombre.value.trim())) { setError(dirNombre, 'Nombre de representante inválido.'); isValid = false; }
      if (!regexCedula.test(dirCed.value.trim())) { setError(dirCed, 'Cédula inválida.'); isValid = false; }
    }

    if (tipo === 'Particular') {
      const nombre = document.querySelector('input[name="part_nombre"]');
      const apellido = document.querySelector('input[name="part_apellido"]');
      const ced = document.querySelector('input[name="part_cedula"]');
      const correo = document.querySelector('input[name="part_correo"]');
      const tel = document.querySelector('input[name="part_telefono"]');

      if (!regexTexto.test(nombre.value.trim())) { setError(nombre, 'Solo letras.'); isValid = false; }
      if (!regexTexto.test(apellido.value.trim())) { setError(apellido, 'Solo letras.'); isValid = false; }
      if (!regexCedula.test(ced.value.trim())) { setError(ced, 'Cédula inválida (7 a 10 dígitos).'); isValid = false; }
      if (!regexCorreo.test(correo.value.trim())) { setError(correo, 'Correo electrónico inválido.'); isValid = false; }
      if (!regexTelefono.test(tel.value.trim())) { setError(tel, 'Teléfono inválido.'); isValid = false; }
    }

    const problematica = document.querySelector('textarea[name="problematica"]');
    if (problematica.value.trim().length < 15) {
      setError(problematica, 'Describa la problemática (mínimo 15 caracteres).');
      isValid = false;
    }

    if (!isValid) e.preventDefault();
  });
});