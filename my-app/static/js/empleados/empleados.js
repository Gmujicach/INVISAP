/**
 * empleados.js - Módulo para Dashboard SPA de Empleados
 * Maneja la lógica de renderizado dinámico y comunicación con el backend
 * Complementa a empleados_validation.js (formularios independientes)
 */

/**
 * Genera las filas de la tabla de empleados.
 * Se reutiliza tanto en el render inicial como en el refresco por AJAX,
 * de modo que los botones mantienen siempre el mismo estándar.
 */
function renderFilasEmpleados(empleados) {
    return empleados.length > 0
        ? empleados.map(e => {
            const estadoBadge = e.estado == 1
                ? '<span class="badge bg-success">Activo</span>'
                : '<span class="badge bg-secondary">Inactivo</span>';

            return `
              <tr data-empleado-id="${e.id_empleados}">
                <td><span class="fw-bold">#${e.id_empleados}</span></td>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="avatar avatar-sm me-2">
                            <span class="avatar-initial rounded-circle bg-label-primary">
                                ${String(e.nombre_empleado || '').charAt(0).toUpperCase()}
                            </span>
                        </div>
                        <div>
                            <strong>${e.nombre_empleado}</strong>
                            ${e.cedula_persona ? `<br><small class="text-muted">CI: ${e.cedula_persona}</small>` : ''}
                        </div>
                    </div>
                </td>
                <td><span class="badge bg-label-primary">${e.cargo}</span></td>
                <td><small class="text-muted">${e.gerencia_asignada || 'No asignada'}</small></td>
                <td>${formatearFecha(e.fecha_ingreso)}</td>
                <td>${estadoBadge}</td>
                <td class="acciones">
                    <div class="btn-acciones" style="justify-content:center;">
                        <button type="button" class="btn btn-sm btn-accion btn-accion-ver"
                                onclick="verEmpleadoDetalle(${e.id_empleados})"
                                title="Ver"
                                aria-label="Ver empleado">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-accion btn-accion-editar"
                                onclick="editarEmpleadoModal(${e.id_empleados})"
                                title="Editar"
                                aria-label="Editar empleado">
                            <i class="bi bi-pencil-square"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-accion btn-accion-eliminar"
                                onclick="eliminarEmpleadoJS(${e.id_empleados})"
                                title="Desactivar"
                                aria-label="Desactivar empleado">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
              </tr>`;
        }).join('')
        : '<tr><td colspan="7" class="text-center py-5 text-muted"><i class="bi bi-inbox fs-1 d-block mb-2"></i>No se encontraron empleados registrados.</td></tr>';
}

/**
 * Recupera la fila de un empleado dentro de la tabla del dashboard.
 * La fila se marca con data-empleado-id.
 */
function obtenerFilaEmpleado(id_empleado) {
    return document.querySelector(
        `tr[data-empleado-id="${id_empleado}"], tr[data-id-empleado="${id_empleado}"]`
    );
}

/**
 * Refresca el listado de empleados por AJAX, sin recargar la pagina.
 * Se invoca tras crear, editar o desactivar un empleado.
 */
