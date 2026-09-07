window.InvilaraSidebarController = true;

function initInvilaraSidebar() {
  'use strict';

  const sidebar = document.getElementById('layout-menu');
  const btnToggle = document.getElementById('sidebarToggleBtn');
  const iconoCerrar = document.getElementById('icono-cerrar');
  const iconoAbrir = document.getElementById('icono-abrir');
  const labelPanel = document.getElementById('sidebar-label-panel');
  const panelType = document.getElementById('sidebar-panel-type');
  const panelTitle = document.getElementById('sidebar-panel-title');
  const panelDescription = document.getElementById('sidebar-panel-description');
  const panelMeta = document.getElementById('sidebar-panel-meta');
  const panelItems = document.getElementById('sidebar-panel-items');
  const panelAction = document.getElementById('sidebar-panel-action');
  const panelClose = document.getElementById('sidebar-panel-close');

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

  function getTopLevelLinks() {
    return Array.from(sidebar.querySelectorAll('.menu-inner > .menu-item > .menu-link'));
  }

  function getLinkLabel(link) {
    const textNode = link.querySelector(':scope > div');
    return (link.dataset.tooltip || (textNode ? textNode.textContent : link.textContent)).trim();
  }

  function getPanelData(link) {
    const menuItem = link.closest('.menu-item');
    const menuSub = menuItem ? menuItem.querySelector(':scope > .menu-sub') : null;
    const subLinks = menuSub ? Array.from(menuSub.querySelectorAll(':scope > .menu-item > .menu-link')) : [];
    const title = getLinkLabel(link);
    const isModule = subLinks.length > 0;
    const directHref = link.dataset.collapsedHref || (subLinks[0] ? subLinks[0].getAttribute('href') : link.getAttribute('href'));

    return {
      title,
      type: isModule ? 'Módulo' : 'Acción',
      description: link.dataset.panelDescription || (isModule
        ? 'Gestiona y da seguimiento a ' + title.toLowerCase() + '.'
        : 'Accede directamente a ' + title.toLowerCase() + '.'),
      subLinks,
      directHref: directHref && directHref !== 'javascript:void(0);' ? directHref : '#'
    };
  }

  let suppressNextPanelFocus = false;

  function closePanel(restoreFocus) {
    if (!labelPanel) return;

    labelPanel.hidden = true;
    labelPanel.setAttribute('aria-hidden', 'true');

    if (restoreFocus && document.activeElement && document.activeElement.closest('#sidebar-label-panel')) {
      const currentLink = getTopLevelLinks().find(function (link) {
        return link.closest('.menu-item').classList.contains('active');
      });
      if (currentLink) {
        suppressNextPanelFocus = true;
        currentLink.focus({ preventScroll: true });
      }
    }
  }

  function renderPanel(link) {
    if (!labelPanel || !isCollapsed() || !link) return;

    const data = getPanelData(link);
    panelType.textContent = data.type;
    panelTitle.textContent = data.title;
    panelDescription.textContent = data.description;
    panelMeta.textContent = data.subLinks.length
      ? data.subLinks.length + (data.subLinks.length === 1 ? ' acción disponible' : ' acciones disponibles')
      : 'Acción directa';
    panelAction.href = data.directHref;
    panelClose.setAttribute('aria-label', 'Cerrar panel de ' + data.title);
    panelItems.innerHTML = '';

    if (data.subLinks.length) {
      data.subLinks.forEach(function (subLink) {
        const row = document.createElement('div');
        const icon = subLink.querySelector('.menu-icon, .nav-icon');
        const textNode = subLink.querySelector(':scope > div');
        const text = document.createElement('span');

        row.className = 'sidebar-panel-item';
        text.textContent = (textNode ? textNode.textContent : subLink.textContent).trim();

        if (icon) {
          const iconClone = icon.cloneNode(true);
          iconClone.setAttribute('aria-hidden', 'true');
          row.appendChild(iconClone);
        }

        row.appendChild(text);
        panelItems.appendChild(row);
      });
    } else {
      const row = document.createElement('div');
      const icon = document.createElement('i');
      const text = document.createElement('span');

      row.className = 'sidebar-panel-item';
      icon.className = 'menu-icon bi bi-arrow-right-circle';
      icon.setAttribute('aria-hidden', 'true');
      text.textContent = 'Acceso directo al módulo';
      row.appendChild(icon);
      row.appendChild(text);
      panelItems.appendChild(row);
    }

    labelPanel.hidden = false;
    labelPanel.setAttribute('aria-hidden', 'false');
  }

  function showCurrentPanel() {
    if (!isCollapsed()) {
      closePanel(false);
      return;
    }

    const currentLink = getTopLevelLinks().find(function (link) {
      return link.closest('.menu-item').classList.contains('active');
    });

    if (currentLink) renderPanel(currentLink);
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

    if (window.Helpers && typeof window.Helpers.toggleCollapsed === 'function') {
      window.Helpers.toggleCollapsed();
    } else {
      setCollapsed(nextState);
    }

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

  getTopLevelLinks().forEach(function (link) {
    link.addEventListener('mouseenter', function () {
      renderPanel(link);
    });
    link.addEventListener('focusin', function () {
      if (suppressNextPanelFocus) {
        suppressNextPanelFocus = false;
        return;
      }
      renderPanel(link);
    });
  });

  if (panelClose) {
    panelClose.addEventListener('click', function () {
      closePanel(true);
    });
  }

  document.addEventListener('click', function (event) {
    if (labelPanel && !labelPanel.hidden && !labelPanel.contains(event.target) && !sidebar.contains(event.target)) {
      closePanel(false);
    }
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && labelPanel && !labelPanel.hidden) {
      closePanel(true);
    }
  });

  syncIconState();
  showCurrentPanel();

  const observer = new MutationObserver(function () {
    syncIconState();
    syncMenuState();
    showCurrentPanel();
  });

  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
  observer.observe(sidebar, { attributes: true, attributeFilter: ['class'], subtree: true });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initInvilaraSidebar, { once: true });
} else {
  initInvilaraSidebar();
}
