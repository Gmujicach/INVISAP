document.addEventListener('DOMContentLoaded', function() {
    console.log("Sistema de Empresas cargado.");

    // --- 1. LÓGICA DE ELIMINACIÓN (Mantenida intacta) ---
    const botonesEliminar = document.querySelectorAll('.btn-eliminar');
    
    botonesEliminar.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const urlEliminar = this.getAttribute('data-url');
            
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
                    window.location.href = urlEliminar;
                }
            });
        });
    });

    // --- 2. LÓGICA DE FORMULARIO (Armar y Desarmar inputs ocultos) ---
    const formulario = document.getElementById('form_registro_empresa');
    if (formulario) {
        
        // A. REPOBLAR EL RIF (Si viene con datos del backend)
        const inputRifFinal = document.getElementById('rif_final');
        if (inputRifFinal && inputRifFinal.value) {
            // Ejemplo: Si value es "J-12345678", lo divide en "J" y "12345678"
            const partesRif = inputRifFinal.value.split('-');
            if (partesRif.length === 2) {
                const tipo = document.getElementById('tipo_rif');
                const num = document.getElementById('numero_rif');
                if (tipo) tipo.value = partesRif[0];
                if (num) num.value = partesRif[1];
            }
        }

        // B. REPOBLAR EL TELÉFONO (Si viene con datos del backend)
        const inputTelFinal = document.getElementById('telefono_final');
        if (inputTelFinal && inputTelFinal.value) {
            // Limpia todo lo que no sea número
            let soloNumeros = inputTelFinal.value.replace(/\D/g, '');
            if (soloNumeros.length >= 7) {
                const pref = document.getElementById('prefijo_telefono');
                const num = document.getElementById('numero_telefono');
                // Los primeros 4 son el prefijo, el resto es el número
                if(pref) pref.value = soloNumeros.substring(0, 4);
                if(num) num.value = soloNumeros.substring(4);
            }
        }

        // C. ANTES DE ENVIAR (Armar los datos ocultos)
        formulario.addEventListener('submit', function(e) {
            // Armar Teléfono
            const prefTel = document.getElementById('prefijo_telefono');
            const numTel = document.getElementById('numero_telefono');
            const telFinal = document.getElementById('telefono_final');
            
            if(prefTel && numTel && telFinal) {
                telFinal.value = prefTel.value + '-' + numTel.value;
            }

            // Armar RIF
            const tipoRif = document.getElementById('tipo_rif');
            const numRif = document.getElementById('numero_rif');
            const rifFinal = document.getElementById('rif_final');

            if (tipoRif && numRif && rifFinal) {
                rifFinal.value = tipoRif.value + '-' + numRif.value;
            }
        });
    }

    // --- 3. VALIDACIÓN VISUAL (Solo permitir números mientras se escribe) ---
    ['numero_rif', 'numero_telefono'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('input', function() {
                this.value = this.value.replace(/[^0-9]/g, '');
            });
        }
    });
});