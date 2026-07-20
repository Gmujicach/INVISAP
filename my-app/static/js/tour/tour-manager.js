(function() {
  if (!window.INVISAP_TOUR_MANAGER) window.INVISAP_TOUR_MANAGER = {};

  const manager = window.INVISAP_TOUR_MANAGER;

  manager.getCurrentModule = function() {
    const body = document.body;
    if (body && body.dataset.module) return body.dataset.module;
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
    manager.stopTour();
    const module = moduleName || manager.getCurrentModule();
    const registry = window.INVISAP_TOURS || {};
    const factory = registry[module] || registry['default'];
    if (typeof factory !== 'function') {
      console.warn('[Tour] Sin tour para:', module);
      return null;
    }
    try {
      if (typeof window.driver === 'undefined' || typeof window.driver.js === 'undefined' || typeof window.driver.js.driver !== 'function') {
        console.error('[Tour] Driver.js no se ha cargado correctamente de forma local.');
        return null;
      }
      const driverInstance = factory();
      if (!driverInstance || typeof driverInstance.drive !== 'function') {
        console.error('[Tour] La factory no devolvió una instancia válida de Driver.js.');
        return null;
      }
      driverInstance.drive();
      manager.activeInstance = driverInstance;
      manager.setActive(true);
      return driverInstance;
    } catch (error) {
      console.error('[Tour] Error al iniciar:', error);
      return null;
    }
  };

  manager.stopTour = function(markSeen) {
    if (manager.activeInstance && typeof manager.activeInstance.destroy === 'function') {
      manager.activeInstance.destroy();
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
    setTimeout(function() { manager.startTour(); }, 600);
  };

  manager.init = function() {
    if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};
    window.startModuleTour = function() { manager.startTour(); };
    window.stopModuleTour = function() { manager.stopTour(); };
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