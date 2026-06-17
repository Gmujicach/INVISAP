document.getElementById('btnCargarEmpresas').addEventListener('click', function() {
    const tablaCuerpo = document.getElementById('tablaEmpresasCuerpo');
    
    // Mostramos un loader mientras carga
    tablaCuerpo.innerHTML = `
        <tr>
            <td colspan="4" class="text-center text-muted py-4">
                <i class="bx bx-loader-alt bx-spin me-2 fs-5 align-middle"></i> 
                Consultando registros de empresas...
            </td>
        </tr>`;

    // IMPORTANTE: Asegúrate de tener esta ruta creada en tu app.py o routes 
    // que devuelva un JSON con las empresas. Ejemplo: [{'rif': 'J-12345', 'nombre_empresa': 'Constructora XYZ'}]
    fetch('/api/obtener-empresas-json')
        .then(response => {
            if (!response.ok) throw new Error('Error en el servidor');
            return response.json();
        })
        .then(data => {
            let contenidoHTML = ''; 

            if (data.length === 0) {
                tablaCuerpo.innerHTML = `<tr><td colspan="4" class="text-center text-muted py-4">No hay empresas registradas.</td></tr>`;
                return;
            }

            data.forEach((empresa, index) => {
                contenidoHTML += `
                    <tr>
                        <td class="fw-bold">${empresa.rif || '—'}</td>
                        <td class="text-uppercase">${empresa.nombre_empresa || '—'}</td>
                        <td class="text-center">
                            <button type="button" class="btn btn-outline-primary btn-sm" 
                                    onclick="seleccionarEmpresa('${(empresa.rif || '').replace(/'/g, "\\'")}', '${(empresa.nombre_empresa || '').replace(/'/g, "\\'")}')">
                                <i class="bx bx-check"></i> Seleccionar
                            </button>
                        </td>
                    </tr>
                `;
            });
            tablaCuerpo.innerHTML = contenidoHTML; 
        })
        .catch(error => {
            console.error('Error al capturar empresas:', error);
            tablaCuerpo.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center text-danger py-4">
                        <i class="bx bx-error-circle me-1 fs-5 align-middle"></i> 
                        Error al conectar con el servidor. Por favor, verifique su ruta de la API.
                    </td>
                </tr>`;
        });
});

// Función que inserta los datos en el formulario principal y cierra el modal secundario
function seleccionarEmpresa(rif, nombre) {
    // Pegamos los valores en los inputs de solo lectura
    document.getElementById('empresa_rif').value = rif;
    document.getElementById('empresa_ganadora').value = nombre;

    // Ocultamos el modal de empresas
    const modalEmpresas = bootstrap.Modal.getOrCreateInstance(document.getElementById('modalEmpresas'));
    modalEmpresas.hide();
    
    // Mostramos nuevamente el modal del formulario principal
    const modalRegistro = bootstrap.Modal.getOrCreateInstance(document.getElementById('modalContratacion'));
    modalRegistro.show();
}

function seleccionarEmpresa(rif, nombre) {
    // Pegamos los valores en los inputs de solo lectura
    document.getElementById('empresa_rif').value = rif;
    document.getElementById('empresa_ganadora').value = nombre;

    // Ocultamos el modal de empresas
    const modalEmpresas = bootstrap.Modal.getOrCreateInstance(document.getElementById('modalEmpresas'));
    modalEmpresas.hide();
    
    // Mostramos nuevamente el modal del formulario principal
    const modalRegistro = bootstrap.Modal.getOrCreateInstance(document.getElementById('modalContratacion'));
    modalRegistro.show();
}

//Validaciones

document.getElementById('descripcion').addEventListener('input', function() {
    const textarea = this;
    const feedback = document.getElementById('descripcionFeedback');
    const contador = document.getElementById('descripcionContador');
    const longitud = textarea.value.trim().length;

    //Actualizar el contador de texto en la esquina derecha
    contador.textContent = `${textarea.value.length} / 100 caracteres`;
    // vacío
    if (textarea.value.length === 0) {
        textarea.classList.remove('is-valid', 'is-invalid');
        feedback.classList.add('d-none');
        contador.className = "text-muted ms-auto";
        return;
    }

    // Validar si cumple con el mínimo de 5 letras
    if (longitud < 5) {
        textarea.classList.add('is-invalid');
        textarea.classList.remove('is-valid');
        feedback.classList.remove('d-none');
        feedback.className = "text-danger fw-bold";
        feedback.textContent = "❌ Descripcion minima de 5 caracteres.";

        contador.className = "text-danger fw-bold ms-auto";
    } else {
        textarea.classList.add('is-valid');
        textarea.classList.remove('is-invalid');
        
        feedback.classList.remove('d-none');
        feedback.className = "text-success fw-bold";
        feedback.textContent = "✅";
        
        contador.className = "text-muted ms-auto";
    }
});


document.getElementById('formContratacion').addEventListener('submit', function(event) {
    const descripcionInput = document.getElementById('descripcion');
    const longitud = descripcionInput.value.trim().length;

    if (longitud < 5) {
        event.preventDefault(); 
        
        descripcionInput.classList.add('is-invalid');
        
        descripcionInput.focus();
    }
});

document.addEventListener('click', function(event) {
    // Buscamos si el clic se hizo en el botón de eliminar o en su ícono interno
    const boton = event.target.closest('.btn-eliminar');
    
    if (boton) {
        // Evitamos que el enlace actúe por defecto
        event.preventDefault();
        
        // Obtenemos la URL de Flask que guardamos en el HTML
        const urlEliminar = boton.getAttribute('data-url');

        // Disparamos la alerta estética de SweetAlert2
        Swal.fire({
            title: '¿Estás completamente seguro?',
            text: "Esta acción eliminará la contratación por completo y no se puede deshacer.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545', // Rojo de Bootstrap para peligro
            cancelButtonColor: '#6c757d',  // Gris de Bootstrap para cancelar
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar',
            reverseButtons: true // Pone el botón de confirmar a la derecha
        }).then((result) => {
            // Si el usuario presionó el botón de "Sí, eliminar"
            if (result.isConfirmed) {
                // Redirigimos a la ruta de Flask para que ejecute el backend
                window.location.href = urlEliminar;
            }
        });
    }
});


document.getElementById('btn_limpiar_seleccion').addEventListener('click', function() {
    const inputEmpresa = document.getElementById('empresa_ganadora');
    const inputRif = document.getElementById('empresa_rif');
    
    // Vaciamos ambos campos de un solo golpe
    inputEmpresa.value = '';
    inputRif.value = '';
    
    // Limpiamos los estilos visuales de validación de Bootstrap si existieran
    inputEmpresa.classList.remove('is-valid', 'is-invalid');
    inputRif.classList.remove('is-valid', 'is-invalid');
});