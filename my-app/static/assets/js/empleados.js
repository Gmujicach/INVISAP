/**
 * VIEW-CONTROLLED: EMPLEADOS
 * Maneja la lógica de renderizado del Dashboard de Empleados (SPA-style).
 */

function triggerEmpleadosDashboard() {
    const empleados = window.resp_empleadosBD || [];
    
    let rowsHtml = empleados.length > 0 
        ? empleados.map(e => `
            <tr>
              <td>
                <div class="d-flex align-items-center">
                  ${e.foto_empleado 
                    ? `<img src="/static/fotos_empleados/${e.foto_empleado}" alt="foto" style="height:38px; width:38px; border-radius:8px; object-fit:cover" class="me-2 shadow-sm">` 
                    : '<div class="me-2 shadow-sm" style="height:38px; width:38px; border-radius:8px; background:#e9ecef; display:flex; align-items:center; justify-content:center"><i class="bi bi-person-fill text-secondary"></i></div>'}
                  <div>
                    <span class="fw-bold d-block">${e.nombre_empleado} ${e.apellido_empleado}</span>
                    <small class="text-muted">${e.sexo_empleado}</small>
                  </div>
                </div>
              </td>
              <td><span class="text-muted">${e.email_empleado || 'Sin correo'}</span></td>
              <td><span class="fw-semibold text-dark">$${e.salario_empleado}</span></td>
              <td class="text-center">
                <div class="d-flex justify-content-center gap-2">
                  <a href="/editar-empleado/${e.id_empleado}" class="btn btn-warning btn-icon-only btn-sm" title="Editar">
                    <i class="bi bi-pencil-square text-white"></i>
                  </a>
                  <button type="button" onclick="eliminarEmpleadoJS('${e.id_empleado}', '${e.foto_empleado || ''}')" class="btn btn-danger btn-icon-only btn-sm" title="Eliminar">
                    <i class="bi bi-trash3"></i>
                  </button>
                </div>
              </td>
            </tr>`).join('')
        : '<tr><td colspan="4" class="text-center py-4 text-muted">No se encontraron empleados registrados.</td></tr>';

    const content = `
      <div class="dashboard-grid">
        <!-- Formulario de Registro -->
        <div class="dashboard-section">
          <h4 class="fw-bold mb-4" style="color: #08b324;"><i class="bi bi-person-plus-fill me-2"></i>Nuevo Empleado</h4>
          <!-- Se corrige la ruta para que coincida con EmpleadoController -->
          <form action="/empleados/create" method="POST" enctype="multipart/form-data">
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label class="form-label">Nombre</label>
                    <input type="text" name="nombre_empleado" class="form-control" required>
                </div>
                <div class="col-md-6 mb-3">
                    <label class="form-label">Apellido</label>
                    <input type="text" name="apellido_empleado" class="form-control" required>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label class="form-label">Sexo</label>
                    <select name="sexo_empleado" class="form-select" required>
                        <option value="1">Masculino</option>
                        <option value="2">Femenino</option>
                    </select>
                </div>
                <div class="col-md-6 mb-3">
                    <label class="form-label">Salario</label>
                    <input type="text" name="salario_empleado" class="form-control" placeholder="Ej: 2500" required>
                </div>
            </div>
            <div class="mb-3">
                <label class="form-label">Teléfono</label>
                <input type="text" name="telefono_empleado" class="form-control" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Email</label>
                <input type="email" name="email_empleado" class="form-control" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Profesión</label>
                <input type="text" name="profesion_empleado" class="form-control" required>
            </div>
            <div class="mb-4">
                <label class="form-label">Foto de Perfil</label>
                <input type="file" name="foto_empleado" class="form-control" accept="image/*">
            </div>
            <button type="submit" class="btn w-100 text-white shadow-sm" style="background-color: #08b324; font-weight: 500;">
                <i class="bi bi-check-circle me-1"></i> Guardar Empleado
            </button>
          </form>
        </div>

        <!-- Listado Detallado -->
        <div class="dashboard-section">
          <h4 class="fw-bold mb-4" style="color: #08b324;"><i class="bi bi-people-fill me-2"></i>Listado de Empleados</h4>
          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead class="table-light">
                <tr><th>Empleado</th><th>Email</th><th>Salario</th><th class="text-center">Acciones</th></tr>
              </thead>
              <tbody>${rowsHtml}</tbody>
            </table>
          </div>
        </div>
      </div>
    `;
    openDashboard(content);
}

function eliminarEmpleadoJS(id, foto) {
    if (confirm("¿Está seguro que desea eliminar a este empleado de la base de datos?")) {
        // Se corrige la ruta para que coincida con EmpleadoController
        let url = `/empleados/delete/${id}`;
        if (foto && foto !== 'None') url += `/${foto}`;
        window.location.href = url;
    }
}