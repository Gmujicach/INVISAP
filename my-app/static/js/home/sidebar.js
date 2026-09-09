window.InvilaraSidebarController = true;

function initInvilaraSidebar() {
  'use strict';

  if (window.__invilaraSidebarInitialized) return;
  window.__invilaraSidebarInitialized = true;

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
    if (window.Helpers && typeof window.Helpers.isSmallScreen === 'function' && window.Helpers.isSmallScreen()) {
      return !document.documentElement.classList.contains('layout-menu-expanded');
    }

    return document.documentElement.classList.contains('layout-menu-collapsed');
  }

  function setCollapsed(collapsed) {
    const isSmallScreen = window.Helpers && typeof window.Helpers.isSmallScreen === 'function'
      ? window.Helpers.isSmallScreen()
      : window.innerWidth < 992;

    if (isSmallScreen) {
      document.documentElement.classList.remove('layout-menu-collapsed');
      document.documentElement.classList.toggle('layout-menu-expanded', !collapsed);
    } else {
      document.documentElement.classList.toggle('layout-menu-collapsed', collapsed);
    }

    sidebar.classList.toggle('menu-collapsed', collapsed);
    sidebar.classList.toggle('layout-menu-expanded', !collapsed);

    requestAnimationFrame(function () {
      window.dispatchEvent(new Event('resize'));
    });
  }

  function getTopLevelLinks() {
    return Array.from(sidebar.querySelectorAll('.menu-inner > .menu-item > .menu-link'));
  }

  function getLinkLabel(link) {
    const textNode = link.querySelector(':scope > div');
    return (link.dataset.tooltip || (textNode ? textNode.textContent : link.textContent)).trim();
  }

  function syncMenuState() {
    sidebar.querySelectorAll('.menu-item > .menu-link').forEach(function (link) {
      const menuItem = link.closest('.menu-item');
      if (!menuItem) return;

      if (!link.hasAttribute('aria-label') && link.dataset.tooltip) {
        link.setAttribute('aria-label', link.dataset.tooltip);
      }

      if (link.classList.contains('menu-toggle')) {
        link.setAttribute('aria-expanded', String(menuItem.classList.contains('open')));
      }

      const isTopLevel = menuItem.parentElement && menuItem.parentElement.classList.contains('menu-inner');
      if (isTopLevel) {
        if (menuItem.classList.contains('active')) {
          link.setAttribute('aria-current', 'page');
        } else {
          link.removeAttribute('aria-current');
        }
      }
    });
  }

  function syncIconState() {
    const collapsed = isCollapsed();

    btnToggle.setAttribute('aria-expanded', String(!collapsed));
    btnToggle.setAttribute('aria-label', collapsed ? 'Expandir menú lateral' : 'Colapsar menú lateral');

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

    setCollapsed(nextState);

    writeStoredState(nextState);
    requestAnimationFrame(syncIconState);
    setTimeout(syncIconState, 50);
    setTimeout(syncIconState, 150);
    setTimeout(showCurrentPanel, 160);
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

  syncMenuState();
  initMenuToggleItems();
  btnToggle.addEventListener('click', toggleMenu);

  syncIconState();

  const observer = new MutationObserver(function () {
    const collapsed = isCollapsed();
    sidebar.classList.toggle('menu-collapsed', collapsed);
    sidebar.classList.toggle('layout-menu-expanded', !collapsed);
    syncIconState();
    syncMenuState();
  });

  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class', 'data-bs-theme'] });
  observer.observe(sidebar, { attributes: true, attributeFilter: ['class'], subtree: true });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initInvilaraSidebar, { once: true });
} else {
  initInvilaraSidebar();
}
