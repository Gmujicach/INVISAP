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

// --- NUEVA VALIDACIÓN: NÚMERO DE CONTRATO ---
document.getElementById('numero_contrato').addEventListener('input', function() {
    const input = this;
    
    // 1. Filtrar caracteres no permitidos en tiempo real
    // Solo permite letras (mayúsculas/minúsculas), números, guiones y asteriscos.
    input.value = input.value.replace(/[^a-zA-Z0-9\-\*]/g, '');

    const longitud = input.value.trim().length;

    // 2. Si el campo está vacío, quitamos colores
    if (longitud === 0) {
        input.classList.remove('is-valid', 'is-invalid');
        return;
    }

    // 3. Evaluar la longitud (Mínimo 3)
    if (longitud < 3) {
        input.classList.add('is-invalid'); // Borde rojo
        input.classList.remove('is-valid');
    } else {
        input.classList.add('is-valid');   // Borde verde
        input.classList.remove('is-invalid');
    }
});
// --------------------------------------------


document.getElementById('formContratacion').addEventListener('submit', function(event) {
    event.preventDefault(); // 1. Detenemos la recarga de página

    const form = this;
    const btnSubmit = form.querySelector('button[type="submit"]');
    const textoOriginalBtn = btnSubmit.innerHTML;

    // 2. Estado de carga visual
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = '<i class="bx bx-loader-alt bx-spin"></i> Guardando...';

    // 3. Envío al servidor
    fetch(form.getAttribute('action'), {
        method: 'POST',
        body: new FormData(form)
    })
    .then(response => response.json())
    .then(data => {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = textoOriginalBtn;

        if (data.status === 'success') {
            Swal.fire({ icon: 'success', title: '¡Éxito!', text: data.message }).then(() => {
                window.location.href = '/contrataciones'; // Redirige solo si es exitoso
            });
        } else {
            Swal.fire({ icon: 'error', title: 'Error', text: data.message });
        }
    })
    .catch(error => {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = textoOriginalBtn;
        Swal.fire({ icon: 'error', title: 'Error', text: 'Error de conexión.' });
    });
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

// --- VALIDACIÓN: MONTO EN TIEMPO REAL (PERMITIENDO ESPACIOS) ---
document.getElementById('monto').addEventListener('input', function() {
    const input = this;
    
    // Filtro: Permite letras (a-z), números (0-9), puntos (.), comas (,) y espacios (\s)
    input.value = input.value.replace(/[^a-zA-Z0-9.,\s]/g, '');

    // Medimos la longitud quitando los espacios de los extremos para que no burlen el mínimo
    const longitud = input.value.trim().length;

    // Si está vacío, quitamos colores
    if (longitud === 0) {
        input.classList.remove('is-valid', 'is-invalid');
        return;
    }

    // Evaluar la longitud mínima de 3
    if (longitud < 3) {
        input.classList.add('is-invalid');
        input.classList.remove('is-valid');
    } else {
        input.classList.add('is-valid');
        input.classList.remove('is-invalid');
    }
});

// --- EFECTO VISUAL: SELECTS Y FECHAS AL SELECCIONAR ---
// Esta función pone los campos en verde en cuanto el usuario elige una opción o fecha
const camposGenerales = [
    'tipo_contrato', 'modalidad', 'objeto', 
    'fecha_inicio_procedimiento', 'fecha_adjudicacion', 'fecha_registro'
];

camposGenerales.forEach(id => {
    const elemento = document.getElementById(id);
    if (elemento) {
        elemento.addEventListener('change', function() {
            if (this.value.trim() !== "") {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } else {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
            }
        });
    }
});

// --- ACTUALIZACIÓN DEL EVENTO SUBMIT PARA EVALUAR TODO ---
// Reemplaza tu actual document.getElementById('formContratacion').addEventListener('submit', ...) por este:

document.getElementById('formContratacion').addEventListener('submit', function(event) {
    let hayErrores = false;
    let primerElementoConError = null;

    // 1. Validar descripción (Si existe en esta vista)
    const descripcionInput = document.getElementById('descripcion');
    if (descripcionInput && descripcionInput.value.trim().length < 5) {
        descripcionInput.classList.add('is-invalid');
        hayErrores = true;
        primerElementoConError = primerElementoConError || descripcionInput;
    }

    // 2. Validar número de contrato (Si existe en esta vista)
    const numeroContratoInput = document.getElementById('numero_contrato');
    if (numeroContratoInput && numeroContratoInput.value.trim().length < 3) {
        numeroContratoInput.classList.add('is-invalid');
        hayErrores = true;
        primerElementoConError = primerElementoConError || numeroContratoInput;
    }

    // 3. Validar Monto
    const montoInput = document.getElementById('monto');
    if (montoInput && montoInput.value.trim().length < 3) {
        montoInput.classList.add('is-invalid');
        hayErrores = true;
        primerElementoConError = primerElementoConError || montoInput;
    }

    // 4. Validar Selects y Fechas
    const camposAValidar = [
        'tipo_contrato', 'modalidad', 'objeto', 
        'fecha_inicio_procedimiento', 'fecha_adjudicacion', 'fecha_registro'
    ];

    camposAValidar.forEach(id => {
        const elemento = document.getElementById(id);
        if (elemento) {
            if (elemento.value.trim() === "") {
                elemento.classList.add('is-invalid'); // Borde rojo si no ha seleccionado nada
                hayErrores = true;
                primerElementoConError = primerElementoConError || elemento;
            } else {
                elemento.classList.remove('is-invalid');
                elemento.classList.add('is-valid');
            }
        }
    });

    // Si encontramos algún error, detenemos el envío y hacemos focus en el primer error
    if (hayErrores) {
        event.preventDefault(); 
        if (primerElementoConError) {
            primerElementoConError.focus();
        }
    }
});