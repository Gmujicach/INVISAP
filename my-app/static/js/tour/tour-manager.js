(function() {
  if (!window.INVISAP_TOUR_MANAGER) window.INVISAP_TOUR_MANAGER = {};

  const manager = window.INVISAP_TOUR_MANAGER;

  manager.getCurrentModule = function() {
    const body = document.body;
    if (body && body.dataset.module) return body.dataset.module;

    const path = window.location.pathname.replace(/\/+$/, '');
    const moduleRules = [
      { pattern: /bitacora/i, module: 'bitacora' },
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
      { pattern: /seguridad|gestionar-permisos/i, module: 'seguridad' },
      { pattern: /users|usuario|usuarios/i, module: 'usuarios' },
      { pattern: /ia|prioridad|gravedad/i, module: 'ia' },
      { pattern: /manual/i, module: 'manual' },
      { pattern: /login|inicio|landing/i, module: 'login' },
      { pattern: /home|dashboard/i, module: 'home' }
    ];

    for (const rule of moduleRules) {
      if (rule.pattern.test(path)) return rule.module;
    }

    if (!path) return 'home';

    const hash = window.location.hash.replace('#', '');
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
      if (!driverInstance) return null;
      if (typeof driverInstance.drive !== 'function') {
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
      manager.markModuleTourStarted(module);
      return driverInstance;
    } catch (error) {
      console.error('[Tour] Error al iniciar:', error);
      manager.activeInstance = null;
      manager.setActive(false);
      return null;
    }
  };

  manager.stopTour = function() {
    if (manager.activeInstance && typeof manager.activeInstance.destroy === 'function') {
      try {
        manager.activeInstance.destroy();
      } catch (e) {
        // destroy can throw if already destroyed
      }
    }
    manager.activeInstance = null;
    manager.setActive(false);
  };

  manager.toggleTour = function(moduleName) {
    if (manager.isActive()) manager.stopTour();
    else manager.startTour(moduleName);
  };

  manager.setActive = function(active) {
    manager._active = active;

    const menu = document.getElementById('tourFabMenu');
    if (menu) menu.classList.toggle('is-touring', active);

    const fab = document.getElementById('btnTourInvilara');
    if (!fab) return;

    if (active) {
      fab.setAttribute('aria-label', 'Guía del sistema, tour en curso');
      fab.title = 'Guía del Sistema · tour en curso';
      fab.classList.add('tour-active');
      // El panel se cierra al arrancar el recorrido
      if (window.INVISAP_TOUR_FAB) window.INVISAP_TOUR_FAB.close();
    } else {
      fab.setAttribute('aria-label', 'Guía del sistema');
      fab.title = 'Guía del Sistema';
      fab.classList.remove('tour-active');
      // Driver.js elimina aria-expanded del elemento resaltado al destruirse;
      // el panel está cerrado, así que se restituye el estado del menú.
      fab.setAttribute('aria-expanded', 'false');
    }
  };

  manager.isActive = function() {
    return manager._active === true;
  };

  manager.ONBOARDING_DURATION_MS = 7 * 24 * 60 * 60 * 1000;
  manager.ONBOARDING_STORAGE_PREFIX = 'invisap_tour_onboarding';

  manager.getOnboardingState = function() {
    const menu = document.getElementById('tourFabMenu');
    const userId = menu && menu.dataset.tourUserId;
    if (!userId) return null;

    const key = manager.ONBOARDING_STORAGE_PREFIX + ':' + encodeURIComponent(userId);
    try {
      let startedAt = Number(localStorage.getItem(key));
      if (!Number.isFinite(startedAt) || startedAt <= 0) {
        startedAt = Date.now();
        localStorage.setItem(key, String(startedAt));
      }

      const elapsed = Date.now() - startedAt;
      return {
        userId: userId,
        key: key,
        isActive: elapsed >= 0 && elapsed < manager.ONBOARDING_DURATION_MS
      };
    } catch (error) {
      console.warn('[Tour] No se pudo consultar el período de bienvenida; el inicio automático queda desactivado.', error);
      return null;
    }
  };

  manager.markModuleTourStarted = function(moduleName) {
    const onboarding = manager.getOnboardingState();
    if (!onboarding || !onboarding.isActive || !moduleName) return;
    try {
      localStorage.setItem(onboarding.key + ':modulo:' + encodeURIComponent(moduleName), 'true');
    } catch (error) {
      console.warn('[Tour] No se pudo guardar el módulo visitado durante la bienvenida.', error);
    }
  };

  manager.autoStart = function() {
    const pageTourButton = document.getElementById('btnTourInvilara');
    if (!pageTourButton) return;

    const pathname = window.location.pathname || '';
    const isLandingLikePage = pathname === '/' || pathname === '' || pathname.indexOf('landing') !== -1 || pathname.indexOf('login') !== -1;
    if (isLandingLikePage) return;

    const currentModule = manager.getCurrentModule();
    if (!currentModule || currentModule === 'default' || currentModule === 'login') return;

    const onboarding = manager.getOnboardingState();
    if (!onboarding || !onboarding.isActive) return;
    try {
      if (localStorage.getItem(onboarding.key + ':modulo:' + encodeURIComponent(currentModule)) === 'true') return;
    } catch (error) {
      console.warn('[Tour] No se pudo consultar el módulo visitado; se omite el inicio automático.', error);
      return;
    }

    const factory = (window.INVISAP_TOURS || {})[currentModule] || (window.INVISAP_TOURS || {})['default'];
    if (typeof factory !== 'function') return;
    setTimeout(function() {
      if (manager.isActive() || manager.getCurrentModule() !== currentModule) return;
      manager.startTour(currentModule);
    }, 700);
  };

  manager.DRIVER_DEFAULTS = {
    showProgress: true,
    nextBtnText: 'Siguiente',
    prevBtnText: 'Anterior',
    doneBtnText: 'Terminar',
    overlayColor: '#000000',
    overlayOpacity: 0.65,
    // Evita competir con la animación del resaltado al desplazar la página.
    smoothScroll: false,
    stagePadding: 16,
    stageRadius: 10,
    popoverOffset: 24,
    disableActiveInteraction: false,
    allowClose: true,
    animate: true
  };

  manager.filterAvailableSteps = function(steps) {
    if (!Array.isArray(steps)) return [];
    const availableSteps = [];

    steps.forEach(function(step) {
      if (!step || !step.element || typeof step.element !== 'string') return;
      const selectorList = step.element.split(',').map(function(item) {
        return item.trim();
      }).filter(Boolean);

      for (const selector of selectorList) {
        try {
          const candidates = document.querySelectorAll(selector);
          for (const element of candidates) {
            const rect = element.getBoundingClientRect();
            const style = window.getComputedStyle(element);
            if (!element.getClientRects().length || rect.width === 0 || rect.height === 0 ||
                style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
              continue;
            }
            availableSteps.push(Object.assign({}, step, { element: element }));
            return;
          }
        } catch (e) {
          continue;
        }
      }
    });

    return availableSteps;
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
        return null;
      }

      // Cualquier cierre del recorrido (botón del popover, Escape o clic en el
      // overlay) debe devolver el FAB y el panel a su estado inactivo.
      const onDestroyed = merged.onDestroyed;
      merged.onDestroyed = function() {
        manager._active = false;
        manager.activeInstance = null;
        manager.setActive(false);
        if (typeof onDestroyed === 'function') return onDestroyed.apply(this, arguments);
      };

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
    window.stopModuleTour = function() { manager.stopTour(); };
    window.toggleModuleTour = function() { manager.toggleTour(); };

    // El FAB de la guía abre su panel de acciones (ver tour-fab-menu.js);
    // el recorrido se inicia desde la celda «Iniciar guía».
    const fab = document.getElementById('btnTourInvilara');
    if (fab) {
      fab.setAttribute('aria-label', 'Guía del sistema');

      // Compatibilidad: si el HTML servido todavía no trae el panel (caché de
      // plantillas), el FAB conserva el comportamiento de iniciar/detener.
      if (!document.getElementById('tourFabMenu')) {
        fab.addEventListener('click', function(event) {
          event.preventDefault();
          event.stopPropagation();
          manager.toggleTour();
        });
      }
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
