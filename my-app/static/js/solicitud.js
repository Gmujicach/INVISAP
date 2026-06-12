document.addEventListener('DOMContentLoaded', () => {
  // ==========================================
  // 1. LÓGICA DE SECCIONES DINÁMICAS
  // ==========================================
  const tipoSolicitudSelect = document.getElementById('tipo_solicitud');
  const form = document.querySelector('form');

  // Referencias a los contenedores de cada sección
  const secciones = {
    'Comunidad': document.getElementById('seccion_comunidad'),
    'Institucion': document.getElementById('seccion_institucion'),
    'Particular': document.getElementById('seccion_particular')
  };

  /**
   * Muestra la sección seleccionada y oculta las demás.
   * Además, habilita/deshabilita los campos internos.
   */
  const toggleSecciones = () => {
    const seleccion = tipoSolicitudSelect.value;

    for (const [key, section] of Object.entries(secciones)) {
      if (key === seleccion) {
        section.style.display = 'block';
        // Habilitamos los inputs para que sean enviados y validados
        section.querySelectorAll('input, select, textarea').forEach(el => el.disabled = false);
      } else {
        section.style.display = 'none';
        // Deshabilitamos los inputs ocultos para que el navegador no exija su validación
        section.querySelectorAll('input, select, textarea').forEach(el => {
          el.disabled = true;
          removeError(el); // Limpiamos errores residuales si el usuario cambia de opinión
        });
      }
    }
  };

  // Escuchar cambios en el selector principal
  tipoSolicitudSelect.addEventListener('change', toggleSecciones);


  // ==========================================
  // 2. LÓGICA DE VALIDACIÓN DE FORMULARIO
  // ==========================================

  // Patrones de Expresiones Regulares
  const regexTexto = /^[a-zA-ZÁÉÍÓÚáéíóúÑñ\s]{3,50}$/; 
  const regexCedula = /^\d{7,10}$/; 
  const regexTelefono = /^\d{10,12}$/; // Permite formatos tipo 04141234567
  const regexCorreo = /^[^\s@ñÑ]+@[^\s@]+\.[^\s@]+$/;
  const regexRif = /^\d{8,9}$/; // 8 a 9 números para RIF

  /**
   * Muestra el error en la interfaz. Busca el contenedor correcto para inyectar el div.
   */
  const setError = (input, message) => {
    input.classList.add('is-invalid');
    
    // Buscamos el contenedor padre adecuado para colocar el mensaje
    let parent = input.closest('.col-md-12, .col-md-8, .col-md-6, .col-md-5, .col-md-4, .col-md-3');
    
    // Si no encuentra los anteriores, es porque es un caso especial o global
    if (!parent) parent = input.parentElement;

    let feedback = parent.querySelector('.invalid-feedback');
    
    // Si no existe, lo creamos
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

  /**
   * Remueve la clase de error de la interfaz.
   */
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

  // Asignar el evento 'input' a todos los campos para borrar errores en tiempo real
  form.querySelectorAll('input, select, textarea').forEach(input => {
    input.addEventListener('input', () => removeError(input));
    input.addEventListener('change', () => removeError(input));
  });

  // Interceptar el Submit
  form.addEventListener('submit', (e) => {
    let isValid = true;
    const tipo = tipoSolicitudSelect.value;

    // Validación del Selector Principal
    if (!tipo) {
      setError(tipoSolicitudSelect, 'Debe seleccionar un perfil.');
      isValid = false;
    }

    // --- Validaciones para "Comunidad" ---
    if (tipo === 'Comunidad') {
      const nombre = document.querySelector('input[name="com_nombre"]');
      const rif = document.querySelector('input[name="com_rif_numero"]');
      const muni = document.querySelector('select[name="com_municipio"]');
      const rep = document.querySelector('input[name="com_representante"]');
      const ced = document.querySelector('input[name="com_cedula"]');
      const tel = document.querySelector('input[name="com_telefono"]');
      const correo = document.querySelector('input[name="com_correo"]');

      if (nombre.value.trim().length < 3) { setError(nombre, 'Ingrese un nombre de comunidad válido.'); isValid = false; }
      if (!regexRif.test(rif.value.trim())) { setError(rif, 'El RIF debe tener 8 o 9 números.'); isValid = false; }
      if (!muni.value) { setError(muni, 'Seleccione un municipio.'); isValid = false; }
      if (!regexTexto.test(rep.value.trim())) { setError(rep, 'Nombre del representante inválido.'); isValid = false; }
      if (!regexCedula.test(ced.value.trim())) { setError(ced, 'La cédula debe tener entre 7 y 10 dígitos.'); isValid = false; }
      if (!regexTelefono.test(tel.value.trim())) { setError(tel, 'Teléfono inválido (10-12 dígitos numéricos).'); isValid = false; }
      if (!regexCorreo.test(correo.value.trim())) { setError(correo, 'Correo electrónico inválido.'); isValid = false; }
    }

    // --- Validaciones para "Institución" ---
    if (tipo === 'Institucion') {
      const nombre = document.querySelector('input[name="inst_nombre"]');
      const correo = document.querySelector('input[name="inst_correo"]');
      const tel = document.querySelector('input[name="inst_telefono"]');
      const dirNombre = document.querySelector('input[name="inst_director_nombre"]');
      const dirCed = document.querySelector('input[name="inst_director_cedula"]');

      if (nombre.value.trim().length < 3) { setError(nombre, 'Ingrese el nombre de la institución.'); isValid = false; }
      if (!regexCorreo.test(correo.value.trim())) { setError(correo, 'Correo electrónico inválido.'); isValid = false; }
      if (!regexTelefono.test(tel.value.trim())) { setError(tel, 'Teléfono inválido.'); isValid = false; }
      if (!regexTexto.test(dirNombre.value.trim())) { setError(dirNombre, 'Nombre del director inválido.'); isValid = false; }
      if (!regexCedula.test(dirCed.value.trim())) { setError(dirCed, 'Cédula inválida.'); isValid = false; }
    }

    // --- Validaciones para "Particular" ---
    if (tipo === 'Particular') {
      const nombre = document.querySelector('input[name="part_nombre"]');
      const ced = document.querySelector('input[name="part_cedula"]');
      const correo = document.querySelector('input[name="part_correo"]');
      const tel = document.querySelector('input[name="part_telefono"]');

      if (!regexTexto.test(nombre.value.trim())) { setError(nombre, 'El nombre debe contener solo letras.'); isValid = false; }
      if (!regexCedula.test(ced.value.trim())) { setError(ced, 'Cédula inválida (7 a 10 dígitos).'); isValid = false; }
      if (!regexCorreo.test(correo.value.trim())) { setError(correo, 'Correo electrónico inválido.'); isValid = false; }
      if (!regexTelefono.test(tel.value.trim())) { setError(tel, 'Teléfono inválido.'); isValid = false; }
    }

    // --- Validación Compartida: Problemática ---
    const problematica = document.querySelector('textarea[name="problematica"]');
    if (problematica.value.trim().length < 15) {
      setError(problematica, 'Por favor, describa la problemática con más detalle (mínimo 15 caracteres).');
      isValid = false;
    }

    // Prevenir el envío si hubo algún error
    if (!isValid) {
      e.preventDefault();
    }
  });
});