/**
 * VIEW-CONTROLLED: EMPLEADOS
 * Maneja la lógica de renderizado del Dashboard de Empleados (SPA-style).
 */

function triggerEmpleadosDashboard() {
    const empleados = window.resp_empleadosBD || [];
    
    let rowsHtml = empleados.length > 0 
        ? empleados.map(e => `
          <tr>
            <td><span class="fw-bold">${e.id_empleados}</span></td>
            <td>${e.nombre_empleado}</td>
            <td><span class="badge bg-label-primary">${e.cargo}</span></td>
            <td><small class="text-muted">${e.gerencia_asignada}</small></td>
            <td>${e.fecha_ingreso}</td>
          </tr>`).join('')
        : '<tr><td colspan="5" class="text-center py-4 text-muted">No se encontraron empleados registrados.</td></tr>';

    const content = `
      <div class="dashboard-grid">
        <!-- Formulario de Registro -->
        <div class="dashboard-section">
          <h4 class="fw-bold mb-4" style="color: #08b324;"><i class="bi bi-person-plus-fill me-2"></i>Nuevo Empleado</h4>
          <form id="formEmpleadoDashboard" onsubmit="registrarEmpleadoFetch(event)" class="needs-validation" novalidate>
            <div class="row">
                <div class="col-md-12 mb-3">
                    <label class="form-label">Nombre del Empleado</label>
                    <input type="text" name="nombre_empleado" class="form-control" placeholder="Ej: Juan Pérez" required pattern="^[A-ZñÑa-záéíóúÁÉÍÓÚ\s]{3,45}$">
                </div>
                <div class="col-md-6 mb-3">
                    <label class="form-label">Fecha de Ingreso</label>
                    <input type="date" name="fecha_ingreso" class="form-control" required>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label class="form-label">Cargo</label>
                    <select name="cargo" class="form-select" required>
                        <option value="" disabled selected>Seleccione...</option>
                        <option value="Gerente">Gerente</option>
                        <option value="Inspector">Inspector</option>
                        <option value="Asistente">Asistente</option>
                        <option value="Proyectista">Proyectista</option>
                    </select>
                </div>
            </div>
          </form>
        </div>

        <!-- Listado Detallado -->
        <div class="dashboard-section">
          <h4 class="fw-bold mb-4" style="color: #08b324;"><i class="bi bi-people-fill me-2"></i>Listado de Empleados</h4>
          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead class="table-light">
                <tr><th>ID</th><th>Nombre</th><th>Cargo</th><th>Gerencia</th><th>Ingreso</th></tr>
              </thead>
              <tbody>${rowsHtml}</tbody>
            </table>
          </div>
        </div>
      </div>
    `;
    openDashboard(content);
}

/**
 * Lógica Fetch para Registro (Sin recarga de página)
 */
async function registrarEmpleadoFetch(event) {
    event.preventDefault();
    const form = event.target;
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return;
    }

    const formData = new FormData(form);
    try {
        const response = await fetch('/empleados/create', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        if (result.status === 'success') {
            // Notificación (createToast debe estar disponible globalmente)
            window.location.reload(); 
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error("Error:", error);
    }
}

/**
 * Borrado Lógico con Confirmación
 */
function eliminarEmpleadoJS(id) {
    if (confirm("¿Estás seguro de desactivar este empleado? (Borrado Lógico)")) {
        window.location.href = `/empleados/delete/${id}`;
    }
}