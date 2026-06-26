document.addEventListener('DOMContentLoaded', function() {
    console.log("Sistema de Empresas cargado.");

    // ELIMINACIÓN
    const botonesEliminar = document.querySelectorAll('.btn-eliminar');
    
    botonesEliminar.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const urlEliminar = this.getAttribute('data-url');
            const filaTabla = this.closest('tr'); // Detectamos la fila <tr>
            
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
                    
                    // Petición AJAX para eliminar
                    fetch(urlEliminar)
                    .then(response => response.json())
                    .then(data => {
                        if(data.exito) {
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
                    .catch(error => {
                        console.error('Error:', error);
                        Swal.fire('Error crítico', 'No se pudo conectar con el servidor.', 'error');
                    });
                }
            });
        });
    });

    // LÓGICA DE FORMULARIO
    const formulario = document.getElementById('form_registro_empresa');
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
            .then(response => response.json()) //JSON del Router
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
});