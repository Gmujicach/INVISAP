document.getElementById('btnCargarEmpresas').addEventListener('click', function() {
    const tablaCuerpo = document.getElementById('tablaEmpresasCuerpo');
    
    tablaCuerpo.innerHTML = `
        <tr>
            <td colspan="4" class="text-center text-muted py-4">
                <i class="bx bx-loader-alt bx-spin me-2 fs-5 align-middle"></i> 
                Consultando registros de empresas...
            </td>
        </tr>`;

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

            data.forEach((empresa) => {
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


function seleccionarEmpresa(rif, nombre) {
    document.getElementById('empresa_rif').value = rif;
    document.getElementById('empresa_ganadora').value = nombre;

    // Ocultamos modal empresas
    const modalEmpresas = bootstrap.Modal.getOrCreateInstance(document.getElementById('modalEmpresas'));
    modalEmpresas.hide();
    
    // Mostramos nuevamente el modal del formulario
    const elModalContratacion = document.getElementById('modalContratacion');
    if (elModalContratacion) {
        const modalRegistro = bootstrap.Modal.getOrCreateInstance(elModalContratacion);
        modalRegistro.show();
    }
}

// Limpiar la empresa seleccionada
document.getElementById('btn_limpiar_seleccion').addEventListener('click', function() {
    const inputEmpresa = document.getElementById('empresa_ganadora');
    const inputRif = document.getElementById('empresa_rif');
    
    inputEmpresa.value = '';
    inputRif.value = '';
    
    inputEmpresa.classList.remove('is-valid', 'is-invalid');
    inputRif.classList.remove('is-valid', 'is-invalid');
});


// 2. VALIDACIONES EN TIEMPO REAL (INPUTS COPIADOS EXACTAMENTE)

// Validación de Descripción
const descInput = document.getElementById('descripcion');
if (descInput) {
    descInput.addEventListener('input', function() {
        const textarea = this;
        const feedback = document.getElementById('descripcionFeedback');
        const contador = document.getElementById('descripcionContador');
        const longitud = textarea.value.trim().length;

        contador.textContent = `${textarea.value.length} / 100 caracteres`;
        
        if (textarea.value.length === 0) {
            textarea.classList.remove('is-valid', 'is-invalid');
            feedback.classList.add('d-none');
            contador.className = "text-muted ms-auto";
            return;
        }

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
}

// Validación de Número de Contrato
const numContratoInput = document.getElementById('numero_contrato');
if (numContratoInput) {
    numContratoInput.addEventListener('input', function() {
        const input = this;
        input.value = input.value.replace(/[^a-zA-Z0-9\-\*]/g, '');
        const longitud = input.value.trim().length;

        if (longitud === 0) {
            input.classList.remove('is-valid', 'is-invalid');
            return;
        }

        if (longitud < 3) {
            input.classList.add('is-invalid');
            input.classList.remove('is-valid');
        } else {
            input.classList.add('is-valid');
            input.classList.remove('is-invalid');
        }
    });
}

// Validación de Monto
const montoInput = document.getElementById('monto');
if (montoInput) {
    montoInput.addEventListener('input', function() {
        const input = this;
        input.value = input.value.replace(/[^a-zA-Z0-9.,\s]/g, '');
        const longitud = input.value.trim().length;

        if (longitud === 0) {
            input.classList.remove('is-valid', 'is-invalid');
            return;
        }

        if (longitud < 3) {
            input.classList.add('is-invalid');
            input.classList.remove('is-valid');
        } else {
            input.classList.add('is-valid');
            input.classList.remove('is-invalid');
        }
    });
}

// Validación Selects y Fechas al cambiar
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


// ELIMINACIÓN DE REGISTROS (SWEETALERT DELEGADO)
document.addEventListener('click', function(event) {
    const boton = event.target.closest('.btn-eliminar');
    
    if (boton) {
        event.preventDefault();
        const urlEliminar = boton.getAttribute('data-url');

        Swal.fire({
            title: '¿Estás completamente seguro?',
            text: "Esta acción eliminará la contratación por completo y no se puede deshacer.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545', 
            cancelButtonColor: '#6c757d',  
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar',
            reverseButtons: true,
            didOpen: () => { 
                document.querySelector('.swal2-container').style.setProperty('z-index', '9999', 'important'); 
            }
        }).then((result) => {
            if (result.isConfirmed) {
                window.location.href = urlEliminar;
            }
        });
    }
});


// ENVÍO UNIFICADO DEL FORMULARIO
document.getElementById('formContratacion').addEventListener('submit', function(event) {
    event.preventDefault(); 
    event.stopPropagation();

    let hayErrores = false;
    let primerElementoConError = null;

    // EVALUACIÓN ANTES DE ENVIAR
    const descripcionInput = document.getElementById('descripcion');
    if (descripcionInput && descripcionInput.value.trim().length < 5) {
        descripcionInput.classList.add('is-invalid');
        hayErrores = true;
        primerElementoConError = primerElementoConError || descripcionInput;
    }

    const numeroContratoInputSubmit = document.getElementById('numero_contrato');
    if (numeroContratoInputSubmit && numeroContratoInputSubmit.value.trim().length < 3) {
        numeroContratoInputSubmit.classList.add('is-invalid');
        hayErrores = true;
        primerElementoConError = primerElementoConError || numeroContratoInputSubmit;
    }

    const montoInputSubmit = document.getElementById('monto');
    if (montoInputSubmit && montoInputSubmit.value.trim().length < 3) {
        montoInputSubmit.classList.add('is-invalid');
        hayErrores = true;
        primerElementoConError = primerElementoConError || montoInputSubmit;
    }

    const camposAValidar = [
        'tipo_contrato', 'modalidad', 'objeto', 
        'fecha_inicio_procedimiento', 'fecha_adjudicacion', 'fecha_registro'
    ];

    camposAValidar.forEach(id => {
        const elemento = document.getElementById(id);
        if (elemento) {
            if (elemento.value.trim() === "") {
                elemento.classList.add('is-invalid'); 
                hayErrores = true;
                primerElementoConError = primerElementoConError || elemento;
            } else {
                elemento.classList.remove('is-invalid');
                elemento.classList.add('is-valid');
            }
        }
    });

    if (hayErrores) {
        if (primerElementoConError) {
            primerElementoConError.focus();
        }
        return; 
    }

    // PETICIÓN FETCH AL SERVIDOR
    const form = this;
    const btnSubmit = form.querySelector('button[type="submit"]');
    const textoOriginalBtn = btnSubmit.innerHTML;

    btnSubmit.disabled = true;
    btnSubmit.innerHTML = '<i class="bx bx-loader-alt bx-spin"></i> Guardando...';

    const loadersComunes = ['.preloader', '#preloader', '.loader-wrapper', '.loading', '#loader'];
    loadersComunes.forEach(selector => {
        const elementoLoader = document.querySelector(selector);
        if (elementoLoader) {
            elementoLoader.style.setProperty('display', 'none', 'important');
            elementoLoader.style.setProperty('opacity', '0', 'important');
            elementoLoader.style.setProperty('visibility', 'hidden', 'important');
        }
    });

    fetch(form.getAttribute('action'), {
        method: 'POST',
        body: new FormData(form)
    })
    .then(response => {
        if (!response.ok) throw new Error('Error crítico en el servidor');
        return response.json();
    })
    .then(data => {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = textoOriginalBtn;

        if (data.status === 'success') {
            Swal.fire({ 
                icon: 'success', 
                title: '¡Éxito!', 
                text: data.message,
                didOpen: () => { 
                    document.querySelector('.swal2-container').style.setProperty('z-index', '9999', 'important'); 
                }
            }).then(() => {
                window.location.href = '/contrataciones'; 
            });
        } else {
            Swal.fire({ 
                icon: 'error', 
                title: 'Error', 
                text: data.message,
                didOpen: () => { 
                    document.querySelector('.swal2-container').style.setProperty('z-index', '9999', 'important'); 
                }
            });
        }
    })
    .catch(error => {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = textoOriginalBtn;
        console.error('Error capturado en el formulario:', error);
        
        Swal.fire({ 
            icon: 'error', 
            title: 'Error de conexión', 
            text: 'No se pudo procesar la solicitud en el servidor.',
            didOpen: () => { 
                document.querySelector('.swal2-container').style.setProperty('z-index', '9999', 'important'); 
            }
        });
    });
});