(function() {
  if (!window.INVISAP_TOUR_MANAGER) window.INVISAP_TOUR_MANAGER = {};

  const manager = window.INVISAP_TOUR_MANAGER;

  manager.getCurrentModule = function() {
    const body = document.body;
    if (body && body.dataset.module) return body.dataset.module;

    const hash = window.location.hash.replace('#', '');
    if (hash) {
      const hashMap = {
        'proyectos': 'proyectos', 'solicitudes': 'solicitudes', 'empleados': 'empleados',
        'empresas': 'empresas', 'obras': 'obras', 'bitacora': 'bitacora',
        'contratacion': 'contratacion', 'contrataciones': 'contratacion',
        'evidencia': 'evidencia', 'evidencias': 'evidencia',
        'inspeccion': 'inspeccion', 'inspecciones': 'inspeccion',
        'inf_avance_obra': 'inf_avance_obra', 'publicaciones': 'publicaciones',
        'perfil': 'perfil', 'reportes': 'reportes', 'respaldo': 'respaldo',
        'seguridad': 'seguridad', 'usuarios': 'usuarios', 'ia': 'ia',
        'login': 'login', 'manual': 'manual', 'home': 'home', 'dashboard': 'home'
      };
      if (hashMap[hash]) return hashMap[hash];
    }

    const path = window.location.pathname.replace(/\/+$/, '');
    if (!path || path === '') return 'home';

    const moduleRules = [
      { pattern: /solicitud|solicitudes/i, module: 'solicitudes' },
      { pattern: /proyecto|proyectos/i, module: 'proyectos' },
      { pattern: /empleado|empleados/i, module: 'empleados' },
      { pattern: /empresa|empresas/i, module: 'empresas' },
      { pattern: /editar-informe|avance_obra|inf_avance_obra|avanceobra/i, module: 'inf_avance_obra' },
      { pattern: /obra|obras/i, module: 'obras' },
      { pattern: /contratacion|contrataciones/i, module: 'contratacion' },
      { pattern: /evidencia|evidencias/i, module: 'evidencia' },
      { pattern: /inspeccion|inspecciones/i, module: 'inspeccion' },
      { pattern: /publicacion|publicaciones/i, module: 'publicaciones' },
      { pattern: /perfil/i, module: 'perfil' },
      { pattern: /reporte|reportes/i, module: 'reportes' },
      { pattern: /respaldo/i, module: 'respaldo' },
      { pattern: /seguridad/i, module: 'seguridad' },
      { pattern: /users|usuario|usuarios/i, module: 'usuarios' },
      { pattern: /ia|prioridad|gravedad/i, module: 'ia' },
      { pattern: /manual/i, module: 'manual' },
      { pattern: /login|inicio|landing/i, module: 'login' },
      { pattern: /home|dashboard/i, module: 'home' }
    ];

    for (const rule of moduleRules) {
      if (rule.pattern.test(path)) return rule.module;
    }

    return 'default';
  };

  manager.startTour = function(moduleName) {
    if (manager.isActive()) manager.stopTour();
    const module = moduleName || manager.getCurrentModule();

    const registry = window.INVISAP_TOURS || {};
    const factory = registry[module] || registry['default'];
    if (typeof factory !== 'function') {
      console.warn('[Tour] Sin tour para:', module);
      return null;
    }
    try {
      if (typeof window.driver === 'undefined' || typeof window.driver.js === 'undefined' || typeof window.driver.js.driver !== 'function') {
        console.error('[Tour] Driver.js no se ha cargado correctamente.');
        return null;
      }

      const driverInstance = factory();
      if (!driverInstance || typeof driverInstance.drive !== 'function') {
        console.error('[Tour] La factory no devolvió una instancia válida.');
        return null;
      }
      manager.activeInstance = driverInstance;
      manager.setActive(true);

      const validModules = ['proyectos', 'solicitudes', 'empleados', 'empresas', 'obras', 'bitacora',
        'contratacion', 'evidencia', 'inspeccion', 'inf_avance_obra', 'publicaciones',
        'perfil', 'reportes', 'respaldo', 'seguridad', 'usuarios', 'ia', 'login', 'manual'];
      if (validModules.includes(module)) {
        try {
          if (!window.location.hash || window.location.hash !== '#' + module) {
            window.location.hash = '#' + module;
          }
        } catch (e) {}
      }

      driverInstance.drive();
      return driverInstance;
    } catch (error) {
      console.error('[Tour] Error al iniciar:', error);
      manager.activeInstance = null;
      manager.setActive(false);
      return null;
    }
  };

  manager.stopTour = function(markSeen) {
    if (manager.activeInstance && typeof manager.activeInstance.destroy === 'function') {
      try {
        manager.activeInstance.destroy();
      } catch (e) {
        // destroy can throw if already destroyed
      }
    }
    manager.activeInstance = null;
    manager.setActive(false);
    if (markSeen) manager.markTourSeen();
  };

  manager.toggleTour = function(moduleName) {
    if (manager.isActive()) manager.stopTour(true);
    else manager.startTour(moduleName);
  };

  manager.setActive = function(active) {
    manager._active = active;
    const fab = document.getElementById('btnTourInvilara');
    if (!fab) return;
    if (active) {
      fab.setAttribute('aria-label', 'Detener tour del sistema');
      fab.setAttribute('aria-pressed', 'true');
      fab.title = 'Detener recorrido guiado';
      fab.classList.add('tour-active');
    } else {
      fab.setAttribute('aria-label', 'Iniciar tour del sistema');
      fab.setAttribute('aria-pressed', 'false');
      fab.title = 'Guía del Sistema';
      fab.classList.remove('tour-active');
    }
  };

  manager.isActive = function() {
    return manager._active === true;
  };

  manager.TOUR_STORAGE_KEY = 'invisap_tour_visto';
  manager.TOUR_RESET_KEY = 'invisap_tour_reset';

  manager.validateHash = function(moduleName) {
    return true;
  };

  manager.hasSeenTour = function() {
    try { return localStorage.getItem(manager.TOUR_STORAGE_KEY) === 'true'; }
    catch (e) { return false; }
  };

  manager.markTourSeen = function() {
    try { localStorage.setItem(manager.TOUR_STORAGE_KEY, 'true'); } catch (e) {}
  };

  manager.resetTourSeen = function() {
    try { localStorage.removeItem(manager.TOUR_STORAGE_KEY); } catch (e) {}
  };

  manager.autoStart = function() {
    if (manager.hasSeenTour()) return;
    const pageTourButton = document.getElementById('btnTourInvilara');
    if (!pageTourButton) return;

    const pathname = window.location.pathname || '';
    const isLandingLikePage = pathname === '/' || pathname === '' || pathname.indexOf('landing') !== -1 || pathname.indexOf('login') !== -1;
    if (isLandingLikePage) return;

    const currentModule = manager.getCurrentModule();
    if (!currentModule || currentModule === 'default' || currentModule === 'login') return;

    const factory = (window.INVISAP_TOURS || {})[currentModule] || (window.INVISAP_TOURS || {})['default'];
    if (typeof factory !== 'function') return;
    setTimeout(function() { manager.startTour(); }, 700);
  };

  manager.DRIVER_DEFAULTS = {
    showProgress: true,
    nextBtnText: 'Siguiente',
    prevBtnText: 'Anterior',
    doneBtnText: 'Terminar',
    overlayColor: '#000000',
    overlayOpacity: 0.65,
    smoothScroll: true,
    stagePadding: 16,
    stageRadius: 10,
    popoverOffset: 24,
    disableActiveInteraction: false,
    allowClose: true,
    animate: true
  };

  manager.filterAvailableSteps = function(steps) {
    if (!Array.isArray(steps)) return [];
    return steps.filter(function(step) {
      if (!step || !step.element || typeof step.element !== 'string') return false;
      const selectorList = step.element.split(',').map(function(item) {
        return item.trim();
      }).filter(Boolean);

      for (const selector of selectorList) {
        try {
          const element = document.querySelector(selector);
          if (!element) continue;
          const rect = element.getBoundingClientRect();
          if (rect.width === 0 && rect.height === 0) continue;
          return true;
        } catch (e) {
          continue;
        }
      }
      return false;
    });
  };

  manager.applyDriverDefaults = function() {
    if (!window.driver || !window.driver.js || typeof window.driver.js.driver !== 'function') return;
    const original = window.driver.js.driver;
    window.driver.js.driver = function(opts) {
      const merged = Object.assign({}, manager.DRIVER_DEFAULTS, opts || {});
      if (opts && opts.popover) {
        merged.popover = Object.assign({}, manager.DRIVER_DEFAULTS.popover, opts.popover);
      }
      if (Array.isArray(opts && opts.steps)) {
        merged.steps = manager.filterAvailableSteps(opts.steps);
      }

      if (!Array.isArray(merged.steps) || merged.steps.length === 0) {
        console.warn('[Tour] No hay pasos válidos para el módulo actual. Se omite la ejecución del recorrido.');
        return {
          drive: function() {},
          destroy: function() {},
          hasNextStep: function() { return false; }
        };
      }

      return original(merged);
    };
  };

  manager.isDarkMode = function() {
    return document.body.classList.contains('dark-mode') ||
           document.documentElement.getAttribute('data-theme') === 'theme-dark';
  };

  manager.init = function() {
    if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};
    manager.applyDriverDefaults();
    window.startModuleTour = function() { manager.startTour(); };
    window.stopModuleTour = function() { manager.stopTour(true); };
    window.toggleModuleTour = function() { manager.toggleTour(); };

    document.body.addEventListener('click', function(event) {
      const fab = event.target.closest('#btnTourInvilara');
      if (!fab) return;
      event.preventDefault();
      event.stopPropagation();
      manager.toggleTour();
    });

    const fab = document.getElementById('btnTourInvilara');
    if (fab) {
      fab.setAttribute('aria-pressed', 'false');
      fab.setAttribute('aria-label', 'Iniciar tour del sistema');
    }

    const inst = manager.activeInstance;
    if (inst && typeof inst.hasNextStep === 'function') {
      inst.refresh();
    }

    manager.autoStart();
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { manager.init(); });
  } else {
    manager.init();
  }
})();
