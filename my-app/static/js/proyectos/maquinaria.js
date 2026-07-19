let paginaActual = 1;

document.addEventListener('DOMContentLoaded', function() {
    const formRegistrar = document.getElementById('formRegistrarMaquinaria');
    const nombreInput = document.getElementById('nombre_maquinaria');
    const tipoSelect = document.getElementById('tipo_maquinaria');

    function marcarInvalido(input, mensaje) {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
        
        let feedback = input.parentElement.querySelector('.invalid-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback d-block';
            input.parentElement.appendChild(feedback);
        }
        feedback.innerText = mensaje;
    }

    function marcarValido(input) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        const feedback = input.parentElement.querySelector('.invalid-feedback');
        if (feedback) feedback.remove();
    }

    if (formRegistrar) {
        if (nombreInput) {
            nombreInput.addEventListener('input', function() {
                const valor = nombreInput.value.trim();
                if (valor.length >= 3) {
                    marcarValido(nombreInput);
                } else {
                    marcarInvalido(nombreInput, 'El nombre debe tener al menos 3 caracteres');
                }
            });
        }

        if (tipoSelect) {
            tipoSelect.addEventListener('change', function() {
                if (tipoSelect.value) {
                    marcarValido(tipoSelect);
                } else {
                    marcarInvalido(tipoSelect, 'Debe seleccionar un tipo de maquinaria');
                }
            });
        }

        formRegistrar.addEventListener('submit', function(e) {
            e.preventDefault();
            let tieneErrores = false;

            if (!nombreInput || !nombreInput.value.trim() || nombreInput.value.trim().length < 3) {
                if (nombreInput) marcarInvalido(nombreInput, 'El nombre es requerido y debe tener al menos 3 caracteres');
                tieneErrores = true;
            }

            if (!tipoSelect || !tipoSelect.value) {
                if (tipoSelect) marcarInvalido(tipoSelect, 'Debe seleccionar un tipo de maquinaria');
                tieneErrores = true;
            }

            if (tieneErrores) {
                const primerError = formRegistrar.querySelector('.is-invalid');
                if (primerError) primerError.focus();
                return;
            }

            registrarMaquinariaAjax(formRegistrar);
        });
    }

    document.addEventListener('click', function(e) {
        if (e.target.closest('.btn-eliminar-maquinaria')) {
            const btn = e.target.closest('.btn-eliminar-maquinaria');
            const id = btn.getAttribute('data-id');
            eliminarMaquinariaAjax(id, btn.closest('tr'));
        }
    });

    // Cargar primera página al iniciar
    cargarPaginaMaquinarias(1);
});

function cargarPaginaMaquinarias(page) {
    const tablaCuerpo = document.getElementById('tablaMaquinaria');
    const paginacion = document.getElementById('paginacionMaquinaria');
    paginaActual = page;
    
    tablaCuerpo.innerHTML = `
        <tr>
            <td colspan="4" class="text-center text-muted py-4">
                <i class="bx bx-loader-alt bx-spin me-2 fs-5 align-middle"></i> 
                Cargando registros...
            </td>
        </tr>`;
    
    fetch(`/api/maquinaria/listar?page=${page}&per_page=10`, {
        method: 'GET',
        headers: {
            'Accept': 'application/json'
        }
    })
    .then(response => response.text())
    .then(text => {
        try {
            const result = JSON.parse(text);
            if (result.success) {
                renderizarTabla(result.data);
                renderizarPaginacion(result.page, result.total_pages);
            } else {
                tablaCuerpo.innerHTML = `<tr><td colspan="4" class="text-center text-danger py-4">Error al cargar datos.</td></tr>`;
            }
        } catch (e) {
            throw new Error(`Respuesta no JSON: ${text}`);
        }
    })
    .catch(error => {
        console.error('Error al cargar maquinarias:', error);
        tablaCuerpo.innerHTML = `
            <tr>
                <td colspan="4" class="text-center text-danger py-4">
                    <i class="bx bx-error-circle me-1 fs-5 align-middle"></i> 
                    Error al cargar los datos: ${error.message}
                </td>
            </tr>`;
    });
}

