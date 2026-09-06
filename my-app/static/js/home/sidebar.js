document.addEventListener('DOMContentLoaded', function () {
  'use strict';

  const sidebar = document.getElementById('layout-menu');
  const btnToggle = document.getElementById('sidebarToggleBtn');
  const iconoCerrar = document.getElementById('icono-cerrar');
  const iconoAbrir = document.getElementById('icono-abrir');

  if (!sidebar || !btnToggle) return;

  function getStorageKey() {
    return 'invilara-sidebar-collapsed';
  }

  function readStoredState() {
    try {
      const raw = localStorage.getItem(getStorageKey());
      return raw === 'true' ? true : raw === 'false' ? false : null;
    } catch (e) {
      return null;
    }
  }

  function writeStoredState(collapsed) {
    try {
      localStorage.setItem(getStorageKey(), String(collapsed));
    } catch (e) {
      // ignore storage errors
    }
  }

  function isCollapsed() {
    const rootCollapsed = document.documentElement.classList.contains('layout-menu-collapsed');
    const sidebarCollapsed = sidebar.classList.contains('menu-collapsed');
    return rootCollapsed || sidebarCollapsed;
  }

  function setCollapsed(collapsed) {
    document.documentElement.classList.toggle('layout-menu-collapsed', collapsed);
    sidebar.classList.toggle('menu-collapsed', collapsed);
    sidebar.classList.toggle('layout-menu-expanded', !collapsed);
    setTimeout(function () {
      window.dispatchEvent(new Event('resize'));
    }, 30);
  }

  function syncIconState() {
    const collapsed = isCollapsed();

    if (btnToggle) {
      btnToggle.setAttribute('aria-expanded', String(!collapsed));
    }

    if (iconoCerrar) {
      iconoCerrar.style.display = collapsed ? 'none' : 'inline-flex';
    }

    if (iconoAbrir) {
      iconoAbrir.style.display = collapsed ? 'inline-flex' : 'none';
    }
  }

  function toggleMenu(e) {
    if (e) e.preventDefault();

    const nextState = !isCollapsed();

    if (window.Helpers && typeof window.Helpers.toggleCollapsed === 'function') {
      window.Helpers.toggleCollapsed();
    } else {
      setCollapsed(nextState);
    }

    writeStoredState(nextState);
    requestAnimationFrame(syncIconState);
    setTimeout(syncIconState, 50);
    setTimeout(syncIconState, 150);
  }

  function initMenuToggleItems() {
    const toggles = sidebar.querySelectorAll('.menu-toggle');
    toggles.forEach(function (item) {
      item.addEventListener('click', function (e) {
        if (isCollapsed()) {
          e.preventDefault();
          e.stopPropagation();
          const target = item.getAttribute('data-collapsed-href');
          if (target) {
            window.location.href = target;
          }
        }
      });
    });
  }

  const stored = readStoredState();
  if (stored !== null) {
    setCollapsed(stored);
  }
  initMenuToggleItems();

  if (btnToggle) {
    btnToggle.addEventListener('click', toggleMenu);
  }

  syncIconState();

  const observer = new MutationObserver(function () {
    syncIconState();
  });

  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
  observer.observe(sidebar, { attributes: true, attributeFilter: ['class'] });
});
