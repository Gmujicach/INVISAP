document.addEventListener('DOMContentLoaded', function () {
  'use strict';

  const sidebar = document.getElementById('layout-menu');
  const btnToggle = document.getElementById('sidebarToggleBtn');
  const iconoCerrar = document.getElementById('icono-cerrar');
  const iconoAbrir = document.getElementById('icono-abrir');

  if (!sidebar) return;

  function isCollapsed() {
    const rootCollapsed = document.documentElement.classList.contains('layout-menu-collapsed');
    const sidebarCollapsed = sidebar.classList.contains('menu-collapsed');
    return rootCollapsed || sidebarCollapsed;
  }

  function syncIconState() {
    const collapsed = isCollapsed();

    if (btnToggle) {
      btnToggle.setAttribute('aria-expanded', String(!collapsed));
    }

    if (iconoCerrar) {
      iconoCerrar.style.display = collapsed ? 'none' : 'block';
    }

    if (iconoAbrir) {
      iconoAbrir.style.display = collapsed ? 'block' : 'none';
    }
  }

  function toggleMenu(e) {
    if (e) e.preventDefault();

    const nextState = !isCollapsed();

    if (window.Helpers && typeof window.Helpers.toggleCollapsed === 'function') {
      window.Helpers.toggleCollapsed();
    } else {
      document.documentElement.classList.toggle('layout-menu-collapsed', nextState);
      sidebar.classList.toggle('menu-collapsed', nextState);
      setTimeout(function () {
        window.dispatchEvent(new Event('resize'));
      }, 30);
    }

    requestAnimationFrame(syncIconState);
  }

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
