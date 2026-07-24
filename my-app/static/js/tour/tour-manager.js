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
    const segment = path.split('/').pop();
    const map = {
      proyectos: 'proyectos', solicitudes: 'solicitudes', empleados: 'empleados',
      empresas: 'empresas', obras: 'obras', bitacora: 'bitacora',
      contratacion: 'contratacion', contrataciones: 'contratacion',
      evidencia: 'evidencia', evidencias: 'evidencia',
      inspeccion: 'inspeccion', inspecciones: 'inspeccion',
      inf_avance_obra: 'inf_avance_obra', publicaciones: 'publicaciones',
      perfil: 'perfil', reportes: 'reportes', respaldo: 'respaldo',
      seguridad: 'seguridad', usuarios: 'usuarios', ia: 'ia',
      login: 'login', manual: 'manual', home: 'home', dashboard: 'home'
    };
    if (map[segment]) return map[segment];
    for (const key of Object.keys(map)) {
      if (path.indexOf(key) !== -1) return map[key];
    }
    return 'default';
  };

  manager.startTour = function(moduleName) {
    if (manager.isActive()) manager.stopTour();
    const module = moduleName || manager.getCurrentModule();
    
    if (!manager.validateHash(module)) {
      console.warn('[Tour] Acceso denegado por hash inválido.');
      return null;
    }
    
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
      fab.title = 'Detener recorrido guiado';
      fab.classList.add('tour-active');
    } else {
      fab.setAttribute('aria-label', 'Iniciar tour del sistema');
      fab.title = 'Guía del Sistema';
      fab.classList.remove('tour-active');
    }
  };

  manager.isActive = function() {
    return manager._active === true;
  };

  manager.TOUR_STORAGE_KEY = 'invisap_tour_visto';
  manager.TOUR_RESET_KEY = 'invisap_tour_reset';
  manager.TOUR_HASH_KEY = 'invisap_tour_hash';

  manager.validateHash = function(moduleName) {
    try {
      const expectedHash = '#' + moduleName;
      const currentHash = window.location.hash;
      
      if (currentHash && currentHash !== expectedHash) {
        const allowed = ['home', 'dashboard'];
        if (!allowed.includes(moduleName)) {
          console.warn('[Tour] Hash inválido para módulo:', moduleName, 'Hash actual:', currentHash);
          return false;
        }
      }
      
      if (!currentHash && moduleName !== 'home' && moduleName !== 'default') {
        const validWithoutHash = ['login', 'manual'];
        if (!validWithoutHash.includes(moduleName)) {
          console.warn('[Tour] Módulo requiere hash:', moduleName);
          return false;
        }
      }
      
      return true;
    } catch (e) {
      return true;
    }
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
    const factory = (window.INVISAP_TOURS || {})[manager.getCurrentModule()] || (window.INVISAP_TOURS || {})['default'];
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

  manager.applyDriverDefaults = function() {
    if (!window.driver || !window.driver.js || typeof window.driver.js.driver !== 'function') return;
    const original = window.driver.js.driver;
    window.driver.js.driver = function(opts) {
      const merged = Object.assign({}, manager.DRIVER_DEFAULTS, opts || {});
      if (opts && opts.popover) {
        merged.popover = Object.assign({}, manager.DRIVER_DEFAULTS.popover, opts.popover);
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
