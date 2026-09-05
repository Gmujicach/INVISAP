/* =========================================
   BITÁCORA CON PAGINACIÓN CLIENT-SIDE
   ========================================= */
let todasLasBitacoras = [];
let paginaActualBitacora = 1;
let registrosPorPaginaBitacora = 10;
let busquedaActualBitacora = '';

function escapeHtmlAttr(value) {
    return String(value || '')
        .replace(/&/g, '&amp;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}

function parseFecha(value) {
    if (!value) return null;
    const cleaned = String(value)
        .replace(/\s*GMT\s*$/i, '')
        .replace(/\s*[+-]\d{2}:?\d{2}$/, '')
        .trim();
    const date = new Date(cleaned);
    return isNaN(date.getTime()) ? null : date;
}

function buildAccionBadge(accion) {
    const a = (accion || 'VER').toUpperCase();
    if (a === 'CREAR') return '<span class="action-badge badge-crear"><i class="bi bi-plus-circle-fill me-1"></i>CREAR</span>';
    if (a === 'EDITAR') return '<span class="action-badge badge-editar"><i class="bi bi-pencil-fill me-1"></i>EDITAR</span>';
    if (a === 'ELIMINAR') return '<span class="action-badge badge-eliminar"><i class="bi bi-trash-fill me-1"></i>ELIMINAR</span>';
    if (a === 'LOGIN') return '<span class="action-badge badge-login"><i class="bi bi-box-arrow-in-right me-1"></i>LOGIN</span>';
    if (a === 'LOGOUT') return '<span class="action-badge badge-logout"><i class="bi bi-box-arrow-right me-1"></i>LOGOUT</span>';
    return '<span class="action-badge badge-ver"><i class="bi bi-eye-fill me-1"></i>VER</span>';
}

function buildFriendlyMessage(usuario, accion, modulo, fecha, horaInicio, horaCierre) {
    const u = String(usuario || 'Usuario').trim();
    const a = String(accion || 'VER').toUpperCase().trim();
    const m = String(modulo || 'General').trim();
    const f = parseFecha(fecha) || new Date();
    const hours = f.getHours();
    const period = hours >= 12 ? 'PM' : 'AM';
    const hour12 = hours % 12 || 12;
    const minutes = String(f.getMinutes()).padStart(2, '0');
    const seconds = String(f.getSeconds()).padStart(2, '0');
    const timeStr = `${hour12}:${minutes}:${seconds} ${period}`;

    const verbMap = {
        'CREAR': 'creó',
        'EDITAR': 'modificó',
        'ELIMINAR': 'eliminó',
        'VER': 'consultó',
        'LOGIN': 'inició sesión en',
        'LOGOUT': 'cerró sesión en',
        'ACCESO_DENEGADO': 'intentó acceder a',
        'GENERAR_REPORTE': 'generó un reporte de'
    };
    const verb = verbMap[a] || 'realizó una acción en';

    let message = '';
    if (a === 'LOGIN') {
        message = `El usuario ${u} ${verb} el sistema`;
    } else if (a === 'LOGOUT') {
        message = `El usuario ${u} ${verb} el sistema`;
    } else if (a === 'VER') {
        message = `El usuario ${u} ${verb} información del módulo ${m}`;
    } else if (a === 'CREAR') {
        message = `El usuario ${u} ${verb} un nuevo registro dentro del módulo ${m}`;
    } else if (a === 'EDITAR') {
        message = `El usuario ${u} ${verb} un registro existente dentro del módulo ${m}`;
    } else if (a === 'ELIMINAR') {
        message = `El usuario ${u} ${verb} un registro del módulo ${m}`;
    } else if (a === 'ACCESO_DENEGADO') {
        message = `El usuario ${u} ${verb} una sección restringida del sistema`;
    } else if (a === 'GENERAR_REPORTE') {
        message = `El usuario ${u} ${verb} desde el módulo ${m}`;
    } else {
        message = `El usuario ${u} ${verb} el módulo ${m}`;
    }

    message += ` el ${f.getDate()}/${f.getMonth() + 1}/${f.getFullYear()} a las ${timeStr}`;

    if (horaInicio && horaCierre && a !== 'LOGIN' && a !== 'LOGOUT') {
        message += ` (Inicio de sesión: ${formatearHora(horaInicio)} | Cierre: ${formatearHora(horaCierre)})`;
    }

    return message;
}

function formatFechaBitacora(fecha) {
    if (!fecha) return '-';
    const f = parseFecha(fecha);
    if (!f) return String(fecha).replace(/\s*GMT\s*$/i, '').trim() || '-';
    const day = String(f.getDate()).padStart(2, '0');
    const month = String(f.getMonth() + 1).padStart(2, '0');
    const year = f.getFullYear();
    const hours = f.getHours();
    const period = hours >= 12 ? 'PM' : 'AM';
    const hour12 = hours % 12 || 12;
    const minutes = String(f.getMinutes()).padStart(2, '0');
    const seconds = String(f.getSeconds()).padStart(2, '0');
    return `${day}/${month}/${year} · ${hour12}:${minutes}:${seconds} ${period}`;
}

function formatearHora(fecha) {
    if (!fecha) return '-';
    const f = parseFecha(fecha);
    if (!f) return String(fecha).replace(/\s*GMT\s*$/i, '').trim() || '-';
    const hours = f.getHours();
    const period = hours >= 12 ? 'PM' : 'AM';
    const hour12 = hours % 12 || 12;
    const minutes = String(f.getMinutes()).padStart(2, '0');
    const seconds = String(f.getSeconds()).padStart(2, '0');
    return `${hour12}:${minutes}:${seconds} ${period}`;
}

function populateModalDetalle(record) {
    document.getElementById('detalle_id').textContent = record.id_bitacora || '-';
    document.getElementById('detalle_usuario').textContent = record.usuario || '-';
    document.getElementById('detalle_modulo').textContent = record.modulo || '-';
    document.getElementById('detalle_accion').innerHTML = buildAccionBadge(record.accion);
    document.getElementById('detalle_fecha').textContent = formatFechaBitacora(record.fecha);
    document.getElementById('detalle_hora_inicio').textContent = formatearHora(record.hora_inicio_sesion);
    document.getElementById('detalle_hora_cierre').textContent = formatearHora(record.hora_cierre_sesion);

    const descRow = document.getElementById('detalle_descripcion_row');
    descRow.style.display = 'none';

    const msgContainer = document.getElementById('detalle_mensaje_container');
    const msgEl = document.getElementById('detalle_mensaje');
    msgEl.textContent = buildFriendlyMessage(record.usuario, record.accion, record.modulo, record.fecha, record.hora_inicio_sesion, record.hora_cierre_sesion);
    msgContainer.style.display = '';
}

function openDetalleModal(record) {
    populateModalDetalle(record);
    const modalEl = document.getElementById('modalDetalleBitacora');
    if (modalEl) {
        const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();
    }
}

function renderizarBitacoras(registros) {
    const tbody = document.querySelector('#tbody_bitacora');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (registros.length === 0) {
        tbody.innerHTML = '<tr class="fila-vacia"><td colspan="7" class="text-center py-5 text-muted">No hay registros en la bitácora</td></tr>';
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
              ${r.fecha ? formatFechaBitacora(r.fecha) : ' '}
            </td>
            <td style="padding: 0.85rem 1.2rem; font-size:0.83rem; color:#475569;">
              ${r.hora_inicio_sesion ? formatearHora(r.hora_inicio_sesion) : ' '}
            </td>
            <td style="padding: 0.85rem 1.2rem; text-align:center;">
              <button type="button"
                class="btn btn-sm btn-outline-primary btn-detalle-bitacora"
                data-id="${r.id_bitacora || ''}"
                data-usuario="${escapeHtmlAttr(r.usuario || '')}"
                data-modulo="${escapeHtmlAttr(r.modulo || '')}"
                data-accion="${escapeHtmlAttr(r.accion || '')}"
                data-fecha="${escapeHtmlAttr(r.fecha || '')}"
                data-hora-inicio="${escapeHtmlAttr(r.hora_inicio_sesion || '')}"
                data-hora-cierre="${escapeHtmlAttr(r.hora_cierre_sesion || '')}"
                title="Ver detalle del registro">
                <i class="bi bi-eye"></i>
              </button>
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
    // Leer page y per_page desde la URL si existen
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('page')) {
        paginaActualBitacora = parseInt(urlParams.get('page')) || 1;
    }
    if (urlParams.has('per_page')) {
        registrosPorPaginaBitacora = parseInt(urlParams.get('per_page')) || 10;
    }

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
    const page = new URLSearchParams(window.location.search).get('page') || '1';
    const per_page = new URLSearchParams(window.location.search).get('per_page') || '10';

    const params = new URLSearchParams();
    if (usuario) params.set('usuario', usuario);
    if (modulo) params.set('modulo', modulo);
    if (accion) params.set('accion', accion);
    params.set('page', page);
    params.set('per_page', per_page);

    fetch(`/api/obtener-bitacora-json?${params.toString()}`)
        .then(res => res.json())
        .then(data => {
            todasLasBitacoras = Array.isArray(data) ? data : [];
            paginaActualBitacora = parseInt(page) || 1;
            registrosPorPaginaBitacora = parseInt(per_page) || 10;
            busquedaActualBitacora = '';
            const input = document.getElementById('buscarBitacora');
            if (input) input.value = '';
            renderizarBitacoras(todasLasBitacoras);
        })
        .catch(err => console.error('Error cargando bitácora:', err));
}

document.getElementById('tbody_bitacora').addEventListener('click', function(event) {
    const btn = event.target.closest('.btn-detalle-bitacora');
    if (!btn) return;

    const record = {
        id_bitacora: btn.dataset.id || '',
        usuario: btn.dataset.usuario || '',
        modulo: btn.dataset.modulo || '',
        accion: btn.dataset.accion || '',
        fecha: btn.dataset.fecha || '',
        hora_inicio_sesion: btn.dataset.horaInicio || btn.dataset.horaInicioSesion || '',
        hora_cierre_sesion: btn.dataset.horaCierre || btn.dataset.horaCierreSesion || '',
        descripcion: btn.dataset.descripcion || ''
    };
    openDetalleModal(record);
});