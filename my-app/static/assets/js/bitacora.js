(function () {
  'use strict';

  var DEBUG = false;

  function log() {
    if (DEBUG && console && console.log) {
      console.log.apply(console, arguments);
    }
  }

  var btnActualizar = document.getElementById('btnActualizar');
  var busquedaRapida = document.getElementById('buscarBitacora');
  var urlBase = '';

  if (window._bitacoraConfig && window._bitacoraConfig.ajaxUrl) {
    urlBase = window._bitacoraConfig.ajaxUrl.replace(/\/$/, '');
  }

  if (!urlBase) {
    urlBase = (window._bitacoraUrlBase || '').replace(/\/$/, '');
  }

  var debounceTimer = null;

  function serializeForm(formEl) {
    var data = new URLSearchParams();
    var elements = formEl.querySelectorAll('input[name], select[name]');
    elements.forEach(function (el) {
      if (el.name) {
        data.append(el.name, el.value || '');
      }
    });
    return data.toString();
  }

  function buildUrl(queryString) {
    if (!urlBase) {
      return '';
    }
    return urlBase + (queryString ? '?' + queryString : '');
  }

  function loadBitacora(queryString) {
    var url = buildUrl(queryString);
    if (!url) {
      log('[bitacora] URL base no configurada');
      return;
    }
    log('[bitacora] GET', url);

    fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then(function (response) {
        if (!response.ok) {
          return response.text().then(function (text) {
            throw new Error('Status: ' + response.status + ' | ' + text);
          });
        }
        return response.json();
      })
      .then(function (data) {
        if (!data || !data.html) {
          log('[bitacora] Respuesta sin HTML');
          return;
        }
        var contentWrapper = document.getElementById('bitacora-content');
        if (contentWrapper) {
          contentWrapper.innerHTML = data.html;
        }
        if (data.estadisticas) {
          actualizarEstadisticas(data.estadisticas, data.total_mostrados);
        }
      })
      .catch(function (error) {
        console.error('[bitacora] Error al cargar bitácora:', error);
      });
  }

  function actualizarEstadisticas(estadisticas, total_mostrados) {
    var contador = document.getElementById('registros-count');
    if (contador && typeof total_mostrados !== 'undefined') {
      contador.textContent = total_mostrados;
    }

    var statCrear = document.getElementById('stat-crear');
    var statEditar = document.getElementById('stat-editar');
    var statEliminar = document.getElementById('stat-eliminar');
    if (statCrear && typeof estadisticas.CREAR !== 'undefined') statCrear.textContent = estadisticas.CREAR;
    if (statEditar && typeof estadisticas.EDITAR !== 'undefined') statEditar.textContent = estadisticas.EDITAR;
    if (statEliminar && typeof estadisticas.ELIMINAR !== 'undefined') statEliminar.textContent = estadisticas.ELIMINAR;
  }

  function buscarRapidaLocal() {
    if (!busquedaRapida) return;
    var filtro = busquedaRapida.value.toLowerCase();
    var filas = document.querySelectorAll('#tabla-bitacora tbody tr');
    filas.forEach(function (fila) {
      fila.style.display = fila.textContent.toLowerCase().includes(filtro) ? '' : 'none';
    });
  }

  function LimpiarFormulario(formEl) {
    if (!formEl) return;
    var inputs = formEl.querySelectorAll('input[name], select[name]');
    inputs.forEach(function (el) {
      if (el.tagName === 'SELECT') {
        el.selectedIndex = 0;
      } else {
        el.value = '';
      }
    });
  }

  function init() {
    var contentWrapper = document.getElementById('bitacora-content');
    var formFiltros = document.getElementById('formFiltrosBitacora');

    if (contentWrapper) {
      contentWrapper.addEventListener('click', function (e) {
        var link = e.target.closest('.page-link');
        if (!link) return;
        e.preventDefault();
        var href = link.getAttribute('href');
        if (!href) return;
        var queryString = href.split('?')[1] || '';
        loadBitacora(queryString);
      });
    }

    if (formFiltros) {
      formFiltros.addEventListener('submit', function (e) {
        e.preventDefault();
        var queryString = serializeForm(formFiltros);
        loadBitacora(queryString);
      });

      var usuarioInput = formFiltros.querySelector('input[name="usuario"]');
      if (usuarioInput) {
        usuarioInput.addEventListener('input', function () {
          clearTimeout(debounceTimer);
          debounceTimer = setTimeout(function () {
            var queryString = serializeForm(formFiltros);
            loadBitacora(queryString);
          }, 400);
        });
      }

      [formFiltros.querySelector('select[name="modulo"]'), formFiltros.querySelector('select[name="accion"]')].forEach(function (selectEl) {
        if (!selectEl) return;
        selectEl.addEventListener('change', function () {
          var queryString = serializeForm(formFiltros);
          loadBitacora(queryString);
        });
      });
    }

    if (btnActualizar) {
      btnActualizar.addEventListener('click', function () {
        if (!formFiltros) return;
        var queryString = serializeForm(formFiltros);
        if (!queryString) {
          LimpiarFormulario(formFiltros);
          queryString = serializeForm(formFiltros);
        }
        loadBitacora(queryString);
      });
    }

    if (busquedaRapida) {
      busquedaRapida.addEventListener('keyup', buscarRapidaLocal);
    }

    log('[bitacora] inicializado');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