function renderizarTabla(maquinarias) {
    const tablaCuerpo = document.getElementById('tablaMaquinaria');
    
    if (!maquinarias || maquinarias.length === 0) {
        tablaCuerpo.innerHTML = `<tr><td colspan="4" class="text-center text-muted py-4">No hay maquinarias registradas.</td></tr>`;
        return;
    }
    
    let contenidoHTML = '';
    maquinarias.forEach((m, index) => {
        const contador = (paginaActual - 1) * 10 + index + 1;
        contenidoHTML += `
            <tr>
                <td>${contador}</td>
                <td>${m.nombre_maquinaria.toUpperCase()}</td>
                <td><span class="badge bg-dark">${m.tipo_maquinaria}</span></td>
                <td class="text-center">
                    <a class="btn btn-sm btn-outline-warning" href="/editar-maquinaria/${m.id_maquinaria}" title="Editar">
                        <i class="bx bx-edit-alt"></i> Editar
                    </a>
                    <button class="btn btn-sm btn-outline-danger btn-eliminar-maquinaria" data-id="${m.id_maquinaria}" title="Eliminar">
                        <i class="bx bx-trash"></i>
                    </button>
                </td>
            </tr>`;
    });
    
    tablaCuerpo.innerHTML = contenidoHTML;
}

function renderizarPaginacion(pagina, totalPaginas) {
    const paginacion = document.getElementById('paginacionMaquinaria');
    
    if (totalPaginas <= 1) {
        paginacion.innerHTML = '';
        return;
    }
    
    let contenidoHTML = '';
    
    // Botón anterior
    if (pagina > 1) {
        contenidoHTML += `<li class="page-item"><a class="page-link" href="#" onclick="cargarPaginaMaquinarias(${pagina - 1}); return false;">Anterior</a></li>`;
    } else {
        contenidoHTML += `<li class="page-item disabled"><span class="page-link">Anterior</span></li>`;
    }
    
    // Páginas numeradas
    for (let i = 1; i <= totalPaginas; i++) {
        if (i === pagina) {
            contenidoHTML += `<li class="page-item active"><span class="page-link">${i}</span></li>`;
        } else {
            contenidoHTML += `<li class="page-item"><a class="page-link" href="#" onclick="cargarPaginaMaquinarias(${i}); return false;">${i}</a></li>`;
        }
    }
    
    // Botón siguiente
    if (pagina < totalPaginas) {
        contenidoHTML += `<li class="page-item"><a class="page-link" href="#" onclick="cargarPaginaMaquinarias(${pagina + 1}); return false;">Siguiente</a></li>`;
    } else {
        contenidoHTML += `<li class="page-item disabled"><span class="page-link">Siguiente</span></li>`;
    }
    
    paginacion.innerHTML = contenidoHTML;
}

function registrarMaquinariaAjax(form) {
    const formData = new FormData(form);
    const nombreVal = formData.get('nombre_maquinaria');
    const tipoVal = formData.get('tipo_maquinaria');
    const nombreInput = document.getElementById('nombre_maquinaria');
    const tipoSelect = document.getElementById('tipo_maquinaria');
    
    fetch(form.action, {
        method: 'POST',
        body: formData
    })
    .then(async response => {
        const text = await response.text();
        try {
            return { ok: response.ok, data: JSON.parse(text) };
        } catch (e) {
            throw new Error(`Respuesta no JSON: ${text}`);
        }
    })
    .then(result => {
        if (result.ok && result.data.success) {
            // Recargar la página actual para mostrar el nuevo registro
            if (result.data.restaurada) {
                // La maquinaria fue restaurada, recargar la página
                cargarPaginaMaquinarias(paginaActual);
            } else {
                // Nuevo registro, recargar página 1
                cargarPaginaMaquinarias(1);
            }
            form.reset();
            
            if (nombreInput) nombreInput.classList.remove('is-valid', 'is-invalid');
            if (tipoSelect) {
                tipoSelect.classList.remove('is-valid', 'is-invalid');
                tipoSelect.value = '';
            }
            
            Swal.fire('¡Éxito!', result.data.message, 'success');
        } else {
            Swal.fire('Error', result.data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        const errorMsg = error.message || 'Error desconocido';
        Swal.fire('Error', `No se pudo registrar la maquinaria.\n${errorMsg}`, 'error');
    });
}

function eliminarMaquinariaAjax(id, fila) {
    Swal.fire({
        title: '¿Estás seguro?',
        text: '¡No podrás revertir esta acción!',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/api/maquinaria/${id}/eliminar`, { method: 'DELETE' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Recargar la página actual para actualizar la tabla
                    cargarPaginaMaquinarias(paginaActual);
                    Swal.fire('Eliminado', data.message, 'success');
                } else {
                    Swal.fire('Error', data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                Swal.fire('Error', 'No se pudo conectar con el servidor', 'error');
            });
        }
    });
}