/* =========================================
   BITÁCORA CON PAGINACIÓN CLIENT-SIDE
   ========================================= */
let todasLasBitacoras = [];
let paginaActualBitacora = 1;
let registrosPorPaginaBitacora = 10;
let busquedaActualBitacora = '';

function buildAccionBadge(accion) {
    const a = (accion || 'VER').toUpperCase();
    if (a === 'CREAR') return '<span class="action-badge badge-crear"><i class="bi bi-plus-circle-fill me-1"></i>CREAR</span>';
    if (a === 'EDITAR') return '<span class="action-badge badge-editar"><i class="bi bi-pencil-fill me-1"></i>EDITAR</span>';
    if (a === 'ELIMINAR') return '<span class="action-badge badge-eliminar"><i class="bi bi-trash-fill me-1"></i>ELIMINAR</span>';
    if (a === 'LOGIN') return '<span class="action-badge badge-login"><i class="bi bi-box-arrow-in-right me-1"></i>LOGIN</span>';
    if (a === 'LOGOUT') return '<span class="action-badge badge-logout"><i class="bi bi-box-arrow-right me-1"></i>LOGOUT</span>';
    return '<span class="action-badge badge-ver"><i class="bi bi-eye-fill me-1"></i>VER</span>';
}

function renderizarBitacoras(registros) {
    const tbody = document.querySelector('#tbody_bitacora');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (registros.length === 0) {
        tbody.innerHTML = '<tr class="fila-vacia"><td colspan="6" class="text-center py-5 text-muted">No hay registros en la bitácora</td></tr>';
        document.getElementById('pagination_container').style.display = 'none';
        document.getElementById('total-registros').innerText = '0';
        return;
    }

    const inicio = (paginaActualBitacora - 1) * registrosPorPaginaBitacora;
    const fin = Math.min(inicio + registrosPorPaginaBitacora, registros.length);
    const paginaRegistros = registros.slice(inicio, fin);

    let html = '';
    paginaRegistros.forEach((r, idx) => {
        html += `<tr class="fila-registro">
            <td class="text-muted" style="padding: 0.85rem 1.2rem; font-size:0.8rem;">${inicio + idx + 1}</td>
            <td style="padding: 0.85rem 1.2rem;">
              <span class="usuario-chip">${r.usuario || ' '}</span>
            </td>
            <td style="padding: 0.85rem 1.2rem;">
              <span class="modulo-chip">${r.modulo || ' '}</span>
            </td>
            <td style="padding: 0.85rem 1.2rem;">
              ${buildAccionBadge(r.accion)}
            </td>
            <td style="padding: 0.85rem 1.2rem; font-size:0.83rem; color:#475569;">
              <i class="bi bi-calendar3 me-1 text-primary opacity-50"></i>
              ${r.fecha ? (r.fecha.includes(' ') ? r.fecha : r.fecha + ' ') : ' '}
            </td>
            <td style="padding: 0.85rem 1.2rem; font-size:0.83rem; color:#475569;">
              ${r.hora_inicio_sesion || ' '}
            </td>
          </tr>`;
    });

    tbody.innerHTML = html;

    const totalPaginas = Math.ceil(registros.length / registrosPorPaginaBitacora);
    document.getElementById('info_registros_bitacora').textContent = `Mostrando ${inicio + 1} a ${fin} de ${registros.length} registros`;
    renderizarControlesBitacora(totalPaginas);
    document.getElementById('pagination_container').style.display = 'flex';
    document.getElementById('total-registros').innerText = registros.length;
}

function renderizarControlesBitacora(totalPaginas) {
    const controls = document.getElementById('pagination_controls_bitacora');
    controls.innerHTML = '';

    const botonAnterior = document.createElement('li');
    botonAnterior.className = `page-item ${paginaActualBitacora === 1 ? 'disabled' : ''}`;
    botonAnterior.innerHTML = `<button class="page-link" onclick="cambiarPaginaBitacora(${paginaActualBitacora - 1})">Anterior</button>`;
    controls.appendChild(botonAnterior);

    for (let i = 1; i <= totalPaginas; i++) {
        const li = document.createElement('li');
        li.className = `page-item ${i === paginaActualBitacora ? 'active' : ''}`;
        li.innerHTML = `<button class="page-link" onclick="cambiarPaginaBitacora(${i})">${i}</button>`;
        controls.appendChild(li);
    }

    const botonSiguiente = document.createElement('li');
    botonSiguiente.className = `page-item ${paginaActualBitacora === totalPaginas ? 'disabled' : ''}`;
    botonSiguiente.innerHTML = `<button class="page-link" onclick="cambiarPaginaBitacora(${paginaActualBitacora + 1})">Siguiente</button>`;
    controls.appendChild(botonSiguiente);
}

window.cambiarPaginaBitacora = function(nuevaPagina) {
    const totalPaginas = Math.ceil(todasLasBitacoras.length / registrosPorPaginaBitacora);
    if (nuevaPagina < 1 || nuevaPagina > totalPaginas) return;
    paginaActualBitacora = nuevaPagina;
    aplicarBusquedaBitacoraYRenderizar();
    document.getElementById('registros_por_pagina_bitacora').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
};

window.buscarBitacora = function(termino) {
    busquedaActualBitacora = termino;
    paginaActualBitacora = 1;
    aplicarBusquedaBitacoraYRenderizar();
};

function aplicarBusquedaBitacoraYRenderizar() {
    let registrosFiltrados = todasLasBitacoras;
    if (busquedaActualBitacora.trim()) {
        const term = busquedaActualBitacora.toLowerCase();
        registrosFiltrados = registrosFiltrados.filter(r =>
            (r.usuario && r.usuario.toLowerCase().includes(term)) ||
            (r.modulo && r.modulo.toLowerCase().includes(term)) ||
            (r.accion && r.accion.toLowerCase().includes(term)) ||
            (r.fecha && r.fecha.toLowerCase().includes(term)) ||
            (r.hora_inicio_sesion && r.hora_inicio_sesion.toLowerCase().includes(term))
        );
    }
    renderizarBitacoras(registrosFiltrados);
}

document.addEventListener('DOMContentLoaded', function() {
    const selectRegistros = document.getElementById('registros_por_pagina_bitacora');
    if (selectRegistros) {
        selectRegistros.value = registrosPorPaginaBitacora;
        selectRegistros.addEventListener('change', function() {
            registrosPorPaginaBitacora = parseInt(this.value);
            paginaActualBitacora = 1;
            aplicarBusquedaBitacoraYRenderizar();
        });
    }

    cargarBitacora();
});

function cargarBitacora() {
    const usuario = new URLSearchParams(window.location.search).get('usuario') || '';
    const modulo = new URLSearchParams(window.location.search).get('modulo') || '';
    const accion = new URLSearchParams(window.location.search).get('accion') || '';

    const params = new URLSearchParams();
    if (usuario) params.set('usuario', usuario);
    if (modulo) params.set('modulo', modulo);
    if (accion) params.set('accion', accion);

    fetch(`/api/obtener-bitacora-json?${params.toString()}`)
        .then(res => res.json())
        .then(data => {
            todasLasBitacoras = Array.isArray(data) ? data : [];
            paginaActualBitacora = 1;
            busquedaActualBitacora = '';
            const input = document.getElementById('buscarBitacora');
            if (input) input.value = '';
            renderizarBitacoras(todasLasBitacoras);
        })
        .catch(err => console.error('Error cargando bitácora:', err));
}