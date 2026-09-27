/* =========================================================================
   ESTANDAR-UI — INVISAP
   -------------------------------------------------------------------------
   Normalizador global de interfaz. Se carga en `base_cpanel.html` y en
   `base_login.html` para garantizar que TODO el sistema comparta el mismo
   estándar visual, sin importar el módulo:

     · Botones de acción (Ver / Editar / Eliminar) de todas las tablas
       → idénticos al Módulo de Listar Solicitudes (tamaño, posición,
         color e iconografía).
     · Botón de cierre (equis) de todos los modales
       → siempre `bi-x-lg` con el mismo tamaño y comportamiento.

   Funciona también con contenido inyectado por AJAX mediante un
   MutationObserver, de modo que las listas recargadas sin refrescar la
   página también quedan estandarizadas.
   ========================================================================= */
(function () {
  'use strict';

  if (window.INVISAP_ESTANDAR_UI) return;
  window.INVISAP_ESTANDAR_UI = { applied: false };

  /* -------------------------------------------------------------------
     1. Catálogo de acciones: clase heredada → { clase, icono, etiqueta }
     ------------------------------------------------------------------- */
  var CATALOGO = [
    { nuevas: ['btn-ver-informe'],            clase: 'btn-accion-detalle',  icono: 'bi-search',              etiqueta: 'Ver informe' },
    { nuevas: ['btn-editar-informe'],         clase: 'btn-accion-editar',   icono: 'bi-pencil-square',       etiqueta: 'Editar informe' },
    { nuevas: ['btn-eliminar-informe'],       clase: 'btn-accion-eliminar',  icono: 'bi-trash',               etiqueta: 'Eliminar informe' },
    { nuevas: ['btn-ver-detalle', 'btn-detalle'], clase: 'btn-accion-detalle', icono: 'bi-eye',                 etiqueta: 'Ver detalle' },
    { nuevas: ['btn-ver'],                    clase: 'btn-accion-ver',      icono: 'bi-eye',                 etiqueta: 'Ver' },
    { nuevas: ['btn-editar'],                 clase: 'btn-accion-editar',   icono: 'bi-pencil-square',       etiqueta: 'Editar' },
    { nuevas: ['btn-eliminar'],               clase: 'btn-accion-eliminar',  icono: 'bi-trash',               etiqueta: 'Eliminar' },
    { nuevas: ['btn-descargar', 'btn-download'], clase: 'btn-accion-descargar', icono: 'bi-download',          etiqueta: 'Descargar' },
    { nuevas: ['btn-aprobar'],                clase: 'btn-accion-aprobar',  icono: 'bi-check2-circle',      etiqueta: 'Aprobar' },
    { nuevas: ['btn-restaurar', 'btn-refrescar'], clase: 'btn-accion-neutro', icono: 'bi-arrow-clockwise',   etiqueta: 'Restaurar' }
  ];

  /* Colores Bootstrap que también representan una acción de tabla */
  var CLASES_COLOR = {
    'btn-outline-info': 'btn-accion-ver',
    'btn-info': 'btn-accion-ver',
    'btn-outline-warning': 'btn-accion-editar',
    'btn-warning': 'btn-accion-editar',
    'btn-outline-danger': 'btn-accion-eliminar',
    'btn-danger': 'btn-accion-eliminar',
    'btn-outline-success': 'btn-accion-detalle',
    'btn-success': 'btn-accion-detalle'
  };

  var REGISTRO = [];
  REGISTRO.push.apply(REGISTRO, CATALOGO);
  REGISTRO.forEach(function (item) {
    item.clases = item.nuevas;
  });

  /* -------------------------------------------------------------------
     2. Utilidades
     ------------------------------------------------------------------- */
  function tieneAlgunaClase(el, lista) {
    for (var i = 0; i < lista.length; i++) {
      if (el.classList.contains(lista[i])) return true;
    }
    return false;
  }

  function resolverAccion(el) {
    if (el.classList.contains('btn-accion')) return null;
    for (var i = 0; i < REGISTRO.length; i++) {
      if (tieneAlgunaClase(el, REGISTRO[i].clases)) return REGISTRO[i];
    }
    var colores = Object.keys(CLASES_COLOR);
    for (var j = 0; j < colores.length; j++) {
      if (el.classList.contains(colores[j])) {
        return { clase: CLASES_COLOR[colores[j]], icono: null, etiqueta: null };
      }
    }
    return null;
  }

  function iconoActual(el) {
    var i = el.querySelector('i.bi');
    return i ? (i.className || '') : null;
  }

  function esCeldaDeAccion(celda) {
    if (!celda) return false;
    if (celda.classList.contains('acciones')) return true;
    if (!celda.parentElement) return false;
    var th = celda.parentElement.querySelector('th');
    if (!th) return false;
    var texto = (th.textContent || '').trim().toLowerCase();
    return texto.indexOf('acci') !== -1 || texto === 'op' || texto === 'opciones';
  }

  /* -------------------------------------------------------------------
     3. Normalización de los botones de acción de las tablas
     ------------------------------------------------------------------- */
  function normalizarAcciones(raiz) {
    var alcance = (raiz && raiz.querySelectorAll)
      ? raiz.querySelectorAll('table tbody td a.btn, table tbody td button.btn, table tbody td a[class*="btn-"], table tbody td button[class*="btn-"]')
      : [];

    Array.prototype.forEach.call(alcance, function (el) {
      if (el.classList.contains('btn-close') || el.classList.contains('btn-close-custom')) return;
      if (el.closest('.modal-footer')) return;
      if (el.closest('.dataTables_paginate')) return;

      var accion = resolverAccion(el);
      if (!accion) return;

      var celda = el.closest('td');
      if (!esCeldaDeAccion(celda)) return;

      /* Se conservan las clases funcionales que usa el JS de cada módulo */
      var conservadas = [];
      Array.prototype.forEach.call(el.classList, function (c) {
        if (c === 'btn' || c === 'btn-sm' || c === 'btn-lg' || c === 'rounded-circle') return;
        if (c.indexOf('btn-outline-') === 0) return;
        if (c === 'btn-info' || c === 'btn-warning' || c === 'btn-danger' ||
            c === 'btn-success' || c === 'btn-secondary' || c === 'btn-primary') return;
        if (REGISTRO.some(function (r) { return r.clases.indexOf(c) !== -1; })) return;
        if (c.indexOf('btn-accion') === 0) return;
        if (['ms-1', 'me-1', 'm-1', 'mx-1', 'p-0', 'shadow-sm', 'shadow', 'text-white'].indexOf(c) !== -1) return;
        conservadas.push(c);
      });

      el.className = ['btn', 'btn-sm', 'btn-accion', accion.clase].concat(conservadas).join(' ');
      el.setAttribute('role', 'button');

      if (accion.etiqueta && !el.getAttribute('title')) {
        el.setAttribute('title', accion.etiqueta);
        el.setAttribute('aria-label', accion.etiqueta);
      }

      /* Iconografía canónica */
      var actual = iconoActual(el);
      var canonico = 'bi ' + accion.icono;
      if (actual && canonico && actual.indexOf(canonico) === -1) {
        var i = el.querySelector('i.bi');
        if (i) {
          i.className = canonico;
        } else {
          i = document.createElement('i');
          i.className = canonico;
          el.innerHTML = '';
          el.appendChild(i);
        }
      } else if (!actual && accion.icono) {
        var nuevo = document.createElement('i');
        nuevo.className = canonico;
        el.appendChild(nuevo);
      }
    });

    /* Contenedor de acciones alineado */
    var celdas = (raiz && raiz.querySelectorAll) ? raiz.querySelectorAll('table tbody td') : [];
    Array.prototype.forEach.call(celdas, function (td) {
      if (!esCeldaDeAccion(td)) return;
      if (!td.querySelector('.btn-accion')) return;
      td.classList.add('acciones');
      var contenedor = td.querySelector('.btn-acciones');
      if (!contenedor) {
        contenedor = document.createElement('div');
        contenedor.className = 'btn-acciones';
        while (td.firstChild) contenedor.appendChild(td.firstChild);
        td.appendChild(contenedor);
      }
    });
  }

  /* -------------------------------------------------------------------
     4. Normalización de la equis de todos los modales
     ------------------------------------------------------------------- */
  function encabezadoConColor(header) {
    if (!header) return true;
    var style = header.getAttribute('style') || '';
    if (style.indexOf('background') !== -1) return true;
    return /(^|\s)bg-[a-z-]+(\s|$)/.test(header.className || '');
  }

  function normalizarModales(raiz) {
    var alcances = [
      'button[data-bs-dismiss="modal"][class*="close"]',
      'button[data-bs-dismiss="modal"].btn-close',
      'button[data-bs-dismiss="modal"].btn.btn-outline-light',
      'button[data-bs-dismiss="modal"].btn.btn-outline-dark',
      'button[data-bs-dismiss="modal"].modal-close-btn',
      'button[data-bs-dismiss="modal"].publication-modal-close',
      'button[data-bs-dismiss="modal"].btn-close-detalle'
    ].join(', ');

    var elementos = (raiz && raiz.querySelectorAll) ? raiz.querySelectorAll(alcances) : [];

    Array.prototype.forEach.call(elementos, function (btn) {
      if (btn.closest('.modal-footer')) return;
      if (btn.classList.contains('modal-close-float')) return;
      if (btn.classList.contains('btn-close-custom')) return;

      var modal = btn.closest('.modal');
      var header = btn.closest('.modal-header');
      var conColor = encabezadoConColor(header) || (!modal && true);

      /* Se conservan identificadores y manejadores de evento */
      var id = btn.getAttribute('id');
      var dataTarget = btn.getAttribute('data-bs-target');
      var eventos = Array.prototype.slice.call(btn.attributes).map(function (a) {
        return a.name;
      });

      var nuevo = document.createElement('button');
      nuevo.type = 'button';
      nuevo.className = 'btn-close-custom' + (conColor ? '' : ' btn-close-dark');
      nuevo.setAttribute('data-bs-dismiss', 'modal');
      nuevo.setAttribute('aria-label', 'Cerrar');

      eventos.forEach(function (nombre) {
        if (['type', 'class', 'data-bs-dismiss', 'aria-label', 'style'].indexOf(nombre) !== -1) return;
        nuevo.setAttribute(nombre, btn.getAttribute(nombre));
      });
      if (id) nuevo.setAttribute('id', id);
      if (dataTarget) nuevo.setAttribute('data-bs-target', dataTarget);

      var icono = document.createElement('i');
      icono.className = 'bi bi-x-lg';
      icono.setAttribute('aria-hidden', 'true');
      nuevo.appendChild(icono);

      btn.parentNode.replaceChild(nuevo, btn);
    });
  }

  /* -------------------------------------------------------------------
     5. Observador de contenido dinámico (AJAX / modales)
     -------------------------------------------------------------------
     IMPORTANTE (rendimiento): al abrir o cerrar un modal, Bootstrap
     inserta y elimina el `.modal-backdrop` y alterna clases, lo que dispara
     este observador. Si en cada mutacion se re-normalizara el documento
     entero, los modales tardarian en aparecer en paginas grandes (la
     bitacora, por ejemplo, supera los 400 KB de HTML).

     Por eso aqui se normaliza SOLO el subarbol que acaba de cambiar, y se
     descartan por completo las mutaciones caused por Bootstrap, los toasts
     y el propio normalizador. */
  var pendiente = null;
  var observador = null;
  var normalizando = false;

  var IGNORAR_SELECTOR = [
    '.modal-backdrop',
    '.offcanvas-backdrop',
    '.modal-open',
    '.toast-custom',
    '.spinner-border',
    '[aria-busy="true"]'
  ].join(', ');

  function esIgnorable(nodo) {
    if (!nodo || nodo.nodeType !== 1) return true;
    if (nodo.tagName === 'SCRIPT' || nodo.tagName === 'STYLE' || nodo.tagName === 'LINK') return true;
    try {
      if (nodo.matches && nodo.matches(IGNORAR_SELECTOR)) return true;
    } catch (e) {
      /* selector no soportado: se sigue adelante */
    }
    return false;
  }

  /** Normaliza solo las raices anadidas, nunca todo el documento. */
  function normalizarRaices(raices) {
    if (normalizando) return;
    normalizando = true;
    try {
      for (var i = 0; i < raices.length; i++) {
        var raiz = raices[i];
        if (esIgnorable(raiz)) continue;
        /* Si el nodo anadido es un <tbody> se procesa el <table> padre,
           porque la busqueda de acciones arranca en `table tbody td`. */
        if (raiz.tagName === 'TBODY' && raiz.parentNode) {
          raiz = raiz.parentNode;
        }
        normalizarAcciones(raiz);
        normalizarModales(raiz);
      }
    } catch (e) {
      if (window.console) console.warn('[EstandarUI]', e);
    } finally {
      normalizando = false;
    }
  }

  function programar(raices) {
    var utiles = [];
    for (var i = 0; i < raices.length; i++) {
      if (!esIgnorable(raices[i])) utiles.push(raices[i]);
    }
    if (!utiles.length) return;

    if (!pendiente) {
      pendiente = { raices: [] };
      window.setTimeout(function () {
        var acumulado = pendiente.raices;
        pendiente = null;
        normalizarRaices(acumulado);
      }, 0);
    }
    for (var j = 0; j < utiles.length; j++) {
      pendiente.raices.push(utiles[j]);
    }
  }

  function observar() {
    if (observador || !window.MutationObserver) return;
    observador = new MutationObserver(function (mutaciones) {
      if (normalizando) return;

      var raices = [];
      for (var i = 0; i < mutaciones.length; i++) {
        var agregados = mutaciones[i].addedNodes;
        for (var j = 0; j < agregados.length; j++) {
          if (agregados[j].nodeType === 1) raices.push(agregados[j]);
        }
      }
      if (raices.length) programar(raices);
    });
    observador.observe(document.body, { childList: true, subtree: true });
  }

  /* -------------------------------------------------------------------
     6. API pública
     ------------------------------------------------------------------- */
  window.INVISAP_ESTANDAR_UI.aplicar = function (raiz) {
    if (!raiz) {
      try {
        normalizando = true;
        normalizarAcciones(document);
        normalizarModales(document);
        window.INVISAP_ESTANDAR_UI.applied = true;
      } catch (e) {
        if (window.console) console.warn('[EstandarUI]', e);
      } finally {
        normalizando = false;
      }
      return;
    }
    normalizarRaices([raiz]);
  };

  function iniciar() {
    window.INVISAP_ESTANDAR_UI.aplicar();
    observar();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciar);
  } else {
    iniciar();
  }
})();
