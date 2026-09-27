/* ============================================================
   seguridad.js — Módulo "Permisos por Rol"
   Fetch API (sin recarga) + SweetAlert2 para confirmaciones.
   Maneja tres secciones: Roles, Módulos y Asignación de Permisos.
   ============================================================ */

// ---------- Utilidades ----------
function alertaSeguridad(mensaje, tipo, contenedorId) {
  const el = document.getElementById(contenedorId);
  if (!el) return;
  el.className = `alert alert-${tipo} d-block`;
  el.textContent = mensaje;
}
function ocultarAlertaSeguridad(contenedorId) {
  const el = document.getElementById(contenedorId);
  if (el) el.className = 'alert d-none';
}
function estadoBadge(estado) {
  return estado == 1
    ? '<span class="badge bg-success">Activo</span>'
    : '<span class="badge bg-secondary">Inactivo</span>';
}
function tipoBadge(tipo) {
  const color = tipo === 'Transaccional' ? 'bg-info' : (tipo === 'Enlace' ? 'bg-secondary' : 'bg-success');
  return `<span class="badge ${color}">${tipo}</span>`;
}

function generarSkeletonRow(celdas) {
  let html = '<div class="seguridad-skeleton"><div class="seguridad-skeleton-row">';
  for (let i = 0; i < celdas.length; i++) {
    const cls = celdas[i];
    if (cls === 'circle') {
      html += '<span class="seguridad-skeleton-circle"></span>';
    } else {
      html += '<span class="seguridad-skeleton-bar ' + cls + '"></span>';
    }
  }
  html += '</div></div>';
  return html;
}
function showSkeleton(tbodyId, colSpan, rows) {
  const tb = document.getElementById(tbodyId);
  if (!tb) return;
  let html = '';
  rows.forEach(row => {
    html += '<tr><td colspan="' + colSpan + '">' + generarSkeletonRow(row) + '</td></tr>';
  });
  tb.innerHTML = html;
}
function hideSkeleton(tbodyId) {
  const tb = document.getElementById(tbodyId);
  if (tb) tb.innerHTML = '';
}

const ICONOS_MODULO = [
  'bi-folder','bi-folder2','bi-person','bi-people','bi-people-fill',
  'bi-person-bounding-box','bi-house','bi-building','bi-gear','bi-tools',
  'bi-clipboard','bi-clipboard-check','bi-card-list','bi-list-task','bi-images',
  'bi-newspaper','bi-bar-chart','bi-bar-chart-line','bi-graph-up','bi-truck',
  'bi-briefcase','bi-exclamation-triangle','bi-arrow-up','bi-shield',
  'bi-journal-text','bi-table','bi-envelope','bi-bell','bi-lock','bi-key',
  'bi-cart','bi-calendar','bi-clock','bi-geo-alt','bi-wrench','bi-tag',
  'bi-star','bi-heart','bi-check-circle','bi-x-circle','bi-plus-circle',
  'bi-pencil','bi-eye','bi-search','bi-download','bi-upload','bi-trash',
  'bi-recycle','bi-link','bi-box','bi-bag','bi-moon','bi-sun'
];

function populateIconPicker() {
  const grid = document.getElementById('icono_dropdown_grid');
  if (!grid) return;
  grid.innerHTML = '';
  ICONOS_MODULO.forEach(function(icono) {
    const col = document.createElement('div');
    col.className = 'col-4 col-sm-3 col-md-2';
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'btn btn-outline-secondary w-100 icon-grid-item py-2';
    btn.dataset.icon = icono;
    btn.innerHTML = '<i class="bi ' + icono + '" style="font-size:1.2rem;"></i>';
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      document.getElementById('icono_modulo').value = icono;
      document.getElementById('icono_dropdown_preview').className = 'bi ' + icono + ' me-2';
      document.getElementById('icono_dropdown_text').textContent = icono;
      document.querySelectorAll('.icon-grid-item').forEach(function(b) { b.classList.remove('active'); });
      btn.classList.add('active');
      bootstrap.Dropdown.getInstance(document.querySelector('.icon-picker-dropdown > button')).hide();
    });
    col.appendChild(btn);
    grid.appendChild(col);
  });
}

