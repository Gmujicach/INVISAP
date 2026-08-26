document.addEventListener('DOMContentLoaded', function() {
    console.log("Sistema de Empresas cargado.");

    // ==========================================
    // MÓDULO DE PAGINACIÓN Y BÚSQUEDA
    // ==========================================
    const tabla = document.getElementById('tablaEmpresas');
    const tbody = tabla ? tabla.querySelector('tbody') : null;
    let filas = tbody ? Array.from(tbody.querySelectorAll('tr')).filter(tr => tr.id !== 'filaVacia') : [];
    
    const filasPorPagina = 8;
    let paginaActual = 1;
    let filasFiltradas = [...filas];

    const buscador = document.getElementById('customBuscador');
    const selectorColumna = document.getElementById('columnaBusqueda');
    const listaPaginacion = document.getElementById('listaPaginacion');
    const infoPaginacion = document.getElementById('infoPaginacion');

    function actualizarTabla() {
        if (!tbody || filas.length === 0) return;

        const textoBusqueda = buscador.value.toLowerCase().trim();
        const columna = selectorColumna.value;

        // 1. Filtrar filas
        filasFiltradas = filas.filter(fila => {
            if (textoBusqueda === '') return true;
            
            if (columna === 'all') {
                return fila.innerText.toLowerCase().includes(textoBusqueda);
            } else {
                const celda = fila.cells[parseInt(columna)];
                return celda && celda.innerText.toLowerCase().includes(textoBusqueda);
            }
        });

        // 2. Calcular paginación
        const totalPaginas = Math.ceil(filasFiltradas.length / filasPorPagina) || 1;
        if (paginaActual > totalPaginas) paginaActual = totalPaginas;

        const inicio = (paginaActual - 1) * filasPorPagina;
        const fin = inicio + filasPorPagina;

        // 3. Aplicar visibilidad
        filas.forEach(fila => fila.style.display = 'none'); // Ocultar todas primero
        filasFiltradas.slice(inicio, fin).forEach(fila => fila.style.display = ''); // Mostrar las de la página

        // 4. Actualizar UI
        renderizarPaginacion(totalPaginas);
        if (infoPaginacion) {
            const total = filasFiltradas.length;
            const mostrandoInicio = total === 0 ? 0 : inicio + 1;
            const mostrandoFin = Math.min(fin, total);
            infoPaginacion.innerHTML = `Mostrando <strong>${mostrandoInicio} a ${mostrandoFin}</strong> de ${total} registros`;
        }
    }

    function renderizarPaginacion(totalPaginas) {
        if (!listaPaginacion) return;
        listaPaginacion.innerHTML = '';

        if (totalPaginas <= 1) return; // No mostrar paginación si hay 1 sola página

        // Botón Anterior
        const liAnt = document.createElement('li');
        liAnt.className = `page-item ${paginaActual === 1 ? 'disabled' : ''}`;
        liAnt.innerHTML = `<a class="page-link" href="#" data-page="${paginaActual - 1}"><i class="bi bi-chevron-left"></i></a>`;
        listaPaginacion.appendChild(liAnt);

        // Números de página
        for (let i = 1; i <= totalPaginas; i++) {
            const li = document.createElement('li');
            li.className = `page-item ${paginaActual === i ? 'active' : ''}`;
            li.innerHTML = `<a class="page-link" href="#" data-page="${i}">${i}</a>`;
            listaPaginacion.appendChild(li);
        }

        // Botón Siguiente
        const liSig = document.createElement('li');
        liSig.className = `page-item ${paginaActual === totalPaginas ? 'disabled' : ''}`;
        liSig.innerHTML = `<a class="page-link" href="#" data-page="${paginaActual + 1}"><i class="bi bi-chevron-right"></i></a>`;
        listaPaginacion.appendChild(liSig);

        // Eventos de click en paginación
        listaPaginacion.querySelectorAll('.page-link').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const nuevaPagina = parseInt(this.getAttribute('data-page'));
                if (nuevaPagina >= 1 && nuevaPagina <= totalPaginas) {
                    paginaActual = nuevaPagina;
                    actualizarTabla();
                }
            });
        });
    }

    // Escuchadores del buscador
    if (buscador && selectorColumna) {
        buscador.addEventListener('input', () => {
            paginaActual = 1;
            actualizarTabla();
        });
        selectorColumna.addEventListener('change', () => {
            paginaActual = 1;
            buscador.value = ''; // Limpiar búsqueda al cambiar filtro
            actualizarTabla();
        });
    }

    // Inicializar tabla si hay datos
    if (filas.length > 0) {
        actualizarTabla();
    }


    // ==========================================
    // LÓGICA EXISTENTE: ELIMINACIÓN
    // ==========================================
    const botonesEliminar = document.querySelectorAll('.btn-eliminar');
    
    botonesEliminar.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const urlEliminar = this.getAttribute('data-url');
            const filaTabla = this.closest('tr'); 
            
            Swal.fire({
                title: '¿Estás seguro?',
                text: "Esta acción no se puede deshacer.",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Sí, eliminar'
            }).then((result) => {
                if (result.isConfirmed) {
                    
                    fetch(urlEliminar)
                    .then(response => response.json())
                    .then(data => {
                        if(data.exito) {
                            filaTabla.remove(); 
                            
                            // NUEVO: Actualizar arreglo de filas y repaginar tras eliminar
                            filas = filas.filter(f => f !== filaTabla);
                            actualizarTabla();
                            
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
                    .catch(error => {
                        console.error('Error:', error);
                        Swal.fire('Error crítico', 'No se pudo conectar con el servidor.', 'error');
                    });
                }
            });
        });
    });

    // ==========================================
    // LÓGICA EXISTENTE: FORMULARIO
    // ==========================================
    const formulario = document.getElementById('formRegistroEmpresa') || document.getElementById('formEditarEmpresa');
    if (formulario) {
        
        // RIF
        const inputRifFinal = document.getElementById('rif_final');
        if (inputRifFinal && inputRifFinal.value) {
            let valorRif = inputRifFinal.value.trim().toUpperCase(); 
            
            const tipo = document.getElementById('tipo_rif');
            const num = document.getElementById('numero_rif');

            if (valorRif.includes('-')) {
                const partesRif = valorRif.split('-');
                if (tipo) tipo.value = partesRif[0];
                if (num) num.value = partesRif[1];
            } 
            else if (valorRif.length > 1) {
                if (tipo) tipo.value = valorRif.charAt(0);
                if (num) num.value = valorRif.substring(1);
            }
        }

        // TELÉFONO
        const inputTelFinal = document.getElementById('telefono_final');
        if (inputTelFinal && inputTelFinal.value) {
            let soloNumeros = inputTelFinal.value.replace(/\D/g, '');
            if (soloNumeros.length >= 7) {
                const pref = document.getElementById('prefijo_telefono');
                const num = document.getElementById('numero_telefono');
                if(pref) pref.value = soloNumeros.substring(0, 4);
                if(num) num.value = soloNumeros.substring(4);
            }
        }

        // ANTES DE ENVIAR AJAX
        formulario.addEventListener('submit', function(e) {
            e.preventDefault();

            const prefTel = document.getElementById('prefijo_telefono');
            const numTel = document.getElementById('numero_telefono');
            const telFinal = document.getElementById('telefono_final');
            if(prefTel && numTel && telFinal) {
                telFinal.value = prefTel.value + '-' + numTel.value;
            }

            const tipoRif = document.getElementById('tipo_rif');
            const numRif = document.getElementById('numero_rif');
            const rifFinal = document.getElementById('rif_final');
            if (tipoRif && numRif && rifFinal) {
                rifFinal.value = tipoRif.value + '-' + numRif.value;
            }

            const formData = new FormData(this);
            
            fetch(this.action, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json()) 
            .then(data => {
                if (data.exito) {
                    Swal.fire({
                        icon: 'success',
                        title: '¡Listo!',
                        text: data.mensaje,
                        timer: 2000,
                        showConfirmButton: false
                    }).then(() => {
                        window.location.href = '/lista-empresas'; 
                    });
                } else {
                    Swal.fire({
                        icon: data.categoria === 'error' ? 'error' : 'warning',
                        title: 'Oops...',
                        text: data.mensaje
                    });
                }
            })
            .catch(error => {
                console.error("Error en la petición AJAX:", error);
                Swal.fire('Error crítico', 'No se pudo comunicar con el servidor.', 'error');
            });
        });
    }

    //VALIDACIÓN VISUAL
    ['numero_rif', 'numero_telefono'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('input', function() {
                this.value = this.value.replace(/[^0-9]/g, '');
            });
        }
    });

    const domicilioInput = document.querySelector('input[name="domicilio_fiscal"]');
    if (domicilioInput) {
        domicilioInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^A-Za-z0-9áéíóúÁÉÍÓÚñÑüÜ\s.,\-#\/()]/g, '');
        });
    }

    // ==========================================
    // LÓGICA: VERIFICACIÓN DE REQUISITOS LEGALES
    // ==========================================
    const modalRequisitosEl = document.getElementById('modalRequisitos');
    if (modalRequisitosEl) {
        const modalRequisitos = new bootstrap.Modal(modalRequisitosEl);
        const checkboxRequisito = document.getElementById('checkboxCumpleRequisitos');
        const btnGuardarRequisito = document.getElementById('btnGuardarRequisito');
        const requisitoRifInput = document.getElementById('requisitoRifEmpresa');
        const requisitoNombreEl = document.getElementById('requisitoNombreEmpresa');
        const requisitoFeedback = document.getElementById('requisitoFeedback');

        document.querySelectorAll('.btn-ver-requisitos').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const rif = this.getAttribute('data-rif');
                const nombre = this.getAttribute('data-nombre');
                const cumple = this.getAttribute('data-cumple') === '1';

                requisitoRifInput.value = rif;
                requisitoNombreEl.textContent = nombre;
                checkboxRequisito.checked = cumple;
                requisitoFeedback.classList.add('d-none');

                modalRequisitos.show();
            });
        });

        btnGuardarRequisito.addEventListener('click', function() {
            const rif = requisitoRifInput.value;
            const valor = checkboxRequisito.checked ? 1 : 0;

            btnGuardarRequisito.disabled = true;
            btnGuardarRequisito.innerHTML = '<i class="bx bx-loader-alt bx-spin"></i> Guardando...';

            const formData = new FormData();
            formData.append('valor', valor);

            fetch(`/marcar-cumple-requisitos/${encodeURIComponent(rif)}`, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: formData
            })
            .then(response => {
                let body;
                try { body = response.json(); } catch (e) { body = {}; }
                if (!response.ok) {
                    throw new Error(body.mensaje || 'Error en el servidor');
                }
                return body;
            })
            .then(data => {
                if (data.exito) {
                    const fila = document.querySelector(`tr[data-rif="${CSS.escape(rif)}"]`);
                    if (fila) {
                        const badgeCell = fila.cells[4];
                        if (badgeCell) {
                            badgeCell.innerHTML = valor === 1
                                ? '<span class="badge bg-success badge-cumple"><i class="bx bx-check-circle"></i> Verificado</span>'
                                : '<span class="badge bg-secondary badge-cumple"><i class="bx bx-x-circle"></i> Pendiente</span>';
                        }
                        const btn = fila.querySelector('.btn-ver-requisitos');
                        if (btn) btn.setAttribute('data-cumple', String(valor));
                    }

                    requisitoFeedback.classList.remove('d-none');
                    setTimeout(() => {
                        requisitoFeedback.classList.add('d-none');
                        modalRequisitos.hide();
                    }, 2000);
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: data.mensaje || 'No se pudo actualizar el estado.',
                        target: modalRequisitosEl
                    });
                }
            })
            .catch(error => {
                Swal.fire({
                    icon: 'error',
                    title: 'Error de conexión',
                    text: 'No se pudo comunicar con el servidor.',
                    target: modalRequisitosEl
                });
            })
            .finally(() => {
                btnGuardarRequisito.disabled = false;
                btnGuardarRequisito.innerHTML = 'Guardar <i class="bi bi-save ms-1"></i>';
            });
        });
    }
});