async function refrescarListadoEmpleados() {
    const cuerpo = document.getElementById('tbodyEmpleadosDashboard');
    if (!cuerpo) {
        window.location.reload();
        return;
    }

    try {
        const response = await fetch('/empleados/api/listar-json?per_page=100', {
            credentials: 'same-origin',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        const data = await response.json();
        if (!data || data.status !== 'success') {
            throw new Error((data && data.message) || 'Respuesta inválida');
        }

        const empleados = data.empleados || [];
        cuerpo.innerHTML = renderFilasEmpleados(empleados);
        window.resp_empleadosBD = empleados;

        actualizarEstadisticasEmpleados(empleados);

        if (window.INVISAP_ESTANDAR_UI) {
            window.INVISAP_ESTANDAR_UI.aplicar(cuerpo);
        }
        filtrarEmpleados();
    } catch (error) {
        console.error('[Empleados] Error al refrescar el listado:', error);
        window.location.reload();
    }
}

/** Actualiza los contadores de total y activos del panel de estadísticas. */
function actualizarEstadisticasEmpleados(empleados) {
    const valores = document.querySelectorAll('#empleadosTotal, #empleadosActivos');
    if (valores.length < 2) return;

    const total = document.getElementById('empleadosTotal');
    const activos = document.getElementById('empleadosActivos');
    if (total) total.textContent = empleados.length;
    if (activos) activos.textContent = empleados.filter(e => e.estado == 1).length;
}

/**
 * Función principal que renderiza el Dashboard de Empleados (SPA-style)
 * Se dispara desde empleados.html al cargar la página
 */
function triggerEmpleadosDashboard() {
    const empleados = window.resp_empleadosBD || [];
    const rowsHtml = renderFilasEmpleados(empleados);

    // Contenido del Dashboard con formulario integrado
    const content = `
      <div class="dashboard-grid">
        <!-- Panel de Registro Rápido -->
        <div class="dashboard-section">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-primary text-white">
              <h5 class="mb-0"><i class="bi bi-person-plus-fill me-2"></i>Registro Rápido de Empleado</h5>
            </div>
            <div class="card-body">
              <form id="formEmpleadoDashboard" onsubmit="registrarEmpleadoFetchDashboard(event)" class="needs-validation" novalidate>
                
                <!-- Datos Laborales -->
                <div class="row g-3">
                  <div class="col-md-12">
                    <label class="form-label fw-medium">
                      <i class="bi bi-person me-1"></i>Nombre Completo
                    </label>
                    <input type="text" name="nombre_empleado" class="form-control" 
                           placeholder="Ej: Juan Carlos Pérez" required 
                           pattern="^[A-ZñÑa-záéíóúÁÉÍÓÚ\s]{3,45}$"
                           title="Solo letras, mínimo 3, máximo 45 caracteres">
                    <div class="invalid-feedback">Nombre inválido (3-45 caracteres).</div>
                  </div>
                  
                  <div class="col-md-6">
                    <label class="form-label fw-medium">
                      <i class="bi bi-briefcase me-1"></i>Cargo
                    </label>
                    <select name="cargo" class="form-select" required>
                      <option value="" disabled selected>Seleccione cargo...</option>
                      <option value="Gerente">Gerente</option>
                      <option value="Inspector">Inspector</option>
                      <option value="Asistente">Asistente</option>
                      <option value="Proyectista">Proyectista</option>
                      <option value="Recepcionista">Recepcionista</option>
                      <option value="Ingeniero">Ingeniero</option>
                      <option value="Coordinador">Coordinador</option>
                      <option value="Operador">Operador</option>
                    </select>
                    <div class="invalid-feedback">Seleccione un cargo.</div>
                  </div>
                  
                  <div class="col-md-6">
                    <label class="form-label fw-medium">
                      <i class="bi bi-calendar-event me-1"></i>Fecha de Ingreso
                    </label>
                    <input type="date" name="fecha_ingreso" class="form-control" required>
                    <div class="invalid-feedback">Fecha obligatoria.</div>
                  </div>
                  
                  <div class="col-md-12">
                    <label class="form-label fw-medium">
                      <i class="bi bi-building me-1"></i>Gerencia Asignada
                    </label>
                    <input type="text" name="gerencia_asignada" class="form-control" 
                           placeholder="Ej: Gerencia de Infraestructura" required
                           pattern="^[A-ZñÑa-záéíóúÁÉÍÓÚ\s]{5,100}$">
                    <div class="invalid-feedback">Gerencia inválida (5-100 caracteres).</div>
                  </div>
                  
                  <div class="col-md-6">
                    <label class="form-label fw-medium">
                      <i class="bi bi-card-text me-1"></i>Cédula
                    </label>
                    <input type="text" name="cedula_empleado" class="form-control" 
                           placeholder="Ej: 12345678" required 
                           pattern="^\\d{7,8}$" minlength="7" maxlength="8">
                    <div class="invalid-feedback">Cédula inválida (7-8 dígitos).</div>
                  </div>
                </div>
                
                <div class="mt-4 d-grid">
                  <button type="submit" class="btn btn-primary" id="btnGuardarDashboard">
                    <i class="bi bi-check-circle me-1"></i>Registrar Empleado
                  </button>
                </div>
              </form>
            </div>
          </div>
          
          <!-- Estadísticas Rápidas -->
          <div class="card border-0 shadow-sm mt-3">
            <div class="card-body">
              <h6 class="text-muted mb-3">Estadísticas</h6>
              <div class="row text-center">
                <div class="col-6">
                  <div class="border-end">
                    <h3 class="text-primary mb-0" id="empleadosTotal">${empleados.length}</h3>
                    <small class="text-muted">Total Empleados</small>
                  </div>
                </div>
                <div class="col-6">
                  <h3 class="text-success mb-0" id="empleadosActivos">${empleados.filter(e => e.estado == 1).length}</h3>
                  <small class="text-muted">Activos</small>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Panel de Listado Detallado -->
        <div class="dashboard-section">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-transparent border-bottom d-flex justify-content-between align-items-center">
              <h5 class="mb-0">
                <i class="bi bi-people-fill me-2 text-primary"></i>Listado de Empleados
              </h5>
              <div class="input-group" style="max-width: 300px;">
                <span class="input-group-text"><i class="bi bi-search"></i></span>
                <input type="text" class="form-control" id="searchEmpleado" 
                       placeholder="Buscar empleado..." onkeyup="filtrarEmpleados()">
              </div>
            </div>
            <div class="card-body p-0">
              <div class="table-responsive">
                <table class="table table-hover align-middle mb-0" id="tablaEmpleadosDashboard">
                  <thead class="table-light">
                    <tr>
                      <th>ID</th>
                      <th>Empleado</th>
                      <th>Cargo</th>
                      <th>Gerencia</th>
                      <th>Ingreso</th>
                      <th>Estado</th>
                      <th class="text-center">Acciones</th>
                    </tr>
                  </thead>
                  <tbody id="tbodyEmpleadosDashboard">
                    ${rowsHtml}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
    
    openDashboard(content);
}

/**
 * Función para formatear fechas de manera legible
 */
function formatearFecha(fecha) {
    if (!fecha) return 'N/A';
    try {
        const date = new Date(fecha);
        const opciones = { year: 'numeric', month: 'short', day: 'numeric' };
        return date.toLocaleDateString('es-ES', opciones);
    } catch (error) {
        return fecha;
    }
}

/**
 * Función para filtrar empleados en tiempo real (búsqueda)
 */
function filtrarEmpleados() {
    const input = document.getElementById('searchEmpleado');
    if (!input) return;
    
    const filter = input.value.toUpperCase();
    const table = document.getElementById('tablaEmpleadosDashboard');
    if (!table) return;
    
    const tr = table.getElementsByTagName('tr');

    for (let i = 1; i < tr.length; i++) {
        const td = tr[i].getElementsByTagName('td');
        let encontrado = false;
        
        for (let j = 0; j < td.length; j++) {
            if (td[j]) {
                const txtValue = td[j].textContent || td[j].innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    encontrado = true;
                    break;
                }
            }
        }
        
        tr[i].style.display = encontrado ? '' : 'none';
    }
}

/**
 * Registro de empleado desde el Dashboard (Fetch/AJAX)
 * Usa la API mejorada /empleados/api/create
 */
async function registrarEmpleadoFetchDashboard(event) {
    event.preventDefault();
    
    const form = event.target;
    
    // Validar formulario HTML5
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        
        const primerCampoInvalido = form.querySelector(':invalid');
        if (primerCampoInvalido) {
            primerCampoInvalido.focus();
        }
        
        mostrarNotificacion('Complete todos los campos correctamente.', 'error');
        return;
    }

    const btnGuardar = document.getElementById('btnGuardarDashboard');
    if (!btnGuardar) return;
    
    const formData = new FormData(form);
    
    // Deshabilitar botón durante el envío
    btnGuardar.disabled = true;
    btnGuardar.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Guardando...';

    try {
        const response = await fetch('/empleados/api/create', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();

        if (result.status === 'success') {
            mostrarNotificacion(result.message, 'success');
            form.reset();
            btnGuardar.disabled = false;
            btnGuardar.innerHTML = '<i class="bi bi-check-circle me-1"></i>Registrar Empleado';
            refrescarListadoEmpleados();
        } else {
            mostrarNotificacion('Error: ' + result.message, 'error');
            btnGuardar.disabled = false;
            btnGuardar.innerHTML = '<i class="bi bi-check-circle me-1"></i>Registrar Empleado';
        }
    } catch (error) {
        console.error('Error al registrar empleado:', error);
        mostrarNotificacion('Error de conexión con el servidor.', 'error');
        btnGuardar.disabled = false;
        btnGuardar.innerHTML = '<i class="bi bi-check-circle me-1"></i>Registrar Empleado';
    }
}

/**
 * Función para editar empleado.
 * Se valida la existencia en tiempo real y se abre el formulario de
 * edición dedicado, que ya incluye la validación del lado del servidor.
 */
function editarEmpleadoModal(id_empleado) {
    fetch(`/empleados/api/validar/${id_empleado}`)
        .then(response => response.json())
        .then(data => {
            if (data.existe) {
                window.location.href = `/empleados/edit/${id_empleado}`;
            } else {
                mostrarNotificacion('El empleado no existe o fue eliminado.', 'error');
            }
        })
        .catch(error => {
            console.error('Error al validar empleado:', error);
            mostrarNotificacion('Error de conexión.', 'error');
        });
}

/**
 * Muestra el detalle del empleado en el modal de la vista.
 * Reutiliza el renderizado definido en empleados.html para que el
 * botón Ver del listado y el del dashboard se comporten igual.
 */
function verEmpleadoDetalle(id_empleado) {
    if (typeof window.mostrarDetalleEmpleado === 'function') {
        const empleados = window.resp_empleadosBD || [];
        const empleado = empleados.find(e => Number(e.id_empleados) === Number(id_empleado));
        if (empleado) {
            window.mostrarDetalleEmpleado(empleado);
            return;
        }
    }
    mostrarNotificacion('No se pudo obtener el detalle del empleado.', 'error');
}

/**
 * Borrado Lógico con Confirmación (SweetAlert2 o confirm nativo)
 */
function eliminarEmpleadoJS(id_empleado) {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            title: '¿Estás seguro?',
            text: "El empleado será desactivado (borrado lógico) y no aparecerá en el listado activo.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Sí, desactivar',
            cancelButtonText: 'Cancelar',
            reverseButtons: true
        }).then((result) => {
            if (result.isConfirmed) {
                fetch(`/empleados/delete/${id_empleado}`)
                    .then(function(response) { return response.json(); })
                    .then(function(data) {
                        if (data && data.status === 'success') {
                            Swal.fire({
                                icon: 'success',
                                title: '¡Éxito!',
                                text: data.message || 'Empleado desactivado correctamente.',
                                timer: 1500,
                                showConfirmButton: false
                            });
                            var row = obtenerFilaEmpleado(id_empleado);
                            if (row) {
                                row.style.transition = 'opacity 0.4s';
                                row.style.opacity = '0';
                                setTimeout(function() { row.remove(); }, 400);
                            }
                            refrescarListadoEmpleados();
                        } else {
                            Swal.fire({
                                icon: 'error',
                                title: 'Error',
                                text: (data && data.message) || 'No se pudo desactivar el empleado.'
                            });
                        }
                    })
                    .catch(function() {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: 'Error de conexión con el servidor.'
                        });
                    });
            }
        });
    } else {
        if (confirm("¿Estás seguro de desactivar este empleado? (Borrado Lógico)")) {
            fetch(`/empleados/delete/${id_empleado}`)
                .then(function(response) { return response.json(); })
                .then(function(data) {
                    if (data && data.status === 'success') {
                        alert('Empleado desactivado correctamente.');
                        var row = obtenerFilaEmpleado(id_empleado);
                        if (row) {
                            row.style.transition = 'opacity 0.4s';
                            row.style.opacity = '0';
                            setTimeout(function() { row.remove(); }, 400);
                        }
                        refrescarListadoEmpleados();
                    } else {
                        alert((data && data.message) || 'No se pudo desactivar el empleado.');
                    }
                })
                .catch(function() {
                    alert('Error de conexión');
                });
        }
    }
}

/**
 * Función de notificación (compatible con SweetAlert2 o Toast personalizado)
 */
function mostrarNotificacion(mensaje, tipo = 'info') {
    if (typeof Swal !== 'undefined') {
        const iconos = {
            'success': 'success',
            'error': 'error',
            'warning': 'warning',
            'info': 'info'
        };
        
        Swal.fire({
            icon: iconos[tipo] || 'info',
            title: tipo === 'success' ? '¡Éxito!' : tipo === 'error' ? 'Error' : 'Información',
            text: mensaje,
            timer: tipo === 'success' ? 2000 : undefined,
            showConfirmButton: tipo !== 'success'
        });
    } else if (typeof createToast === 'function') {
        // Si existe función createToast global
        createToast(mensaje, tipo);
    } else {
        // Fallback a alert nativo
        alert(mensaje);
    }
}

/**
 * Función para obtener empleados por cargo (usado por otros módulos)
 * Ejemplo: obtenerEmpleadosPorCargo('Inspector').then(inspectores => {...})
 */
async function obtenerEmpleadosPorCargo(cargo) {
    try {
        const response = await fetch(`/empleados/api/por-cargo/${cargo}`);
        const result = await response.json();
        
        if (result.status === 'success') {
            return result.empleados;
        } else {
            console.error('Error al obtener empleados por cargo:', result.message);
            return [];
        }
    } catch (error) {
        console.error('Error de conexión:', error);
        return [];
    }
}

/**
 * Función auxiliar para cargar empleados dinámicamente (usado por otros módulos)
 * Ejemplo de uso en módulo de inspecciones:
 * 
 * cargarEmpleadosPorCargo('Inspector', 'selectInspector');
 */
async function cargarEmpleadosPorCargo(cargo, selectId) {
    const selectElement = document.getElementById(selectId);
    if (!selectElement) {
        console.error(`Elemento select con ID '${selectId}' no encontrado`);
        return;
    }
    
    try {
        const empleados = await obtenerEmpleadosPorCargo(cargo);
        
        // Limpiar opciones existentes (excepto la primera)
        selectElement.innerHTML = '<option value="" disabled selected>Seleccione...</option>';
        
        // Agregar empleados como opciones
        empleados.forEach(emp => {
            const option = document.createElement('option');
            option.value = emp.id_empleados;
            option.textContent = `${emp.nombre_empleado} - ${emp.gerencia_asignada}`;
            selectElement.appendChild(option);
        });
        
        // Habilitar el select
        selectElement.disabled = false;
        
        if (typeof ValidacionesComunes !== 'undefined' && ValidacionesComunes.marcarSelectInvalido) {
            ValidacionesComunes.marcarSelectInvalido(selectElement);
        }
        
    } catch (error) {
        console.error('Error al cargar empleados:', error);
        selectElement.innerHTML = '<option value="" disabled selected>Error al cargar empleados</option>';
        if (typeof ValidacionesComunes !== 'undefined' && ValidacionesComunes.marcarSelectInvalido) {
            ValidacionesComunes.marcarSelectInvalido(selectElement);
        }
    }
}

/**
 * Paginación AJAX del listado de empleados (empleados.html)
 * Actualiza solo la tabla y los controles de paginación sin recargar la vista.
 */
function initPaginacionEmpleados() {
    const paginacion = document.querySelector('.pagination');
    if (!paginacion) return;

    paginacion.addEventListener('click', async function(e) {
        const link = e.target.closest('a.page-link');
        if (!link) return;

        e.preventDefault();

        const url = link.getAttribute('href');
        if (!url || url === '#') return;

        try {
            const response = await fetch(url, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            if (!response.ok) throw new Error('Error en la respuesta del servidor');

            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            const nuevaTabla = doc.querySelector('#tablaEmpleados');
            const nuevaInfo = doc.querySelector('#infoRegistros');
            const nuevaPaginacion = doc.querySelector('.pagination');

            const tbody = document.getElementById('tbodyEmpleados');
            if (nuevaTabla && tbody) {
                const nuevoTbody = nuevaTabla.querySelector('tbody');
                if (nuevoTbody) {
                    tbody.innerHTML = nuevoTbody.innerHTML;
                }
            }

            if (nuevaInfo) {
                const infoActual = document.getElementById('infoRegistros');
                if (infoActual) infoActual.outerHTML = nuevaInfo.outerHTML;
            }

            if (nuevaPaginacion && paginacion) {
                paginacion.outerHTML = nuevaPaginacion.outerHTML;
                initPaginacionEmpleados();
            }
        } catch (error) {
            console.error('Error al cargar la página:', error);
            mostrarNotificacion('No se pudo cargar la página solicitada.', 'error');
        }
    });
}

if (typeof window !== 'undefined') {
    window.initPaginacionEmpleados = initPaginacionEmpleados;
}

/**
 * Exportar funciones para uso global (si se usa módulos ES6)
 * Si no usas módulos, estas funciones ya están en el scope global
 */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        triggerEmpleadosDashboard,
        registrarEmpleadoFetchDashboard,
        eliminarEmpleadoJS,
        obtenerEmpleadosPorCargo,
        cargarEmpleadosPorCargo,
        filtrarEmpleados,
        editarEmpleadoModal,
        initPaginacionEmpleados
    };
}