// ============================================================
// ROLES
// ============================================================
function cargarRoles() {
  showSkeleton('cuerpoRoles', 5, [
    ['circle','sm','lg','sm','sm'],
    ['circle','sm','lg','sm','sm'],
    ['circle','sm','lg','sm','sm']
  ]);
  fetch('/api/seguridad/roles/listar')
    .then(r => r.json())
    .then(data => renderTablaRoles(data))
    .catch(() => Swal.fire('Error', 'No se pudieron cargar los roles.', 'error'));
}
function renderTablaRoles(roles) {
  const tb = document.getElementById('cuerpoRoles');
  tb.innerHTML = '';
  document.getElementById('contadorRoles').textContent = roles.length + ' roles';
  if (!roles.length) {
    tb.innerHTML = `<tr><td colspan="5" class="text-center py-4 text-muted">No hay roles registrados.</td></tr>`;
    return;
  }
  roles.forEach(r => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${r.id_rol}</td>
      <td><strong>${r.nombre}</strong></td>
      <td>${r.descripcion || '—'}</td>
      <td>${estadoBadge(r.estado)}</td>
     <td class="acciones">
     <div class="btn-acciones" style="justify-content:center;">
     <button class="btn btn-sm btn-accion btn-accion-ver" onclick="verRol(${r.id_rol})" title="Ver rol" aria-label="Ver rol"><i class="bi bi-eye"></i></button>
     <button class="btn btn-sm btn-accion btn-accion-editar" onclick="editarRol(${r.id_rol})" title="Editar rol" aria-label="Editar rol"><i class="bi bi-pencil-square"></i></button>
          <button class="btn btn-sm btn-accion btn-accion-eliminar" onclick="eliminarRol(${r.id_rol})" title="Eliminar rol" aria-label="Eliminar rol"><i class="bi bi-trash"></i></button>
        </div>
      </td>`;
    tb.appendChild(tr);
  });
}
function resetFormRol() {
  document.getElementById('modalRolTitle').textContent = 'Nuevo Rol';
  document.getElementById('id_rol').value = '';
  document.getElementById('nombre_rol').value = '';
  document.getElementById('descripcion_rol').value = '';
  document.getElementById('estado_rol').checked = true;
  document.getElementById('formRol').classList.remove('was-validated');
  ocultarAlertaSeguridad('mensajeRol');
  restaurarCamposModal('rol', ['id_rol', 'nombre_rol', 'descripcion_rol', 'estado_rol'], 'btnGuardarRol');
}

/**
 * Devuelve un modal al modo editable tras haberlo mostrado en solo lectura.
 */
function restaurarCamposModal(clave, campos, idBoton) {
  campos.forEach(function (campo) {
    const el = document.getElementById(campo);
    if (el) el.disabled = false;
  });
  const btn = document.getElementById(idBoton);
  if (btn) btn.style.display = '';
  return clave;
}
/**
 * Boton Ver: carga el registro en su modal y deja el formulario en solo
 * lectura, de modo que el usuario puede consultarlo sin arriesgar cambios.
 */
function verRol(id) {
  fetch(`/api/seguridad/roles/obtener/${id}`)
    .then(r => r.json())
    .then(d => {
      if (!d) return Swal.fire('Aviso', 'Rol no encontrado.', 'warning');
      editarRol(id, true);
    })
    .catch(() => Swal.fire('Error', 'No se pudo cargar el rol.', 'error'));
}

function editarRol(id, soloLectura) {
  fetch(`/api/seguridad/roles/obtener/${id}`)
    .then(r => r.json())
    .then(d => {
      if (!d) return Swal.fire('Aviso', 'Rol no encontrado.', 'warning');
      document.getElementById('modalRolTitle').textContent = soloLectura ? 'Detalle del Rol' : 'Editar Rol';
      document.getElementById('id_rol').value = d.id_rol;
      document.getElementById('nombre_rol').value = d.nombre;
      document.getElementById('descripcion_rol').value = d.descripcion || '';
      document.getElementById('estado_rol').checked = d.estado == 1;
      ocultarAlertaSeguridad('mensajeRol');

      ['id_rol', 'nombre_rol', 'descripcion_rol', 'estado_rol'].forEach(campo => {
        const el = document.getElementById(campo);
        if (el) el.disabled = !!soloLectura;
      });
      const btn = document.getElementById('btnGuardarRol');
      if (btn) btn.style.display = soloLectura ? 'none' : '';

      new bootstrap.Modal(document.getElementById('modalRol')).show();
    })
    .catch(() => Swal.fire('Error', 'No se pudo cargar el rol.', 'error'));
}
function eliminarRol(id) {
  Swal.fire({
    title: '¿Desea eliminar este rol?',
    text: 'Se eliminará este rol del sistema.',
    icon: 'warning', showCancelButton: true,
    confirmButtonText: 'Sí, eliminar', cancelButtonText: 'Cancelar'
  }).then(res => {
    if (!res.isConfirmed) return;
    fetch(`/api/seguridad/roles/eliminar/${id}`, { method: 'DELETE' })
      .then(r => r.json())
      .then(d => {
        if (d.success) { Swal.fire('Listo', 'Rol eliminado exitosamente', 'success'); cargarRoles(); cargarSelectRol(); localStorage.setItem('invisap_roles_updated', Date.now()); }
        else Swal.fire('Error', d.message, 'error');
      });
  });
}
function guardarRol() {
  const form = document.getElementById('formRol');
  if (!form.checkValidity()) { form.classList.add('was-validated'); return; }
  const id = document.getElementById('id_rol').value;
  const nombre = document.getElementById('nombre_rol').value.trim();
  if (nombre.toLowerCase() === 'super usuario') {
    fetch('/api/seguridad/roles/listar')
      .then(r => r.json())
      .then(roles => {
        const existe = roles.some(r => (r.nombre || '').trim().toLowerCase() === 'super usuario' && (id ? parseInt(r.id_rol) !== parseInt(id) : true));
        if (existe) {
          Swal.fire('Restricción', 'Ya existe un Super Usuario activo. No se permite crear ni asignar este rol a otro usuario.', 'warning');
          return;
        }
        enviarGuardadoRol(id, nombre);
      })
      .catch(() => Swal.fire('Error', 'No se pudo validar el rol.', 'error'));
    return;
  }
  enviarGuardadoRol(id, nombre);
}
function enviarGuardadoRol(id, nombre) {
  const payload = {
    nombre: nombre,
    descripcion: document.getElementById('descripcion_rol').value.trim(),
    estado: document.getElementById('estado_rol').checked ? 1 : 0
  };
  const url = id ? `/api/seguridad/roles/actualizar/${id}` : '/api/seguridad/roles/registrar';
  fetch(url, {
    method: id ? 'PUT' : 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  .then(r => r.json())
  .then(d => {
    if (d.success) {
      Swal.fire('Listo', d.message, 'success');
      bootstrap.Modal.getInstance(document.getElementById('modalRol')).hide();
      cargarRoles(); cargarSelectRol(); localStorage.setItem('invisap_roles_updated', Date.now());
    } else alertaSeguridad(d.message, 'danger', 'mensajeRol');
  })
  .catch(() => alertaSeguridad('Error de conexión.', 'danger', 'mensajeRol'));
}

// ============================================================
// MÓDULOS
// ============================================================
function cargarModulos() {
  showSkeleton('cuerpoModulos', 6, [
    ['circle','sm','lg','sm','sm','sm'],
    ['circle','sm','lg','sm','sm','sm'],
    ['circle','sm','lg','sm','sm','sm']
  ]);
  fetch('/api/seguridad/modulos/listar')
    .then(r => r.json())
    .then(data => renderTablaModulos(data))
    .catch(() => Swal.fire('Error', 'No se pudieron cargar los módulos.', 'error'));
}
function renderTablaModulos(modulos) {
  const tb = document.getElementById('cuerpoModulos');
  tb.innerHTML = '';
  document.getElementById('contadorModulos').textContent = modulos.length + ' módulos';
  if (!modulos.length) {
    tb.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-muted">No hay módulos registrados.</td></tr>`;
    return;
  }
  modulos.forEach(m => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${m.id_modulo}</td>
      <td><strong>${m.nombre}</strong></td>
      <td><code>${m.url}</code></td>
      <td>${tipoBadge(m.tipo)}</td>
      <td>${estadoBadge(m.estado)}</td>
     <td class="acciones">
     <div class="btn-acciones" style="justify-content:center;">
     <button class="btn btn-sm btn-accion btn-accion-ver" onclick="verModulo(${m.id_modulo})" title="Ver módulo" aria-label="Ver módulo"><i class="bi bi-eye"></i></button>
     <button class="btn btn-sm btn-accion btn-accion-editar" onclick="editarModulo(${m.id_modulo})" title="Editar módulo" aria-label="Editar módulo"><i class="bi bi-pencil-square"></i></button>
          <button class="btn btn-sm btn-accion btn-accion-eliminar" onclick="eliminarModulo(${m.id_modulo})" title="Eliminar módulo" aria-label="Eliminar módulo"><i class="bi bi-trash"></i></button>
        </div>
      </td>`;
    tb.appendChild(tr);
  });
}
function resetFormModulo() {
  document.getElementById('modalModuloTitle').textContent = 'Nuevo Módulo';
  document.getElementById('id_modulo').value = '';
  document.getElementById('nombre_modulo').value = '';
  document.getElementById('url_modulo').value = '';
  document.getElementById('url_modulo').readOnly = false;
  document.getElementById('url_modulo').title = '';
  document.getElementById('descripcion_modulo').value = '';
  document.getElementById('tipo_modulo').value = 'CRUD';
  document.getElementById('icono_modulo').value = '';
  document.getElementById('icono_dropdown_preview').className = 'bi bi-folder me-2';
  document.getElementById('icono_dropdown_text').textContent = 'Selecciona icono del módulo';
  document.getElementById('orden_modulo').value = '0';
  document.getElementById('estado_modulo').checked = true;
  document.getElementById('formModulo').classList.remove('was-validated');
  ocultarAlertaSeguridad('mensajeModulo');
  restaurarCamposModal('modulo',
    ['id_modulo', 'nombre_modulo', 'descripcion_modulo', 'tipo_modulo', 'orden_modulo', 'estado_modulo'],
    'btnGuardarModulo');
  document.querySelectorAll('.icon-grid-item, #icono_dropdown_toggle').forEach(function (el) {
    el.disabled = false;
  });
}
/** Boton Ver del módulo: mismo modal en modo solo lectura. */
function verModulo(id) {
  editarModulo(id, true);
}

function editarModulo(id, soloLectura) {
  fetch(`/api/seguridad/modulos/obtener/${id}`)
    .then(r => r.json())
    .then(d => {
      if (!d) return Swal.fire('Aviso', 'Módulo no encontrado.', 'warning');
      document.getElementById('modalModuloTitle').textContent = soloLectura ? 'Detalle del Módulo' : 'Editar Módulo';
      document.getElementById('id_modulo').value = d.id_modulo;
      document.getElementById('nombre_modulo').value = d.nombre;
      document.getElementById('url_modulo').value = d.url;
      document.getElementById('url_modulo').readOnly = true;
      document.getElementById('url_modulo').title = 'La URL no se puede modificar después de crear el módulo.';
      document.getElementById('descripcion_modulo').value = d.descripcion || '';
      document.getElementById('tipo_modulo').value = d.tipo;
      document.getElementById('icono_modulo').value = d.icono || '';
      if (d.icono) {
        document.getElementById('icono_dropdown_preview').className = 'bi ' + d.icono + ' me-2';
        document.getElementById('icono_dropdown_text').textContent = d.icono;
      } else {
        document.getElementById('icono_dropdown_preview').className = 'bi bi-folder me-2';
        document.getElementById('icono_dropdown_text').textContent = 'Selecciona icono del módulo';
      }
      document.getElementById('orden_modulo').value = d.orden || 0;
      document.getElementById('estado_modulo').checked = d.estado == 1;
      document.querySelectorAll('.icon-grid-item').forEach(function(b) { b.classList.remove('active'); });
      if (d.icono) {
        const match = document.querySelector('.icon-grid-item[data-icon="' + d.icono + '"]');
        if (match) match.classList.add('active');
      }
      ocultarAlertaSeguridad('mensajeModulo');

      if (soloLectura) {
        ['id_modulo', 'nombre_modulo', 'descripcion_modulo', 'tipo_modulo', 'orden_modulo', 'estado_modulo']
          .forEach(campo => {
            const el = document.getElementById(campo);
            if (el) el.disabled = true;
          });
        document.querySelectorAll('.icon-grid-item, #icono_dropdown_toggle').forEach(function (el) {
          el.disabled = true;
        });
        const btn = document.getElementById('btnGuardarModulo');
        if (btn) btn.style.display = 'none';
      }

      new bootstrap.Modal(document.getElementById('modalModulo')).show();
    })
    .catch(() => Swal.fire('Error', 'No se pudo cargar el módulo.', 'error'));
}
function eliminarModulo(id) {
  Swal.fire({
    title: '¿Desea eliminar este módulo?', text: 'Se eliminará del sistema.',
    icon: 'warning', showCancelButton: true,
    confirmButtonText: 'Sí, eliminar', cancelButtonText: 'Cancelar'
  }).then(res => {
    if (!res.isConfirmed) return;
    fetch(`/api/seguridad/modulos/eliminar/${id}`, { method: 'DELETE' })
      .then(r => r.json())
      .then(d => {
        if (d.success) { Swal.fire('Listo', 'Módulo eliminado exitosamente', 'success'); cargarModulos(); }
        else Swal.fire('Error', d.message, 'error');
      });
  });
}
function guardarModulo() {
  const form = document.getElementById('formModulo');
  if (!form.checkValidity()) { form.classList.add('was-validated'); return; }
  const id = document.getElementById('id_modulo').value;
  const payload = {
    nombre: document.getElementById('nombre_modulo').value.trim(),
    descripcion: document.getElementById('descripcion_modulo').value.trim(),
    url: document.getElementById('url_modulo').value.trim(),
    tipo: document.getElementById('tipo_modulo').value,
    icono: document.getElementById('icono_modulo').value.trim(),
    orden: parseInt(document.getElementById('orden_modulo').value || 0, 10),
    estado: document.getElementById('estado_modulo').checked ? 1 : 0
  };
  const url = id ? `/api/seguridad/modulos/actualizar/${id}` : '/api/seguridad/modulos/registrar';
  fetch(url, {
    method: id ? 'PUT' : 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  .then(r => r.json())
  .then(d => {
    if (d.success) {
      Swal.fire('Listo', d.message, 'success');
      bootstrap.Modal.getInstance(document.getElementById('modalModulo')).hide();
      cargarModulos();
    } else alertaSeguridad(d.message, 'danger', 'mensajeModulo');
  })
  .catch(() => alertaSeguridad('Error de conexión.', 'danger', 'mensajeModulo'));
}

// ============================================================
// PERMISOS POR ROL
// ============================================================
function cargarSelectRol() {
  fetch('/api/seguridad/roles/listar')
    .then(r => r.json())
    .then(roles => {
      const sel = document.getElementById('selectRol');
      sel.innerHTML = '';
      const filtered = Array.isArray(roles) ? roles.filter(r => (r.nombre || '').trim().toLowerCase() !== 'super usuario') : [];
      filtered.forEach(r => {
        const opt = document.createElement('option');
        opt.value = r.id_rol;
        opt.textContent = r.nombre;
        sel.appendChild(opt);
      });
      if (filtered.length) cargarPermisos();
    })
    .catch(() => {});
}
function cargarPermisos() {
  const idRol = document.getElementById('selectRol').value;
  document.getElementById('selectUsuariosPorRol').value = '';
  window.permisosObjetivo = { tipo: 'rol', id: idRol };
  if (!idRol) {
    showSkeleton('cuerpoPermisos', 5, [
      ['lg','sm','sm','sm','sm'],
      ['lg','sm','sm','sm','sm']
    ]);
    return;
  }
  showSkeleton('cuerpoPermisos', 5, [
    ['lg','sm','sm','sm','sm'],
    ['lg','sm','sm','sm','sm']
  ]);
  fetch(`/api/seguridad/permisos/obtener/${idRol}`)
    .then(r => r.json())
    .then(data => renderTablaPermisos(data))
    .catch(() => Swal.fire('Error', 'No se pudieron cargar los permisos.', 'error'));
}
function cargarPermisosUsuario(idUsuario) {
  if (!idUsuario) {
    cargarPermisos();
    return;
  }
  window.permisosObjetivo = { tipo: 'usuario', id: idUsuario };
  showSkeleton('cuerpoPermisos', 5, [
    ['lg','sm','sm','sm','sm'], ['lg','sm','sm','sm','sm']
  ]);
  const idRol = document.getElementById('selectRol').value;
  Promise.all([
    fetch(`/api/seguridad/usuarios/${idUsuario}/permisos`).then(r => r.json()),
    fetch(`/api/seguridad/permisos/obtener/${idRol}`).then(r => r.json())
  ])
    .then(([excepciones, heredados]) => {
      const porModulo = {};
      (Array.isArray(excepciones) ? excepciones : []).forEach(p => { porModulo[p.id_modulo] = p; });
      const efectivos = (Array.isArray(heredados) ? heredados : []).map(p => ({
        ...p, ...(porModulo[p.id_modulo] || {})
      }));
      renderTablaPermisos(efectivos);
    })
    .catch(() => Swal.fire('Error', 'No se pudieron cargar los permisos del usuario.', 'error'));
}
function renderTablaPermisos(filas) {
  const tb = document.getElementById('cuerpoPermisos');
  tb.innerHTML = '';
  if (!filas.length) {
    tb.innerHTML = `<tr><td colspan="5" class="text-center py-4 text-muted">No hay módulos disponibles.</td></tr>`;
    return;
  }
  filas.forEach(f => {
    const tr = document.createElement('tr');
    const chk = (val, name) =>
      `<td class="text-center"><input class="form-check-input perm-check" type="checkbox" data-id="${f.id_modulo}" data-campo="${name}" ${val ? 'checked' : ''}></td>`;
    tr.innerHTML = `
      <td><i class="bi ${f.icono || 'bi-grid'} me-2 text-primary"></i><strong>${f.nombre}</strong> <small class="text-muted">${f.url}</small></td>
      ${chk(f.puede_ver, 'puede_ver')}
      ${chk(f.puede_crear, 'puede_crear')}
      ${chk(f.puede_editar, 'puede_editar')}
      ${chk(f.puede_eliminar, 'puede_eliminar')}`;
    tb.appendChild(tr);
  });
}
function guardarPermisos() {
  const objetivo = window.permisosObjetivo || {
    tipo: 'rol', id: document.getElementById('selectRol').value
  };
  const idRol = document.getElementById('selectRol').value;
  if (!idRol) return Swal.fire('Aviso', 'Seleccione un rol.', 'warning');
  const checks = document.querySelectorAll('#cuerpoPermisos .perm-check');
  const permisos = {};
  checks.forEach(c => {
    const id = c.getAttribute('data-id');
    const campo = c.getAttribute('data-campo');
    if (!permisos[id]) permisos[id] = { id_modulo: parseInt(id, 10), puede_ver: 0, puede_crear: 0, puede_editar: 0, puede_eliminar: 0 };
    permisos[id][campo] = c.checked ? 1 : 0;
  });
  const endpoint = objetivo.tipo === 'usuario'
    ? '/api/seguridad/usuarios/permisos/guardar'
    : '/api/seguridad/permisos/guardar';
  const body = objetivo.tipo === 'usuario'
    ? { id_usuario: parseInt(objetivo.id, 10), permisos: Object.values(permisos) }
    : { id_rol: parseInt(objetivo.id, 10), permisos: Object.values(permisos) };
  fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'same-origin',
    body: JSON.stringify(body)
  })
  .then(async r => {
    const data = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(data.message || `Error HTTP ${r.status}`);
    return data;
  })
  .then(d => {
    if (d.success) {
      Swal.fire('Listo', d.message, 'success').then(() => {
        // El módulo ya sabe reconstruir sus tablas por AJAX: recargamos
        // los listados afectados en vez de recargar la página completa.
        if (typeof cargarRoles === 'function') cargarRoles();
        if (typeof cargarModulos === 'function') cargarModulos();
        const selRol = document.getElementById('selectRol');
        if (selRol && selRol.value && typeof cargarPermisos === 'function') {
          cargarPermisos(selRol.value);
        }
      });
    }
    else Swal.fire('Error', d.message, 'error');
  })
  .catch(error => Swal.fire('Error', error.message || 'Error de conexión.', 'error'));
}

// ============================================================
// BÚSQUEDA RÁPIDA + INIT
// ============================================================
function filaFiltro(inputId, cuerpoId) {
  const filtro = document.getElementById(inputId).value.toLowerCase();
  document.querySelectorAll(`#${cuerpoId} tr`).forEach(fila => {
    fila.style.display = fila.textContent.toLowerCase().includes(filtro) ? '' : 'none';
  });
}

document.addEventListener('DOMContentLoaded', function () {
  cargarRoles();
  cargarModulos();
  cargarSelectRol();
  populateIconPicker();

  document.getElementById('btnGuardarRol').addEventListener('click', guardarRol);
  document.getElementById('btnGuardarModulo').addEventListener('click', guardarModulo);
  document.getElementById('btnGuardarPermisos').addEventListener('click', guardarPermisos);
  document.getElementById('selectRol').addEventListener('change', cargarPermisos);
  document.getElementById('selectUsuariosPorRol').addEventListener('change', function () {
    cargarPermisosUsuario(this.value);
  });
  document.getElementById('buscarRol').addEventListener('keyup', () => filaFiltro('buscarRol', 'cuerpoRoles'));
  document.getElementById('buscarModulo').addEventListener('keyup', () => filaFiltro('buscarModulo', 'cuerpoModulos'));

});
