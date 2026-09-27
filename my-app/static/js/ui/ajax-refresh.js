/**
 * Utilidad global de refresco AJAX de listados.
 *
 * Objetivo: evitar recargas completas de pagina tras crear, editar o
 * eliminar registros. En lugar de `location.reload()`, se vuelve a pedir la
 * pagina actual al servidor, se extrae solo el <tbody> de la tabla
 * interesada y se reemplaza en el DOM.
 *
 * Uso tipico:
 *   INVISAP_AJAX.refrescarListadoActual('tablaEmpleados');
 *   INVISAP_AJAX.refrescarListadoActual('tablaEmpleados', { origen: 'empleados' });
 *   INVISAP_AJAX.refrescarListadoActual('tablaEmpleados', { url: '/empleados' });
 */
(function (global) {
  'use strict';

  const CABECERA_AJAX = { 'X-Requested-With': 'XMLHttpRequest' };

  const OPCIONES_POR_DEFECTO = {
    url: null,
    origen: null,
    esperaSilenciosa: false,
    alTerminar: null,
    alFallar: null
  };

  function opcionesValidas(opciones) {
    return Object.assign({}, OPCIONES_POR_DEFECTO, opciones || {});
  }

  function urlActual() {
    return global.location.pathname + global.location.search;
  }

  function esHtml(respuesta) {
    const tipo = respuesta.headers.get('Content-Type') || '';
    return tipo.indexOf('text/html') !== -1;
  }

  /**
   * Localiza el <tbody> de la tabla indicada dentro de un documento ya
   * parseado. Admite id CSS, nombre de tabla sin "#" o indice numerico.
   */
  function localizarTbody(doc, referencia) {
    if (referencia === undefined || referencia === null || referencia === '') {
      return null;
    }

    if (typeof referencia === 'number') {
      const tablas = doc.querySelectorAll('table');
      return tablas[referencia] ? tablas[referencia].querySelector('tbody') : null;
    }

    const selector = referencia.charAt(0) === '#' || referencia.indexOf('.') !== -1
      ? referencia
      : '#' + referencia;

    let tabla = null;
    try {
      tabla = doc.querySelector(selector);
    } catch (error) {
      tabla = null;
    }

    if (tabla) {
      return tabla.querySelector('tbody') || tabla;
    }

    // Respaldo: buscar por id en cualquier posicion del HTML.
    const id = referencia.replace(/^[#.]/, '');
    const porId = doc.getElementById(id);
    if (porId) {
      return porId.tagName === 'TBODY' ? porId : (porId.querySelector('tbody') || porId);
    }

    return null;
  }

  function actualizarContadores(doc, cuerpo) {
    if (!doc || !cuerpo) {
      return;
    }
    // DataTables no se usa en el proyecto, pero algunas vistas muestran
    // contadores "N registros" junto al titulo de la tabla.
    const textoAnterior = cuerpo.innerText || cuerpo.textContent || '';
    const filas = cuerpo.querySelectorAll('tr').length;
    if (filas === 0) {
      return;
    }
    const nuevoTexto = doc.body ? (doc.body.innerText || doc.body.textContent || '') : '';
    if (!nuevoTexto || nuevoTexto === textoAnterior) {
      return;
    }
    document.querySelectorAll('[data-contador-listado]').forEach(function (nodo) {
      const patron = new RegExp(nodo.getAttribute('data-contador-listado'), 'i');
      const coincidencia = nuevoTexto.match(patron);
      if (coincidencia) {
        nodo.textContent = coincidencia[0];
      }
    });
  }

  function trasReemplazar(cuerpo) {
    if (global.INVISAP_ESTANDAR_UI && typeof global.INVISAP_ESTANDAR_UI.aplicar === 'function') {
      global.INVISAP_ESTANDAR_UI.aplicar(cuerpo || document);
    } else {
      document.dispatchEvent(new CustomEvent('invisap:ajax-refrescado', {
        detail: { cuerpo: cuerpo || null }
      }));
    }
  }

  /**
   * Refresca el listado actual sin recargar la pagina.
   * @returns {Promise<boolean>} true si la tabla fue actualizada.
   */
  function refrescarListadoActual(referencia, opciones) {
    const cfg = opcionesValidas(opciones);
    const destino = urlActual();
    const origen = cfg.origen || 'listado';

    return refrescarListadoDesde(destino, referencia, cfg)
      .then(function (ok) {
        if (ok) {
          console.info('[INVISAP_AJAX] Listado "' + referencia + '" actualizado sin recargar (' + origen + ').');
        }
        if (typeof cfg.alTerminar === 'function') {
          cfg.alTerminar(ok);
        }
        return ok;
      })
      .catch(function (error) {
        console.error('[INVISAP_AJAX] No se pudo refrescar "' + referencia + '":', error);
        if (cfg.esperaSilenciosa && typeof cfg.alFallar !== 'function') {
          return false;
        }
        refrescoDeEmergencia(destino);
        if (typeof cfg.alFallar === 'function') {
          cfg.alFallar(error);
        }
        return false;
      });
  }

  /**
   * Si la tabla estaba inicializada con DataTables, se destruye la instancia
   * antes de reemplazar el contenido y se vuelve a inicializar despues.
   * La mayoria de los listados del proyecto son tablas simples, pero el
   * modulo de contrataciones usa DataTables.
   */
  function esDataTable(elemento) {
    return !!(window.jQuery && window.jQuery.fn && window.jQuery.fn.DataTable &&
      window.jQuery.fn.DataTable.isDataTable(elemento));
  }

  function destruirDataTable(elemento) {
    if (esDataTable(elemento)) {
      window.jQuery(elemento).DataTable().destroy();
      return true;
    }
    return false;
  }

  function reinicializarDataTable(elemento) {
    if (!elemento || !esDataTable(elemento)) return;
    const inicializador = global[elemento.id + 'DataTable'] ||
      global['inicializarTabla' + elemento.id] ||
      global['cargarTabla' + elemento.id];
    if (typeof inicializador === 'function') {
      inicializador();
    }
  }

  /**
   * Refresca un listado desde una URL concreta.
   */
  function refrescarListadoDesde(url, referencia, opciones) {
    const cfg = opcionesValidas(opciones);

    return fetch(url, {
      method: 'GET',
      headers: CABECERA_AJAX,
      credentials: 'same-origin'
    })
      .then(function (respuesta) {
        if (!respuesta.ok) {
          throw new Error('HTTP ' + respuesta.status);
        }
        if (!esHtml(respuesta)) {
          throw new Error('La respuesta no es HTML');
        }
        return respuesta.text();
      })
      .then(function (html) {
        const doc = new DOMParser().parseFromString(html, 'text/html');
        const cuerpoNuevo = localizarTbody(doc, referencia);
        const tablaActual = document.getElementById(String(referencia).replace(/^[#.]/, ''));

        if (!cuerpoNuevo || !tablaActual) {
          return false;
        }

        const cuerpoActual = tablaActual.tagName === 'TBODY'
          ? tablaActual
          : (tablaActual.querySelector('tbody') || tablaActual);

        const habiaDataTable = destruirDataTable(tablaActual);

        cuerpoActual.innerHTML = cuerpoNuevo.innerHTML;
        actualizarContadores(doc, cuerpoActual);
        trasReemplazar(cuerpoActual);

        if (habiaDataTable) {
          reinicializarDataTable(tablaActual);
        }
        return true;
      });
  }

  /** Ultimo recurso: recargar la pagina de forma controlada. */
  function refrescoDeEmergencia(url) {
    if (url && url !== urlActual()) {
      global.location.href = url;
    } else {
      global.location.reload();
    }
  }

  global.INVISAP_AJAX = {
    refrescarListadoActual: refrescarListadoActual,
    refrescarListadoDesde: refrescarListadoDesde,
    localizarTbody: localizarTbody
  };
})(window);
