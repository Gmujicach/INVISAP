document.addEventListener('DOMContentLoaded', function () {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const imagePreviewContainer = document.getElementById('imagePreview');
    const formEvidencias = document.getElementById('formEvidencias') || document.getElementById('formEvidenciasUpdate');
    const btnSubmit = document.getElementById('btnSubir') || document.getElementById('btnModificar');
    
    let selectedFiles = []; // Aquí acumularemos las imágenes
    let isEditMode = formEvidencias && formEvidencias.id === 'formEvidenciasUpdate';
    const MIN_IMAGENES = 3;
    const MAX_IMAGENES = 50;

    // Validación inicial para modo edición
    if (isEditMode && window.evidenciaData) {
        const existingUrls = window.evidenciaData.url_archivos ? window.evidenciaData.url_archivos.split(',') : [];
        if (existingUrls.length >= 1) {
            btnSubmit.disabled = false;
            if (dropZone) dropZone.style.borderColor = '#08b324';
        } else {
            btnSubmit.disabled = true;
            if (dropZone) dropZone.style.borderColor = '#dc3545';
        }
    }

    // Configuración de la zona Drag & Drop
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
            handleFiles(e.dataTransfer.files);
        });
        fileInput.addEventListener('change', () => {
            handleFiles(fileInput.files);
            fileInput.value = ''; // Limpiamos el input para permitir seleccionar el mismo archivo si se borra
        });
    }

    function handleFiles(files) {
        if (isEditMode) {
            if (files.length > 1) {
                mostrarError('Solo se permite una imagen para modificar');
                return;
            }
            if (files.length > 0) {
                selectedFiles = [files[0]];
            }
        } else {
            // SOLUCIÓN 1: Concatenar archivos en lugar de sobreescribir (Permite selección individual)
            const newFiles = Array.from(files);
            if (selectedFiles.length + newFiles.length > MAX_IMAGENES) {
                mostrarError(`Límite alcanzado. Solo puedes tener un máximo de ${MAX_IMAGENES} imágenes.`);
                const allowed = MAX_IMAGENES - selectedFiles.length;
                selectedFiles = selectedFiles.concat(newFiles.slice(0, allowed));
            } else {
                selectedFiles = selectedFiles.concat(newFiles);
            }
        }
        
        updatePreviews();
        validateFileCount();
        
        const helpEtapa = document.getElementById('helpEtapa');
        if (helpEtapa) {
            if (selectedFiles.length > 0) {
                helpEtapa.classList.remove('d-none');
            } else if (!isEditMode) {
                helpEtapa.classList.add('d-none');
            }
        }
    }

    // Nueva función para eliminar imágenes seleccionadas individualmente
    window.removeFile = function(index) {
        selectedFiles.splice(index, 1);
        updatePreviews();
        validateFileCount();
    };

    function updatePreviews() {
        // SOLUCIÓN 2: Guardar el estado de los selectores antes de repintar el HTML
        const currentSelectStates = {};
        document.querySelectorAll('select[data-index]').forEach(select => {
            currentSelectStates[select.dataset.index] = select.value;
        });

        imagePreviewContainer.innerHTML = '';
        
        if (selectedFiles.length === 0 && isEditMode && window.evidenciaData && window.evidenciaData.url_archivos) {
            const existingUrls = window.evidenciaData.url_archivos.split(',');
            existingUrls.forEach(url => {
                imagePreviewContainer.innerHTML += crearCardPreviewExistente('/static/' + url, 'Evidencia existente');
            });
            return;
        }
        
        selectedFiles.forEach((file, index) => {
            const containerDiv = document.createElement('div');
            containerDiv.className = 'preview-card-container';
            containerDiv.dataset.index = index;
            
            // Recuperamos el valor guardado (si existe) para no perder la selección
            const val = currentSelectStates[index] || '';
            
            containerDiv.innerHTML = `
                <div class="preview-card position-relative">
                    <img id="img-prev-${index}" src="" alt="${file.name}" title="${file.name}">
                    <button type="button" class="btn btn-danger btn-sm position-absolute top-0 end-0 m-1 px-2 py-0" 
                            onclick="removeFile(${index})" style="line-height: 1.2; border-radius: 50%; font-weight: bold;" title="Eliminar">&times;</button>
                </div>
                <select class="form-select form-select-sm mt-2 custom-placeholder" data-index="${index}" required>
                    <option value="" disabled ${val === '' ? 'selected' : ''}>Seleccione etapa</option>
                    <option value="antes" ${val === 'antes' ? 'selected' : ''}>Antes</option>
                    <option value="durante" ${val === 'durante' ? 'selected' : ''}>Durante</option>
                    <option value="despues" ${val === 'despues' ? 'selected' : ''}>Después</option>
                </select>
            `;
            imagePreviewContainer.appendChild(containerDiv);

            // Cargar la imagen usando FileReader
            const reader = new FileReader();
            reader.onload = function (e) {
                const img = document.getElementById(`img-prev-${index}`);
                if (img) img.src = e.target.result;
            };
            reader.readAsDataURL(file);

            agregarEventoSelect(index);
        });
    }

    function crearCardPreviewExistente(src, alt) {
        return `<div class="preview-card"><img src="${src}" alt="${alt}" title="${alt}"><p class="text-muted small mt-1">Imagen actual</p></div>`;
    }

    function agregarEventoSelect(index) {
        const select = document.querySelector(`select[data-index="${index}"]`);
        if (select) {
            select.addEventListener('change', function() {
                validateFileCount();
            });
        }
    }

    function validateFileCount() {
        const count = selectedFiles.length;
        if (isEditMode) {
            if (count === 1) {
                const select = document.querySelector('select[data-index]');
                btnSubmit.disabled = !(select && select.value);
                if (dropZone) dropZone.style.borderColor = '#08b324';
            } else {
                btnSubmit.disabled = true;
                if (dropZone) dropZone.style.borderColor = '#dc3545';
            }
            return;
        }
        
        // Validación del límite (3 a 5 imágenes)
        if (count >= MIN_IMAGENES && count <= MAX_IMAGENES) {
            const allSelects = document.querySelectorAll('select[data-index]');
            let allSelected = true;
            allSelects.forEach(s => {
                if (!s.value) allSelected = false;
            });
            
            if (allSelected && allSelects.length > 0) {
                btnSubmit.disabled = false;
                if (dropZone) dropZone.style.borderColor = '#08b324';
            } else {
                btnSubmit.disabled = true;
                if (dropZone) dropZone.style.borderColor = '#ffc107'; // Amarillo si falta etapa
            }
        } else {
            btnSubmit.disabled = true;
            if (dropZone) dropZone.style.borderColor = '#dc3545';
        }
    }

    function getSelectoresEtapa() {
        return document.querySelectorAll('select[data-index]');
    }

    function validarEtapas() {
        const selectoresEtapa = getSelectoresEtapa();
        let completas = true;
        selectoresEtapa.forEach(select => {
            if (!select.value) {
                completas = false;
                select.classList.add('is-invalid');
            } else {
                select.classList.remove('is-invalid');
            }
        });
        return completas;
    }

    function generarFormDataLimpio() {
        const formData = new FormData();
        selectedFiles.forEach((file, index) => {
            const select = document.querySelector(`select[data-index="${index}"]`);
            formData.append('fotos', file);
            formData.append('etapas[]', select && select.value ? select.value : 'antes');
        });
        return formData;
    }

    // Funciones de conexión Fetch
    window.registrarEvidenciasFetch = async function(event) {
        event.preventDefault();
        if (btnSubmit.disabled) return;
        
        const textoOriginal = btnSubmit.innerHTML;
        
        if (selectedFiles.length < MIN_IMAGENES || selectedFiles.length > MAX_IMAGENES) {
            btnSubmit.disabled = false;
            btnSubmit.innerHTML = textoOriginal;
            return mostrarError(`Debe subir entre ${MIN_IMAGENES} y ${MAX_IMAGENES} imágenes.`);
        }
        if (!validarEtapas()) {
            btnSubmit.disabled = false;
            btnSubmit.innerHTML = textoOriginal;
            return mostrarError('Seleccione la etapa para cada imagen seleccionada');
        }
        
        const formData = generarFormDataLimpio();
        
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Procesando...';
        
        try {
            const response = await fetch('/api/evidencias/subir', { method: 'POST', body: formData, credentials: 'include' });
            const result = await response.json();
            if (result.status === 'success') {
                mostrarExito(result.message);
                setTimeout(() => { window.location.href = '/evidencias/listar'; }, 1500);
            } else {
                mostrarError(result.message);
                btnSubmit.disabled = false;
                btnSubmit.innerHTML = textoOriginal;
            }
        } catch (error) {
            mostrarError('Error de red: ' + error.message);
            btnSubmit.disabled = false;
            btnSubmit.innerHTML = textoOriginal;
        }
    };

    window.actualizarEvidenciasFetch = async function(event) {
        event.preventDefault();
        if (btnSubmit.disabled) return;
        const textoOriginal = btnSubmit.innerHTML;
        const idEvidencia = document.getElementById('idEvidencia').value;
        const existeResp = await fetch(`/api/evidencias/validar/${idEvidencia}`);
        const existeData = await existeResp.json();
        
        if (!existeData.existe) {
            btnSubmit.disabled = false;
            btnSubmit.innerHTML = textoOriginal;
            return mostrarError('Evidencia no válida');
        }
        if (!validarEtapas()) {
            btnSubmit.disabled = false;
            btnSubmit.innerHTML = textoOriginal;
            return mostrarError('Seleccione la etapa para la imagen');
        }
        const formData = generarFormDataLimpio();
        
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Procesando...';
        try {
            const response = await fetch(`/api/evidencias/actualizar/${idEvidencia}`, { method: 'POST', body: formData, credentials: 'include' });
            const result = await response.json();
            if (result.status === 'success') {
                mostrarExito(result.message);
                setTimeout(() => { window.location.href = '/evidencias/listar'; }, 1500);
            } else {
                mostrarError(result.message);
                btnSubmit.disabled = false;
                btnSubmit.innerHTML = textoOriginal;
            }
        } catch (error) {
            mostrarError('Error de red: ' + error.message);
            btnSubmit.disabled = false;
            btnSubmit.innerHTML = textoOriginal;
        }
    };

    window.eliminarEvidenciaJS = function(id_evidencia) {
        Swal.fire({
            title: '¿Desactivar registro?',
            text: 'Se aplicará borrado lógico',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Desactivar',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                fetch(`/evidencias/eliminar/${id_evidencia}`)
                    .then(function(response) { return response.json(); })
                    .then(function(data) {
                        if (data && data.status === 'success') {
                            Swal.fire({
                                icon: 'success',
                                title: '¡Éxito!',
                                text: data.message || 'Registro desactivado.',
                                timer: 1500,
                                showConfirmButton: false
                            });
                            var row = document.querySelector(`tr[data-id-evidencia="${id_evidencia}"]`);
                            if (row) {
                                row.style.transition = 'opacity 0.4s';
                                row.style.opacity = '0';
                                setTimeout(function() { row.remove(); }, 400);
                            } else {
                                setTimeout(function() { location.reload(); }, 1200);
                            }
                        } else {
                            Swal.fire({
                                icon: 'error',
                                title: 'Error',
                                text: (data && data.message) || 'No se pudo desactivar.'
                            });
                        }
                    })
                    .catch(function() {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: 'Error de conexión con el servidor.'
                        });
                    });
            }
        });
    };

    function mostrarExito(msj) { Swal.fire({ icon: 'success', title: 'Éxito', text: msj, timer: 2000, showConfirmButton: false }); }
    function mostrarError(msj) { Swal.fire({ icon: 'error', title: 'Error', text: msj }); }
});