/**
 * evidencias.js - Módulo de gestión de evidencias con Fetch/Ajax
 * Implementa drag & drop, previsualización, validación y envío asíncrono.
 * Arquitectura modular e inyección de datos limpia
 */

document.addEventListener('DOMContentLoaded', function () {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const imagePreviewContainer = document.getElementById('imagePreview');
    const formEvidencias = document.getElementById('formEvidencias') || document.getElementById('formEvidenciasUpdate');
    const btnSubmit = document.getElementById('btnSubir') || document.getElementById('btnModificar');

    let selectedFiles = [];
    let isEditMode = formEvidencias && formEvidencias.id === 'formEvidenciasUpdate';

    const MIN_IMAGENES = 3;
    const MAX_IMAGENES = 5;

    // ========== INICIALIZACIÓN ==========
    if (isEditMode && window.evidenciaData) {
        const existingUrls = window.evidenciaData.url_archivos ? window.evidenciaData.url_archivos.split(',') : [];
        if (existingUrls.length >= MIN_IMAGENES && existingUrls.length <= MAX_IMAGENES) {
            btnSubmit.disabled = false;
            if (dropZone) dropZone.style.borderColor = '#08b324';
        } else {
            btnSubmit.disabled = true;
            if (dropZone) dropZone.style.borderColor = '#dc3545';
        }
    }

    // ========== DRAG & DROP ==========
    if (dropZone && fileInput) {
        dropZone.addEventListener('click', () => fileInput.click());

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

        fileInput.addEventListener('change', () => {
            handleFiles(fileInput.files);
        });
    }

    // ========== MANEJO DE ARCHIVOS ==========
    function handleFiles(files) {
        const filesArray = Array.from(files);
        selectedFiles = filesArray;
        updatePreviews();
        validateFileCount();
    }

    // ========== PREVISUALIZACIÓN ==========
    function updatePreviews() {
        imagePreviewContainer.innerHTML = '';

        if (selectedFiles.length === 0 && isEditMode && window.evidenciaData && window.evidenciaData.url_archivos) {
            const existingUrls = window.evidenciaData.url_archivos.split(',');
            existingUrls.forEach(url => {
                const previewCard = crearCardPreview(getStaticUrl(url), 'Evidencia existente', true);
                imagePreviewContainer.innerHTML += previewCard;
            });
            return;
        }

        selectedFiles.forEach((file, index) => {
            const reader = new FileReader();
            reader.onload = function (e) {
                const previewCard = crearCardPreview(e.target.result, file.name, false, index);
                imagePreviewContainer.insertAdjacentHTML('beforeend', previewCard);
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
        return '/' + relativePath;
    }

    // ========== VALIDACIÓN DE CANTIDAD ==========
    function validateFileCount() {
        const count = selectedFiles.length;
        if (count >= MIN_IMAGENES && count <= MAX_IMAGENES) {
            btnSubmit.disabled = false;
            if (dropZone) dropZone.style.borderColor = '#08b324';
        } else {
            btnSubmit.disabled = true;
            if (dropZone) dropZone.style.borderColor = '#dc3545';
            if (count > 0) {
                mostrarError(`Debe seleccionar entre ${MIN_IMAGENES} y ${MAX_IMAGENES} imágenes.`);
            }
        }
    }

    // ========== ENVÍO ASÍNCRONO (REGISTRO) ==========
    window.registrarEvidenciasFetch = async function(event) {
        event.preventDefault();
        if (btnSubmit.disabled) {
            mostrarError('Complete todos los campos requeridos.');
            return;
        }

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

        // ✅ CORRECCIÓN: Usar el formulario directamente para incluir todos los campos
        const formData = new FormData(formEvidencias);
        
        // Agregar los archivos al FormData
        selectedFiles.forEach((file, index) => {
            formData.append('fotos', file);

            const selectEtapa = document.querySelector(`select[name="etapa-foto-${index}"]`);
            if (selectEtapa && selectEtapa.value) {
                if (!formData.has(`etapa-foto-${index}`)) {
                    formData.append(`etapa-foto-${index}`, selectEtapa.value);
                }
            }
        });

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

    // ========== ENVÍO ASÍNCRONO (ACTUALIZACIÓN) ==========
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

        const existeResponse = await fetch(`/api/evidencias/validar/${idEvidencia}`);
        const existeData = await existeResponse.json();
        if (!existeData.existe) {
            mostrarError('La evidencia no existe o fue eliminada.');
            return;
        }

        if (selectedFiles.length === 0) {
            mostrarError('Debe seleccionar al menos una imagen nueva.');
            return;
        }

        // Validar cantidad de imágenes seleccionadas
        if (selectedFiles.length < MIN_IMAGENES || selectedFiles.length > MAX_IMAGENES) {
            mostrarError(`Debe seleccionar entre ${MIN_IMAGENES} y ${MAX_IMAGENES} imágenes.`);
            return;
        }

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

        // ✅ CORRECCIÓN: Usar el formulario directamente para incluir todos los campos
        const formData = new FormData(formEvidencias);
        
        // Agregar los archivos al FormData
        selectedFiles.forEach((file) => {
            formData.append('fotos', file);
        });

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

    // ========== BORRADO LÓGICO CON SWEETALERT2 ==========
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

    // ========== NOTIFICACIONES ==========
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