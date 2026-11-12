/* =========================================================================
   GUÍA DEL SISTEMA — CONTROL DEL FAB Y SU PANEL DE ACCIONES
   -------------------------------------------------------------------------
   El FAB de la guía ya no inicia el tour directamente: despliega un panel
   anclado con celdas de acción. Este módulo se encarga de:

     · Abrir y cerrar el panel (aria-expanded en el FAB, aria-hidden en el panel).
     · Cerrar con Escape, clic fuera o al iniciar/detener el tour.
     · Navegar entre celdas con las flechas y devolver el foco al FAB.
     · Delegar en INVISAP_TOUR_MANAGER (startTour / stopTour).

   Requiere el markup `.tour-fab-menu#tourFabMenu` de `tour-fab.css`.
   ========================================================================= */
(function () {
  'use strict';

  var MENU_SELECTOR = '#tourFabMenu';

  function init() {
    var menu = document.querySelector(MENU_SELECTOR);
    if (!menu || menu.dataset.tourFabReady === 'true') return;

    var fab = menu.querySelector('.tour-fab');
    var panel = menu.querySelector('.tour-fab-panel');
    var tiles = Array.prototype.slice.call(menu.querySelectorAll('.tour-action-tile'));
    var startTile = menu.querySelector('[data-tour-action="start"]');
    var stopTile = menu.querySelector('[data-tour-action="stop"]');
    var tourModule = menu.getAttribute('data-tour-module') || undefined;

    menu.dataset.tourFabReady = 'true';

    function isOpen() {
      return menu.classList.contains('is-open');
    }

    function visibleTiles() {
      return tiles.filter(function (tile) {
        return tile.offsetParent !== null;
      });
    }

    // El panel mide una columna con una sola acción y dos cuando crece
    function updateColumns() {
      if (!panel) return;
      panel.classList.toggle('is-grid-2', visibleTiles().length > 1);
    }

    function open(focusFirst) {
      if (isOpen()) return;
      updateColumns();
      menu.classList.add('is-open');
      if (fab) fab.setAttribute('aria-expanded', 'true');
      if (panel) panel.setAttribute('aria-hidden', 'false');
      document.addEventListener('keydown', onDocumentKeydown);
      document.addEventListener('click', onDocumentClick, true);
      if (focusFirst) {
        var first = visibleTiles()[0];
        if (first) first.focus();
      }
    }

    function close(restoreFocus) {
      if (!isOpen()) return;
      menu.classList.remove('is-open');
      if (fab) fab.setAttribute('aria-expanded', 'false');
      if (panel) panel.setAttribute('aria-hidden', 'true');
      document.removeEventListener('keydown', onDocumentKeydown);
      document.removeEventListener('click', onDocumentClick, true);
      if (restoreFocus && fab) fab.focus();
    }

    function toggle(focusFirst) {
      if (isOpen()) close(false);
      else open(focusFirst);
    }

    function onDocumentClick(event) {
      if (menu.contains(event.target)) return;
      close(false);
    }

    function onDocumentKeydown(event) {
      if (event.key !== 'Escape') return;
      event.preventDefault();
      close(true);
    }

    function onFabClick(event) {
      event.preventDefault();
      event.stopPropagation();
      toggle(false);
    }

    function onFabKeydown(event) {
      if (event.key !== 'ArrowUp') return;
      event.preventDefault();
      open(true);
    }

    function onPanelKeydown(event) {
      var list = visibleTiles();
      if (!list.length) return;
      var index = list.indexOf(document.activeElement);
      var forward = event.key === 'ArrowDown' || event.key === 'ArrowRight';
      var backward = event.key === 'ArrowUp' || event.key === 'ArrowLeft';

      if (forward) {
        event.preventDefault();
        list[(index + 1 + list.length) % list.length].focus();
      } else if (backward) {
        event.preventDefault();
        list[(index - 1 + list.length) % list.length].focus();
      } else if (event.key === 'Tab' && index === list.length - 1) {
        event.preventDefault();
        close(true);
      }
    }

    function startTour() {
      var manager = window.INVISAP_TOUR_MANAGER;
      close(false);
      if (manager && typeof manager.startTour === 'function') {
        manager.startTour(tourModule);
        return;
      }
      if (typeof window.startModuleTour === 'function') window.startModuleTour();
    }

    function stopTour() {
      var manager = window.INVISAP_TOUR_MANAGER;
      close(false);
      if (manager && typeof manager.stopTour === 'function') {
        manager.stopTour();
        return;
      }
      if (typeof window.stopModuleTour === 'function') window.stopModuleTour();
    }

    if (fab) {
      fab.addEventListener('click', onFabClick);
      fab.addEventListener('keydown', onFabKeydown);
    }
    if (panel) panel.addEventListener('keydown', onPanelKeydown);
    if (startTile) startTile.addEventListener('click', startTour);
    if (stopTile) stopTile.addEventListener('click', stopTour);

    window.INVISAP_TOUR_FAB = {
      open: function () { open(false); },
      close: function () { close(false); },
      toggle: toggle,
      isOpen: isOpen,
      sync: function (active) {
        menu.classList.toggle('is-touring', !!active);
        updateColumns();
      }
    };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
