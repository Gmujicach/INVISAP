/**
 * empleados.js - Módulo para Dashboard SPA de Empleados
 * Maneja la lógica de renderizado dinámico y comunicación con el backend
 * Complementa a empleados_validation.js (formularios independientes)
 */

/**
 * Función principal que renderiza el Dashboard de Empleados (SPA-style)
 * Se dispara desde empleados.html al cargar la página
 */
function triggerEmpleadosDashboard() {
    const empleados = window.resp_empleadosBD || [];
    
    // Generar filas de la tabla con validación de datos y acciones
    let rowsHtml = empleados.length > 0 
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
                                ${e.nombre_empleado.charAt(0).toUpperCase()}
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
                <td class="text-center">
                    <div class="btn-group" role="group">
                        <button type="button" class="btn btn-sm btn-warning" 
                                onclick="editarEmpleadoModal(${e.id_empleados})" 
                                title="Editar">
                            <i class="bi bi-pencil-square"></i>
                        </button>
                        <button type="button" class="btn btn-sm btn-danger" 
                                onclick="eliminarEmpleadoJS(${e.id_empleados})" 
                                title="Desactivar">
                            <i class="bi bi-trash3-fill"></i>
                        </button>
                    </div>
                </td>
              </tr>`;
        }).join('')
        : '<tr><td colspan="7" class="text-center py-5 text-muted"><i class="bi bi-inbox fs-1 d-block mb-2"></i>No se encontraron empleados registrados.</td></tr>';

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
                    <h3 class="text-primary mb-0">${empleados.length}</h3>
                    <small class="text-muted">Total Empleados</small>
                  </div>
                </div>
                <div class="col-6">
                  <h3 class="text-success mb-0">${empleados.filter(e => e.estado == 1).length}</h3>
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
            
            // Recargar página después de 1.5 segundos
            setTimeout(() => {
                window.location.reload();
            }, 1500);
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
 * Función para editar empleado (abre modal o redirige)
 */
function editarEmpleadoModal(id_empleado) {
    // Validar existencia en tiempo real antes de editar
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
 * Borrado Lógico con Confirmación (SweetAlert2 o confirm nativo)
 */
function eliminarEmpleadoJS(id_empleado) {
    if (typeof Swal !== 'undefined') {
        // Usar SweetAlert2 si está disponible
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
                window.location.href = `/empleados/delete/${id_empleado}`;
            }
        });
    } else {
        // Fallback a confirm nativo
        if (confirm("¿Estás seguro de desactivar este empleado? (Borrado Lógico)")) {
            window.location.href = `/empleados/delete/${id_empleado}`;
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
        
    } catch (error) {
        console.error('Error al cargar empleados:', error);
        selectElement.innerHTML = '<option value="" disabled selected>Error al cargar empleados</option>';
    }
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
        editarEmpleadoModal
    };
}