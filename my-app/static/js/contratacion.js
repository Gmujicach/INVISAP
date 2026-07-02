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

    const modalEmpresas = bootstrap.Modal.getOrCreateInstance(document.getElementById('modalEmpresas'));
    modalEmpresas.hide();
    
    const elModalContratacion = document.getElementById('modalContratacion');
    if (elModalContratacion) {
        const modalRegistro = bootstrap.Modal.getOrCreateInstance(elModalContratacion);
        modalRegistro.show();
    }
}

document.getElementById('btn_limpiar_seleccion').addEventListener('click', function() {
    const inputEmpresa = document.getElementById('empresa_ganadora');
    const inputRif = document.getElementById('empresa_rif');
    
    inputEmpresa.value = '';
    inputRif.value = '';
    
    inputEmpresa.classList.remove('is-valid', 'is-invalid');
    inputRif.classList.remove('is-valid', 'is-invalid');
});


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


document.addEventListener('click', function(event) {
    const boton = event.target.closest('.btn-eliminar');
    
    if (boton) {
        event.preventDefault();
        const urlEliminar = boton.getAttribute('data-url');
        const filaTabla = boton.closest('tr');

        Swal.fire({
            title: '¿Estás completamente seguro?',
            text: "Esta acción no se puede deshacer.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545', 
            cancelButtonColor: '#6c757d',  
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar',
            reverseButtons: true
        }).then((result) => {
            if (result.isConfirmed) {
                fetch(urlEliminar, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.exito) {
                        filaTabla.remove(); 
                        Swal.fire({
                            icon: 'success',
                            title: '¡Eliminado!',
                            text: data.mensaje,
                            timer: 2000,
                            showConfirmButton: false
                        });
                    } else {
                        Swal.fire('Error', data.mensaje, 'error');
                    }
                })
                .catch(error => Swal.fire('Error', 'No se pudo conectar con el servidor.', 'error'));
            }
        });
    }
});


document.getElementById('formContratacion').addEventListener('submit', function(event) {
    event.preventDefault(); 
    event.stopPropagation();

    let hayErrores = false;
    let primerError = null;

    const descripcion = document.getElementById('descripcion');
    if (descripcion && descripcion.value.trim().length < 5) {
        descripcion.classList.add('is-invalid');
        hayErrores = true;
        primerError = primerError || descripcion;
    }

    const numContrato = document.getElementById('numero_contrato');
    if (numContrato && numContrato.value.trim().length < 3) {
        numContrato.classList.add('is-invalid');
        hayErrores = true;
        primerError = primerError || numContrato;
    }

    const monto = document.getElementById('monto');
    if (monto && monto.value.trim().length < 3) {
        monto.classList.add('is-invalid');
        hayErrores = true;
        primerError = primerError || monto;
    }

    const camposAValidar = ['tipo_contrato', 'modalidad', 'objeto', 'fecha_inicio_procedimiento', 'fecha_adjudicacion', 'fecha_registro'];
    camposAValidar.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            if (el.value.trim() === "") {
                el.classList.add('is-invalid'); 
                hayErrores = true;
                primerError = primerError || el;
            } else {
                el.classList.remove('is-invalid');
                el.classList.add('is-valid');
            }
        }
    });

    if (hayErrores) {
        if (primerError) primerError.focus();
        return; 
    }

    const form = this;
    const btnSubmit = form.querySelector('button[type="submit"]');
    const textoBtn = btnSubmit.innerHTML;

    btnSubmit.disabled = true;
    btnSubmit.innerHTML = '<i class="bx bx-loader-alt bx-spin"></i> Guardando...';

    fetch(form.getAttribute('action'), {
        method: 'POST',
        body: new FormData(form)
    })
    .then(response => response.json())
    .then(data => {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = textoBtn;

        if (data.status === 'success') {
            
            const modalEl = document.getElementById('modalContratacion');
            if (modalEl) {
                const modalInstancia = bootstrap.Modal.getInstance(modalEl);
                if (modalInstancia) modalInstancia.hide();
            }

            Swal.fire({ 
                icon: 'success', 
                title: '¡Éxito!', 
                text: data.message,
                timer: 2000,
                showConfirmButton: false
            }).then(() => {
                
                if (data.redirect) {
                    window.location.href = data.redirect;
                } else {
                    form.reset();
                    form.querySelectorAll('.is-valid, .is-invalid').forEach(el => el.classList.remove('is-valid', 'is-invalid'));
                    
                    fetch(window.location.href)
                    .then(res => res.text())
                    .then(html => {
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(html, 'text/html');
                        const nuevaTabla = doc.querySelector('.table-responsive').innerHTML;
                        document.querySelector('.table-responsive').innerHTML = nuevaTabla;
                    });
                }
            });

        } else {
            Swal.fire({ 
                icon: 'error', 
                title: 'Error', 
                text: data.message,
                target: document.getElementById('modalContratacion')
            });
        }
    })
    .catch(error => {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = textoBtn;
        Swal.fire({ 
            icon: 'error', 
            title: 'Error de conexión', 
            text: 'No se pudo procesar la solicitud.',
            target: document.getElementById('modalContratacion')
        });
    });
});