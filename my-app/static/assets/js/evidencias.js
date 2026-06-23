/**
 * evidencias.js
 * Implementa comunicación asíncrona con Fetch/Ajax, Validación en tiempo real y 
 * manejo de eventos
 */

document.addEventListener('DOMContentLoaded', function () {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const imagePreviewContainer = document.getElementById('imagePreview');
    const formEvidencias = document.getElementById('formEvidencias') || document.getElementById('formEvidenciasUpdate');
    const btnSubmit = document.getElementById('btnSubir') || document.getElementById('btnModificar');
    
    let selectedFiles = [];
    let isEditMode = formEvidencias && formEvidencias.id === 'formEvidenciasUpdate';

    // Constantes de validación
    const MIN_IMAGENES = 3;
    const MAX_IMAGENES = 5;
    const FORMATOS_PERMITIDOS = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];

    // ========== INICIALIZACIÓN MODO EDICIÓN ==========
    
    if (isEditMode && window.evidenciaData) {
        const existingUrls = window.evidenciaData.url_archivos ? window.evidenciaData.url_archivos.split(',') : [];
        if (existingUrls.length >= MIN_IMAGENES && existingUrls.length <= MAX_IMAGENES) {
            btnSubmit.disabled = false;
            if (dropZone) dropZone.style.borderColor = '#08b324'; // Verde
        } else {
            btnSubmit.disabled = true;
            if (dropZone) dropZone.style.borderColor = '#dc3545'; // Rojo
        }
    }

    // ========== EVENTOS DRAG AND DROP ==========
    
    if (dropZone && fileInput) {
        // Click en zona de drop abre selector de archivos
        dropZone.addEventListener('click', () => fileInput.click());
        
        // Eventos de arrastre
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            handleFiles(files);
        });
        
        // Evento de selección de archivos
        fileInput.addEventListener('change', () => {
            handleFiles(fileInput.files);
        });
    }

    // ========== MANEJO DE ARCHIVOS ==========
    
    function handleFiles(files) {
        // Convertir FileList a Array
        const filesArray = Array.from(files);
        
        // Validar formatos
        const archivosInvalidos = filesArray.filter(file => !FORMATOS_PERMITIDOS.includes(file.type));
        
        if (archivosInvalidos.length > 0) {
            mostrarError(`Formato no permitido. Solo se aceptan: JPG, JPEG, PNG, GIF, WEBP.`);
            return;
        }
        
        selectedFiles = filesArray;
        updatePreviews();
        validateFileCount();
    }

    // ========== ACTUALIZACIÓN DE PREVISUALIZACIONES ==========
    
    function updatePreviews() {
        imagePreviewContainer.innerHTML = ''; // Limpiar previsualizaciones
        
        if (selectedFiles.length === 0 && isEditMode && window.evidenciaData && window.evidenciaData.url_archivos) {
            // Mostrar imágenes existentes en modo edición
            const existingUrls = window.evidenciaData.url_archivos.split(',');
            existingUrls.forEach(url => {
                const previewCard = crearCardPreview(getStaticUrl(url), 'Evidencia existente', true);
                imagePreviewContainer.innerHTML += previewCard;
            });
            return;
        }
        
        // Mostrar previsualizaciones de archivos seleccionados
        selectedFiles.forEach((file, index) => {
            const reader = new FileReader();
            reader.onload = function (e) {
                const previewCard = crearCardPreview(e.target.result, file.name, false, index);
                imagePreviewContainer.innerHTML += previewCard;
            };
            reader.readAsDataURL(file);
        });
    }

    function crearCardPreview(src, alt, esExistente, index = 0) {
        if (esExistente) {
            return `
                <div class="preview-card">
                    <img src="${src}" alt="${alt}" title="${alt}">
                    <p class="text-muted small mt-1">Imagen actual</p>
                </div>
            `;
        }
        
        // CORRECCIÓN: Valores en minúsculas para coincidir con el backend
        return `
            <div class="preview-card-container">
                <div class="preview-card">
                    <img src="${src}" alt="${alt}" title="${alt}">
                </div>
                <select class="form-select form-select-sm mt-2" name="etapa-foto-${index}" required>
                    <option value="" disabled selected>Seleccione etapa...</option>
                    <option value="antes">Antes</option>
                    <option value="durante">Durante</option>
                    <option value="despues">Después</option>
                </select>
            </div>
        `;
    }

    function getStaticUrl(relativePath) {
        // Construye URL estática (simula url_for de Flask)
        return `/${relativePath}`;
    }

    // ========== VALIDACIÓN DE CANTIDAD DE ARCHIVOS ==========
    
    function validateFileCount() {
        const count = selectedFiles.length;
        
        if (count >= MIN_IMAGENES && count <= MAX_IMAGENES) {
            btnSubmit.disabled = false;
            if (dropZone) dropZone.style.borderColor = '#08b324'; // Verde
        } else {
            btnSubmit.disabled = true;
            if (dropZone) dropZone.style.borderColor = '#dc3545'; // Rojo
            
            if (count > 0) {
                mostrarError(`Debe seleccionar entre ${MIN_IMAGENES} y ${MAX_IMAGENES} imágenes.`);
            }
        }
    }

    // ========== ENVÍO ASÍNCRONO (FETCH/AJAX) - REGISTRO ==========
    
    window.registrarEvidenciasFetch = async function(event) {
        event.preventDefault();
        
        if (btnSubmit.disabled) {
            mostrarError('Complete todos los campos requeridos.');
            return;
        }

        // Validar que todas las etapas estén seleccionadas
        const selectoresEtapa = document.querySelectorAll('select[name^="etapa-foto-"]');
        let etapasCompletas = true;
        
        selectoresEtapa.forEach(select => {
            if (!select.value) {
                etapasCompletas = false;
                select.classList.add('is-invalid');
            } else {
                select.classList.remove('is-invalid');
            }
        });
        
        if (!etapasCompletas) {
            mostrarError('Debe seleccionar la etapa para cada imagen.');
            return;
        }

        // Construir FormData
        const formData = new FormData();
        
        // Agregar archivos
        selectedFiles.forEach(file => {
            formData.append('fotos', file);
        });
        
        // Agregar etapas (IMPORTANTE: en minúsculas)
        selectoresEtapa.forEach((select, index) => {
            formData.append(`etapa-foto-${index}`, select.value.toLowerCase());
        });

        // Deshabilitar botón durante el envío
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Registrando...';

        try {
            const response = await fetch('/api/evidencias/subir', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();

            if (result.status === 'success') {
                mostrarExito(result.message);
                setTimeout(() => {
                    window.location.href = '/evidencias/listar';
                }, 1500);
            } else {
                mostrarError('Error: ' + result.message);
                btnSubmit.disabled = false;
                btnSubmit.innerHTML = '<i class="bi bi-check-circle me-1"></i>Registrar Evidencias';
            }
        } catch (error) {
            console.error('Error al subir evidencias:', error);
            mostrarError('Error de conexión con el servidor.');
            btnSubmit.disabled = false;
            btnSubmit.innerHTML = '<i class="bi bi-check-circle me-1"></i>Registrar Evidencias';
        }
    };

    // ========== ENVÍO ASÍNCRONO (FETCH/AJAX) - ACTUALIZACIÓN ==========
    
    window.actualizarEvidenciasFetch = async function(event) {
        event.preventDefault();
        
        if (btnSubmit.disabled) {
            mostrarError('Complete todos los campos requeridos.');
            return;
        }

        const idEvidencia = document.getElementById('idEvidencia').value;
        
        if (!idEvidencia) {
            mostrarError('ID de evidencia no válido.');
            return;
        }

        // Validar existencia en tiempo real antes de actualizar
        const existeResponse = await fetch(`/api/evidencias/validar/${idEvidencia}`);
        const existeData = await existeResponse.json();
        
        if (!existeData.existe) {
            mostrarError('La evidencia no existe o fue eliminada.');
            return;
        }

        // Validar que se hayan seleccionado nuevas imágenes
        if (selectedFiles.length === 0) {
            mostrarError('Debe seleccionar al menos una imagen nueva.');
            return;
        }

        // Validar etapas
        const selectoresEtapa = document.querySelectorAll('select[name^="etapa-foto-"]');
        let etapasCompletas = true;
        
        selectoresEtapa.forEach(select => {
            if (!select.value) {
                etapasCompletas = false;
                select.classList.add('is-invalid');
            } else {
                select.classList.remove('is-invalid');
            }
        });
        
        if (!etapasCompletas) {
            mostrarError('Debe seleccionar la etapa para cada imagen.');
            return;
        }

        // Construir FormData
        const formData = new FormData();
        
        // Agregar archivos
        selectedFiles.forEach(file => {
            formData.append('fotos', file);
        });
        
        // Agregar etapas (en minúsculas)
        selectoresEtapa.forEach((select, index) => {
            formData.append(`etapa-foto-${index}`, select.value.toLowerCase());
        });

        // Deshabilitar botón durante el envío
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Actualizando...';

        try {
            const response = await fetch(`/api/evidencias/actualizar/${idEvidencia}`, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();

            if (result.status === 'success') {
                mostrarExito(result.message);
                setTimeout(() => {
                    window.location.href = '/evidencias/listar';
                }, 1500);
            } else {
                mostrarError('Error: ' + result.message);
                btnSubmit.disabled = false;
                btnSubmit.innerHTML = '<i class="bi bi-arrow-repeat me-1"></i>Modificar Evidencia';
            }
        } catch (error) {
            console.error('Error al actualizar evidencias:', error);
            mostrarError('Error de conexión con el servidor.');
            btnSubmit.disabled = false;
            btnSubmit.innerHTML = '<i class="bi bi-arrow-repeat me-1"></i>Modificar Evidencia';
        }
    };

    // ========== BORRADO LÓGICO CON CONFIRMACIÓN (SWEETALERT2) ==========
    
    window.eliminarEvidenciaJS = function(id_evidencia) {
        Swal.fire({
            title: '¿Estás seguro?',
            text: "La evidencia será desactivada (borrado lógico) y no aparecerá en el listado activo.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Sí, desactivar',
            cancelButtonText: 'Cancelar',
            reverseButtons: true
        }).then((result) => {
            if (result.isConfirmed) {
                window.location.href = `/evidencias/eliminar/${id_evidencia}`;
            }
        });
    };

    // ========== FUNCIONES DE NOTIFICACIÓN ==========
    
    function mostrarExito(mensaje) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'success',
                title: '¡Éxito!',
                text: mensaje,
                timer: 2000,
                showConfirmButton: false
            });
        } else {
            alert(mensaje);
        }
    }

    function mostrarError(mensaje) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: mensaje
            });
        } else {
            alert(mensaje);
        }
    }
});