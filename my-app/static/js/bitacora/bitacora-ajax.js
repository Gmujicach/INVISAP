/* =========================================
   BITÁCORA - AUTO REFRESH CON AJAX
   ========================================= */
let autoRefreshInterval = null;
let isRefreshing = false;
let lastRefreshTime = 0;
const DEFAULT_REFRESH_INTERVAL = 30000; // 30 segundos
const MIN_REFRESH_INTERVAL = 2000; // 2 segundos mínimo entre refreshes manuales

function mostrarError(btn, mensaje) {
    if (!btn) return;
    const originalHtml = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `<i class="bi bi-exclamation-triangle me-1"></i> ${mensaje}`;
    btn.classList.remove('btn-outline-primary');
    btn.classList.add('btn-danger');
    setTimeout(() => {
        btn.disabled = false;
        btn.innerHTML = originalHtml;
        btn.classList.remove('btn-danger');
        btn.classList.add('btn-outline-primary');
    }, 3000);
}

function iniciarAutoRefresh(intervalo = DEFAULT_REFRESH_INTERVAL) {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    
    autoRefreshInterval = setInterval(() => {
        if (!document.hidden && !isRefreshing) {
            recargarBitacoraSilencioso();
        }
    }, intervalo);
    
    console.log(`Auto-refresh iniciado cada ${intervalo / 1000} segundos`);
}

function detenerAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
        console.log('Auto-refresh detenido');
    }
}

function recargarBitacoraSilencioso() {
    if (isRefreshing) return Promise.resolve();
    
    isRefreshing = true;
    
    const usuario = new URLSearchParams(window.location.search).get('usuario') || '';
    const modulo = new URLSearchParams(window.location.search).get('modulo') || '';
    const accion = new URLSearchParams(window.location.search).get('accion') || '';
    const page = new URLSearchParams(window.location.search).get('page') || '1';
    const per_page = new URLSearchParams(window.location.search).get('per_page') || '10';
    
    const params = new URLSearchParams();
    if (usuario) params.set('usuario', usuario);
    if (modulo) params.set('modulo', modulo);
    if (accion) params.set('accion', accion);
    params.set('page', page);
    params.set('per_page', per_page);
    params.set('silent', '1');
    
    return fetch(`/api/obtener-bitacora-json?${params.toString()}`)
        .then(res => {
            if (res.status === 401) {
                // Auto-refresh: solo log, no redirigir (usuario verá al interactuar)
                throw new Error('Sesión expirada');
            }
            return res.json();
        })
        .then(data => {
            const nuevosRegistros = Array.isArray(data) ? data : [];
            
            if (todasLasBitacoras.length !== nuevosRegistros.length || 
                JSON.stringify(todasLasBitacoras) !== JSON.stringify(nuevosRegistros)) {
                todasLasBitacoras = nuevosRegistros;
                aplicarBusquedaBitacoraYRenderizar();
                actualizarEstadisticas(nuevosRegistros);
            }
        })
        .catch(err => {
            console.error('Error en auto-refresh bitácora:', err);
            if (err.message === 'Sesión expirada' && !document.hidden) {
                console.warn('Sesión expirada - será redirigido al interactuar');
            }
        })
        .finally(() => {
            isRefreshing = false;
        });
}

function actualizarEstadisticas(registros) {
    const stats = { CREAR: 0, EDITAR: 0, ELIMINAR: 0 };
    
    registros.forEach(r => {
        const accion = (r.accion || '').toUpperCase();
        if (stats.hasOwnProperty(accion)) {
            stats[accion]++;
        }
    });
    
    const statCrear = document.querySelector('.stat-card[style*="10b981"] .stat-number');
    const statEditar = document.querySelector('.stat-card[style*="3b82f6"] .stat-number');
    const statEliminar = document.querySelector('.stat-card[style*="ef4444"] .stat-number');
    const statTotal = document.getElementById('total-registros');
    
    if (statCrear) statCrear.textContent = stats.CREAR;
    if (statEditar) statEditar.textContent = stats.EDITAR;
    if (statEliminar) statEliminar.textContent = stats.ELIMINAR;
    if (statTotal) statTotal.textContent = registros.length;
    
    const badgeTotal = document.querySelector('.badge.bg-primary');
    if (badgeTotal) badgeTotal.textContent = registros.length;
}

function forzarRefreshAhora() {
    recargarBitacoraSilencioso();
}

function recargarBitacoraConFeedback() {
    const btn = document.getElementById('btnActualizarBitacora');
    if (!btn) return Promise.reject(new Error('Botón no encontrado'));
    
    // Validación: prevenir clicks rápidos (debounce)
    const ahora = Date.now();
    if (ahora - lastRefreshTime < MIN_REFRESH_INTERVAL) {
        mostrarError(btn, 'Espere un momento...');
        return Promise.reject(new Error('Rate limited'));
    }
    lastRefreshTime = ahora;
    
    // Validación: prevenir doble click
    if (btn.disabled || isRefreshing) {
        return Promise.reject(new Error('Ya se está actualizando'));
    }
    
    btn.disabled = true;
    const originalHtml = btn.innerHTML;
    btn.innerHTML = '<i class="bi bi-arrow-clockwise me-1 spin"></i> Actualizando...';
    
    return recargarBitacoraSilencioso()
        .then(() => {
            // Éxito silencioso - solo restaurar botón
        })
        .catch(err => {
            if (err.message === 'Sesión expirada') {
                if (typeof Swal !== 'undefined') {
                    Swal.fire('Sesión expirada', 'Su sesión ha expirado. Por favor, inicie sesión nuevamente.', 'warning')
                        .then(() => window.location.href = '/login');
                } else {
                    alert('Su sesión ha expirado. Por favor, inicie sesión nuevamente.');
                    window.location.href = '/login';
                }
            } else if (err.message !== 'Rate limited' && err.message !== 'Ya se está actualizando') {
                mostrarError(btn, 'Error al actualizar');
            }
            throw err;
        })
        .finally(() => {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = originalHtml;
            }
        });
}

function cambiarIntervaloRefresh(nuevoIntervalo) {
    iniciarAutoRefresh(nuevoIntervalo);
}

document.addEventListener('DOMContentLoaded', function() {
    // Iniciar auto-refresh solo si no está en modo edición de filtros
    const urlParams = new URLSearchParams(window.location.search);
    if (!urlParams.has('usuario') && !urlParams.has('modulo') && !urlParams.has('accion')) {
        iniciarAutoRefresh();
    }
    
    // Event listener para el botón Actualizar
    const btnActualizar = document.getElementById('btnActualizarBitacora');
    if (btnActualizar) {
        btnActualizar.addEventListener('click', function(e) {
            e.preventDefault();
            recargarBitacoraConFeedback();
        });
    }
    
    // Detener auto-refresh cuando la pestaña no es visible
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            // Opcional: mantener corriendo en background
        } else {
            // Al volver a la pestaña, forzar refresh inmediato
            if (!isRefreshing) {
                setTimeout(() => recargarBitacoraSilencioso(), 500);
            }
        }
    });
    
    // Exponer funciones globalmente
    window.bitacoraAjax = {
        iniciar: iniciarAutoRefresh,
        detener: detenerAutoRefresh,
        refrescarAhora: forzarRefreshAhora,
        cambiarIntervalo: cambiarIntervaloRefresh
    };
});