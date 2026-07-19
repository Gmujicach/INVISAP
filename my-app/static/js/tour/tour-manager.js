(function() {
  console.log('[Tour] tour-manager.js cargado');
  if (!window.INVISAP_TOUR_MANAGER) window.INVISAP_TOUR_MANAGER = {};

  const manager = window.INVISAP_TOUR_MANAGER;

  manager.getCurrentModule = function() {
    const body = document.body;
    if (body && body.dataset.module) {
      return body.dataset.module;
    }
    const path = window.location.pathname.replace(/\/+$/, '');
    if (!path || path === '') return 'home';
    const segment = path.split('/').pop();
    const map = {
      'proyectos': 'proyectos',
      'solicitudes': 'solicitudes',
      'empleados': 'empleados',
      'empresas': 'empresas',
      'obras': 'obras',
      'bitacora': 'bitacora',
      'contratacion': 'contratacion',
      'contrataciones': 'contratacion',
      'evidencia': 'evidencia',
      'evidencias': 'evidencia',
      'inspeccion': 'inspeccion',
      'inspecciones': 'inspeccion',
      'inf_avance_obra': 'inf_avance_obra',
      'publicaciones': 'publicaciones',
      'perfil': 'perfil',
      'reportes': 'reportes',
      'respaldo': 'respaldo',
      'seguridad': 'seguridad',
      'usuarios': 'usuarios',
      'ia': 'ia',
      'login': 'login',
      'manual': 'manual',
      'home': 'home',
      'dashboard': 'home'
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
    console.log('[Tour] Intentando iniciar tour para módulo:', module);
    const registry = window.INVISAP_TOURS || {};
    console.log('[Tour] Tours registrados:', Object.keys(registry));
    const factory = registry[module] || registry['default'];
    if (typeof factory !== 'function') {
      console.warn('[Tour] No hay tour registrado para el módulo:', module);
      alert('No hay guía disponible para este módulo: ' + module);
      return null;
    }
    if (typeof window.driver === 'undefined' || typeof window.driver.js !== 'function') {
      console.error('[Tour] driver.js no está disponible en window.driver.js');
      alert('El motor de recorridos (driver.js) no está disponible.');
      return null;
    }
    try {
      const driverInstance = window.driver.js();
      driverInstance.drive();
      manager.activeInstance = driverInstance;
      manager.setActive(true);
      console.log('[Tour] Tour iniciado correctamente');
      return driverInstance;
    } catch (error) {
      console.error('[Tour] Error al iniciar el tour:', error);
      alert('Error al iniciar el tour: ' + error.message);
      return null;
    }
  };

  manager.stopTour = function() {
    if (manager.activeInstance && typeof manager.activeInstance.destroy === 'function') {
      manager.activeInstance.destroy();
    }
    manager.activeInstance = null;
    manager.setActive(false);
    console.log('[Tour] Tour detenido');
  };

  manager.toggleTour = function(moduleName) {
    console.log('[Tour] toggleTour llamado. active:', manager.isActive());
    if (manager.isActive()) {
      manager.stopTour();
    } else {
      manager.startTour(moduleName);
    }
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

  manager.init = function() {
    if (!window.INVISAP_TOURS) window.INVISAP_TOURS = {};

    window.startModuleTour = function() {
      manager.startTour();
    };

    window.stopModuleTour = function() {
      manager.stopTour();
    };

    window.toggleModuleTour = function() {
      manager.toggleTour();
    };

    const fab = document.getElementById('btnTourInvilara');
    if (!fab) {
      console.warn('[Tour] No se encontró el botón #btnTourInvilara');
      return;
    }

    console.log('[Tour] Botón de tour encontrado, bindeando click');
    fab.addEventListener('click', function() {
      manager.toggleTour();
    });
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      manager.init();
    });
  } else {
    manager.init();
  }
})();
