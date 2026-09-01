/**
 * Validaciones en tiempo real (Frontend) para el módulo de Obras.
 * - Expresiones Regulares (Regex) espejo del backend.
 * - Mensajes de ayuda bajo cada input (color corporativo #cca025).
 * - Marca visual con Bootstrap (is-invalid / is-valid).
 * Ley de Hick: reducir carga cognitiva guiando al usuario mientras escribe.
 */

(function () {
  'use strict';

  const COLOR_INVILARA = '#cca025';

  const REGEX_OBRA = {
    titulo_obra: /^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s\.\,\-\#\/\(\)\:°º]{1,45}$/,
    ubicacion_obra: /^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s\.\,\-\#\/\(\)\:°º]{1,80}$/,
    periodo_ejecucion: /^[A-Za-z0-9\s]{1,10}$/,
    numero_contrato: /^[A-Za-z0-9\-\/\.\#\s]{1,20}$/,
    mediciones_obra: /^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s\.\,\-\#\/\(\)\:°º²]{1,45}$/,
    valuaciones: /^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s\.\,\-\#\/\(\)\:°ºBs\.]{1,100}$/,
    modificaciones_contrato: /^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s\.\,\-\#\/\(\)\:°º]{1,100}$/
  };

  const MENSAJES = {
    titulo_obra: 'Solo letras, números, espacios y los símbolos . , - # / ( ) : º. Máx. 45 caracteres.',
    ubicacion_obra: 'Solo letras, números, espacios y los símbolos . , - # / ( ) : º. Máx. 80 caracteres.',
    periodo_ejecucion: 'Solo letras, números y espacios. Máx. 10 caracteres (ej. "2 meses").',
    fecha_inicio: 'Seleccione una fecha válida (dd/mm/aaaa).',
    fecha_fin: 'Seleccione una fecha válida (dd/mm/aaaa). No puede ser anterior a la fecha de inicio.',
    mediciones_obra: 'Solo letras, números y símbolos . , - # / ( ) : º ². Máx. 45 caracteres.',
    valuaciones: 'Solo letras, números y símbolos . , - # / ( ) : º Bs. Máx. 100 caracteres.',
    modificaciones_contrato: 'Solo letras, números y símbolos . , - # / ( ) : º. Máx. 100 caracteres.',
    certificaciones_obras_ejecutadas: 'Número entero mayor o igual a 0.',
    porcentaje_avance_obra: 'Número entero entre 0 y 100.',
    numero_contrato: 'Solo letras, números y los símbolos - / . #. Máx. 20 caracteres.',
    contratacion_id_contratacion: 'Debe seleccionar una contratación válida.',
    gestionar_proyectos_codigo_proyecto: 'Debe seleccionar un proyecto válido.'
  };

  function getOrCreateHelp(input) {
    let help = input.parentElement.querySelector('.invalid-feedback-js');
    if (!help) {
      help = document.createElement('span');
      help.className = 'invalid-feedback invalid-feedback-js';
      help.style.display = 'none';
      help.style.color = '#dc3545';
      help.style.fontSize = '0.8rem';
      help.style.marginTop = '0.25rem';
      input.parentElement.appendChild(help);
    }
    return help;
  }

  function getOrCreateHint(input) {
    let hint = input.parentElement.querySelector('.form-hint-invilara');
    if (!hint) {
      hint = document.createElement('small');
      hint.className = 'form-hint-invilara d-block mt-1';
      hint.style.color = COLOR_INVILARA;
      hint.style.fontWeight = '500';
      hint.style.fontSize = '0.78rem';
      input.parentElement.appendChild(hint);
    }
    return hint;
  }

  function validarCampoTexto(input) {
    const nombre = input.name;
    const regex = REGEX_OBRA[nombre];
    const help = getOrCreateHelp(input);
    const valor = (input.value || '').trim();

    if (!valor) {
      input.classList.remove('is-valid', 'is-invalid');
      help.style.display = 'none';
      help.textContent = '';
      return true;
    }

    if (regex && !regex.test(valor)) {
      input.classList.add('is-invalid');
      input.classList.remove('is-valid');
      help.textContent = MENSAJES[nombre] || 'Formato inválido.';
      help.style.display = 'block';
      return false;
    }

    input.classList.remove('is-invalid');
    input.classList.add('is-valid');
    help.style.display = 'none';
    help.textContent = '';
    return true;
  }

  function validarNumeroEntero(input) {
    const nombre = input.name;
    const help = getOrCreateHelp(input);
    const valor = (input.value || '').trim();

    if (!valor) {
      input.classList.remove('is-valid', 'is-invalid');
      help.style.display = 'none';
      return true;
    }

    const num = Number(valor);
    let ok = Number.isInteger(num);

    if (ok && nombre === 'porcentaje_avance_obra') {
      ok = num >= 0 && num <= 100;
    } else if (ok && nombre === 'certificaciones_obras_ejecutadas') {
      ok = num >= 0;
    }

    if (!ok) {
      input.classList.add('is-invalid');
      input.classList.remove('is-valid');
      help.textContent = MENSAJES[nombre] || 'Número inválido.';
      help.style.display = 'block';
      return false;
    }

    input.classList.remove('is-invalid');
    input.classList.add('is-valid');
    help.style.display = 'none';
    return true;
  }

  function validarFecha(input, otroInput) {
    const help = getOrCreateHelp(input);
    const valor = input.value;

    if (!valor) {
      input.classList.remove('is-valid', 'is-invalid');
      help.style.display = 'none';
      return true;
    }

    const fecha = new Date(valor);
    if (isNaN(fecha.getTime())) {
      input.classList.add('is-invalid');
      input.classList.remove('is-valid');
      help.textContent = MENSAJES[input.name] || 'Fecha inválida.';
      help.style.display = 'block';
      return false;
    }

    if (otroInput && otroInput.value) {
      const otra = new Date(otroInput.value);
      if (!isNaN(otra.getTime()) && input.name === 'fecha_fin' && fecha < otra) {
        input.classList.add('is-invalid');
        input.classList.remove('is-valid');
        help.textContent = MENSAJES.fecha_fin;
        help.style.display = 'block';
        return false;
      }
    }

    input.classList.remove('is-invalid');
    input.classList.add('is-valid');
    help.style.display = 'none';
    return true;
  }

  function validarSelectAsync(input) {
    const help = getOrCreateHelp(input);
    const valor = (input.value || '').trim();

    if (!valor || valor === '0') {
      input.classList.remove('is-valid');
      input.classList.add('is-invalid');
      help.textContent = MENSAJES[input.name] || 'Debe seleccionar una opción.';
      help.style.display = 'block';
      return Promise.resolve(false);
    }

    return fetch(`/api/obra/validar-${input.name === 'contratacion_id_contratacion' ? 'contratacion' : 'proyecto'}?id=${encodeURIComponent(valor)}`)
      .then(r => r.json())
      .then(data => {
        if (data && data.valido) {
          input.classList.remove('is-invalid');
          input.classList.add('is-valid');
          help.style.display = 'none';
          return true;
        }
        input.classList.add('is-invalid');
        input.classList.remove('is-valid');
        help.textContent = data.mensaje || MENSAJES[input.name];
        help.style.display = 'block';
        return false;
      })
      .catch(() => {
        input.classList.add('is-invalid');
        help.textContent = 'No se pudo verificar la selección. Intente nuevamente.';
        help.style.display = 'block';
        return false;
      });
  }

  function initFormularioObra(formId) {
    const form = document.getElementById(formId);
    if (!form) return;

    const inputsTexto = ['titulo_obra', 'ubicacion_obra', 'periodo_ejecucion', 'numero_contrato',
                          'mediciones_obra', 'valuaciones', 'modificaciones_contrato'];

    inputsTexto.forEach(nombre => {
      const input = form.querySelector(`[name="${nombre}"]`);
      if (!input) return;
      const hint = getOrCreateHint(input);
      hint.textContent = input.placeholder
        ? `Ej. ${input.placeholder.replace(/^Ej\.\s*/i, '')}`
        : 'Ingrese un valor válido.';
      input.addEventListener('input', () => validarCampoTexto(input));
      input.addEventListener('blur', () => validarCampoTexto(input));
    });

    const inputsNumero = ['certificaciones_obras_ejecutadas', 'porcentaje_avance_obra'];
    inputsNumero.forEach(nombre => {
      const input = form.querySelector(`[name="${nombre}"]`);
      if (!input) return;
      const hint = getOrCreateHint(input);
      hint.textContent = nombre === 'porcentaje_avance_obra'
        ? 'Debe ser un número entero entre 0 y 100.'
        : 'Debe ser un número entero mayor o igual a 0.';
      input.addEventListener('input', () => validarNumeroEntero(input));
      input.addEventListener('blur', () => validarNumeroEntero(input));
    });

    const fechaInicio = form.querySelector('[name="fecha_inicio"]');
    const fechaFin = form.querySelector('[name="fecha_fin"]');
    if (fechaInicio) {
      const hint = getOrCreateHint(fechaInicio);
      hint.textContent = 'Formato: dd/mm/aaaa. Debe ser anterior a la fecha de fin.';
      fechaInicio.addEventListener('change', () => {
        validarFecha(fechaInicio, fechaFin);
        if (fechaFin) validarFecha(fechaFin, fechaInicio);
      });
    }
    if (fechaFin) {
      const hint = getOrCreateHint(fechaFin);
      hint.textContent = 'Formato: dd/mm/aaaa. No puede ser anterior a la fecha de inicio.';
      fechaFin.addEventListener('change', () => {
        validarFecha(fechaFin, fechaInicio);
        if (fechaInicio) validarFecha(fechaInicio, fechaFin);
      });
    }

    const selects = form.querySelectorAll('select');
    selects.forEach(sel => {
      const hint = getOrCreateHint(sel);
      hint.textContent = MENSAJES[sel.name] || 'Seleccione una opción válida.';
      sel.addEventListener('change', () => validarSelectAsync(sel));
    });
  }

  window.ValidacionesObra = {
    init: initFormularioObra,
    validarCampoTexto,
    validarNumeroEntero,
    validarFecha,
    validarSelectAsync
  };
})();