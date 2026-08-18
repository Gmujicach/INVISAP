/**
 * Validaciones comunes para formularios del sistema INVILARA / INVISAP
 * Autor: Kilo - Sistema INVILARA
 */

(function () {
  'use strict';

  const VALIDACIONES = {
    /**
     * Inicializa validaciones de selects en un formulario.
     * Marca con borde rojo los selects que tienen la opción por defecto vacía.
     * @param {HTMLFormElement} form
     * @param {Object} [opts]
     * @param {string} [opts.selector='select'] - Selector de selects a validar.
     * @param {string} [opts.claseError='is-invalid'] - Clase para marcar error.
     * @param {string} [opts.claseOk='is-valid'] - Clase para marcar válido.
     * @param {boolean} [opts.validarAlCambio=true] - Si debe validar en change.
     * @param {boolean} [opts.validarAlEnviar=true] - Si debe validar en submit.
     */
    initSelects: function (form, opts) {
      if (!form) return;
      const config = Object.assign(
        {
          selector: 'select',
          claseError: 'is-invalid',
          claseOk: 'is-valid',
          validarAlCambio: true,
          validarAlEnviar: true,
        },
        opts
      );

      const selects = Array.from(form.querySelectorAll(config.selector));

      const validarSelect = function (select) {
        if (!select || select.disabled) return true;
        const val = (select.value || '').trim();
        const invalido = val === '' || val === '0' || select.options[0]?.text === 'Seleccione...';
        const padre = select.closest('.col-md-6, .col-md-4, .col-md-3, .col-12, .mb-3, .row, [class*="col-"]');
        if (invalido) {
          select.classList.add(config.claseError);
          select.classList.remove(config.claseOk);
        } else {
          select.classList.remove(config.claseError);
          select.classList.add(config.claseOk);
        }
        return !invalido;
      };

      selects.forEach(function (select) {
        if (config.validarAlCambio) {
          select.addEventListener('change', function () {
            validarSelect(select);
          });
        }
        validarSelect(select);
      });

      if (config.validarAlEnviar) {
        form.addEventListener('submit', function () {
          selects.forEach(function (select) {
            validarSelect(select);
          });
        });
      }
    },

    /**
     * Inicializa validaciones de botones de submit en un formulario.
     * Deshabilita el botón durante el envío para evitar doble clic.
     * @param {HTMLFormElement} form
     * @param {Object} [opts]
     * @param {string} [opts.selector='button[type="submit"]'] - Botón a controlar.
     * @param {string} [opts.textoGuardando='Guardando...'] - Texto mientras envía.
     * @param {string} [opts.textoOriginal] - Si se provee, restaura este texto al finalizar.
     */
    initBotonesSubmit: function (form, opts) {
      if (!form) return;
      const config = Object.assign(
        {
          selector: 'button[type="submit"]',
          textoGuardando: 'Guardando...',
        },
        opts
      );

      const boton = form.querySelector(config.selector);
      if (!boton) return;

      const textoOriginal = config.textoOriginal || boton.innerHTML;

      form.addEventListener('submit', function () {
        boton.disabled = true;
        boton.innerHTML =
          '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>' +
          config.textoGuardando;
      });

      const restaurarBoton = function () {
        boton.disabled = false;
        boton.innerHTML = textoOriginal;
      };

      form.addEventListener('reset', restaurarBoton);

      if (form.tagName === 'FORM') {
        form._restaurarBoton = restaurarBoton;
      }
    },

    /**
     * Inicializa validación genérica de formulario con Bootstrap was-validated.
     * @param {HTMLFormElement} form
     * @param {Function} [onValid] - Callback al ser válido.
     * @param {Function} [onInvalid] - Callback al ser inválido.
     */
    initFormularioBootstrap: function (form, onValid, onInvalid) {
      if (!form) return;
      form.addEventListener('submit', function (event) {
        if (form.checkValidity()) {
          event.preventDefault();
          if (typeof onValid === 'function') onValid(form);
        } else {
          event.preventDefault();
          event.stopPropagation();
          form.classList.add('was-validated');
          if (typeof onInvalid === 'function') onInvalid(form);
        }
      });
    },

    /**
     * Marca todos los selects vacíos de un formulario con clase de error.
     * @param {HTMLFormElement} form
     * @param {Object} [opts]
     * @returns {boolean} true si todos los selects tienen valor.
     */
    validarSelectsVacios: function (form, opts) {
      if (!form) return false;
      const config = Object.assign(
        {
          selector: 'select',
          claseError: 'is-invalid',
          mensaje: 'Debe seleccionar una opción válida en todos los campos desplegables.',
        },
        opts
      );

      const selects = Array.from(form.querySelectorAll(config.selector));
      let hayVacios = false;

      selects.forEach(function (select) {
        if (select.disabled) return;
        const val = (select.value || '').trim();
        if (val === '' || val === '0') {
          select.classList.add(config.claseError);
          hayVacios = true;
        } else {
          select.classList.remove(config.claseError);
        }
      });

      return !hayVacios;
    },

    /**
     * Inicializa listeners comunes en formularios con fetch/AJAX.
     * @param {HTMLFormElement} form
     * @param {Object} [opts]
     * @param {string} [opts.url] - URL del endpoint.
     * @param {string} [opts.metodo='POST'] - Método HTTP.
     * @param {Function} [opts.antesDeEnviar] - Hook antes del fetch.
     * @param {Function} [opts.alExito] - Callback éxito.
     * @param {Function} [opts.alError] - Callback error.
     * @param {boolean} [opts.validarSelects=true] - Si valida selects vacíos.
     * @param {boolean} [opts.validarHTML5=true] - Si aplica validación HTML5.
     */
    initFormularioFetch: function (form, opts) {
      if (!form) return;
      const config = Object.assign(
        {
          metodo: 'POST',
          validarSelects: true,
          validarHTML5: true,
        },
        opts
      );

      form.addEventListener('submit', function (event) {
        event.preventDefault();

        if (config.validarHTML5 && !form.checkValidity()) {
          form.classList.add('was-validated');
          const primerInvalido = form.querySelector(':invalid');
          if (primerInvalido) primerInvalido.focus();
          if (typeof config.alError === 'function') {
            config.alError(new Error('Complete los campos requeridos correctamente.'));
          }
          return;
        }

        if (config.validarSelects && !VALIDACIONES.validarSelectsVacios(form)) {
          const primerSelect = form.querySelector('select.is-invalid');
          if (primerSelect) primerSelect.focus();
          if (typeof config.alError === 'function') {
            config.alError(new Error('Debe seleccionar una opción en todos los campos desplegables.'));
          }
          return;
        }

        if (typeof config.antesDeEnviar === 'function') {
          config.antesDeEnviar(form);
        }

        const boton = form.querySelector('button[type="submit"]');
        const textoOriginal = boton ? boton.innerHTML : '';
        if (boton) {
          boton.disabled = true;
          boton.innerHTML =
            '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Guardando...';
        }

        const formData = new FormData(form);
        const url = config.url || form.action;

        fetch(url, {
          method: config.metodo,
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
          },
        })
          .then(function (response) {
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
              return response.text().then(function () {
                throw new Error('Respuesta inesperada del servidor.');
              });
            }
            if (!response.ok) {
              return response.json().then(function (data) {
                throw new Error(data.message || 'Error en el servidor');
              });
            }
            return response.json();
          })
          .then(function (data) {
            if (typeof config.alExito === 'function') {
              config.alExito(data, form);
            }
          })
          .catch(function (error) {
            console.error('Error en formulario fetch:', error);
            if (typeof config.alError === 'function') {
              config.alError(error);
            }
          })
          .finally(function () {
            if (boton) {
              boton.disabled = false;
              boton.innerHTML = textoOriginal;
            }
          });
      });
    },

    /**
     * Marca un select como inválido si su valor es vacío.
     * @param {HTMLSelectElement} select
     * @param {Object} [opts]
     */
    marcarSelectInvalido: function (select, opts) {
      if (!select) return;
      const config = Object.assign(
        {
          claseError: 'is-invalid',
          claseOk: 'is-valid',
        },
        opts
      );
      const val = (select.value || '').trim();
      if (val === '' || val === '0') {
        select.classList.add(config.claseError);
        select.classList.remove(config.claseOk);
      } else {
        select.classList.remove(config.claseError);
        select.classList.add(config.claseOk);
      }
    },
  };

  window.ValidacionesComunes = VALIDACIONES;
})();
