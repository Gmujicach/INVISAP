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
        });
    }

    function handleFiles(files) {
        if (isEditMode) {
            if (files.length > 1) {
                mostrarError('Solo se permite una imagen para modificar');
                fileInput.value = '';
                return;
            }
            if (files.length === 0) {
                selectedFiles = [];
            } else {
                selectedFiles = [files[0]];
            }
        } else {
            selectedFiles = Array.from(files);
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

    function updatePreviews() {
        imagePreviewContainer.innerHTML = '';
        if (selectedFiles.length === 0 && isEditMode && window.evidenciaData && window.evidenciaData.url_archivos) {
            const existingUrls = window.evidenciaData.url_archivos.split(',');
            existingUrls.forEach(url => {
                imagePreviewContainer.innerHTML += crearCardPreview('/static/' + url, 'Evidencia existente', true);
            });
            return;
        }
        selectedFiles.forEach((file, index) => {
            const reader = new FileReader();
            reader.onload = function (e) {
                imagePreviewContainer.innerHTML += crearCardPreview(e.target.result, file.name, false, index);
                agregarEventoSelect(index);
            };
            reader.readAsDataURL(file);
        });
    }

    function crearCardPreview(src, alt, esExistente, index = 0) {
        if (esExistente) {
            return `<div class="preview-card"><img src="${src}" alt="${alt}" title="${alt}"><p class="text-muted small mt-1">Imagen actual</p></div>`;
        }
        return `<div class="preview-card-container" data-index="${index}">
                    <div class="preview-card">
                        <img src="${src}" alt="${alt}" title="${alt}">
                    </div>
                    <select class="form-select form-select-sm mt-2 custom-placeholder" data-index="${index}" required>
                        <option value="" disabled selected>👉 Seleccione etapa</option>
                        <option value="antes">Antes</option>
                        <option value="durante">Durante</option>
                        <option value="despues">Despues</option>
                    </select>
                </div>`;
    }

    function agregarEventoSelect(index) {
        const select = document.querySelector(`select[data-index="${index}"]`);
        if (select) {
            select.addEventListener('change', function() {
                validateFileCount();
                const allSelects = document.querySelectorAll('select[data-index]');
                let allSelected = true;
                allSelects.forEach(s => {
                    if (!s.value) allSelected = false;
                });
                if (allSelected && selectedFiles.length >= MIN_IMAGENES) {
                    btnSubmit.disabled = false;
                    if (dropZone) dropZone.style.borderColor = '#08b324';
                } else {
                    btnSubmit.disabled = true;
                    if (dropZone) dropZone.style.borderColor = '#dc3545';
                }
            });
        }
    }

    function validateFileCount() {
        const count = selectedFiles.length;
        if (isEditMode) {
            if (count === 1) {
                const select = document.querySelector('select[data-index]');
                if (select && select.value) {
                    btnSubmit.disabled = false;
                } else {
                    btnSubmit.disabled = true;
                }
                if (dropZone) dropZone.style.borderColor = '#08b324';
            } else {
                btnSubmit.disabled = true;
                if (dropZone) dropZone.style.borderColor = '#dc3545';
            }
            return;
        }
        if (count >= MIN_IMAGENES && count <= MAX_IMAGENES) {
            const allSelects = document.querySelectorAll('select[data-index]');
            let allSelected = true;
            allSelects.forEach(s => {
                if (!s.value) allSelected = false;
            });
            if (allSelected) {
                btnSubmit.disabled = false;
                if (dropZone) dropZone.style.borderColor = '#08b324';
            } else {
                btnSubmit.disabled = true;
                if (dropZone) dropZone.style.borderColor = '#dc3545';
            }
        } else {
            btnSubmit.disabled = true;
            if (dropZone) dropZone.style.borderColor = '#dc3545';
            if (count > 0) mostrarError(`Seleccione entre ${MIN_IMAGENES} y ${MAX_IMAGENES} imagenes`);
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
        const selectoresEtapa = getSelectoresEtapa();
        selectedFiles.forEach((file, index) => {
            const select = document.querySelector(`select[data-index="${index}"]`);
            formData.append('fotos', file);
            if (select) {
                formData.append('etapas[]', select.value);
            } else {
                formData.append('etapas[]', '');
            }
        });
        return formData;
    }

    window.registrarEvidenciasFetch = async function(event) {
        event.preventDefault();
        if (btnSubmit.disabled) return;
        if (!validarEtapas()) return mostrarError('Seleccione la etapa para cada imagen');
        const formData = generarFormDataLimpio();
        
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Procesando...';
        try {
            const response = await fetch('/api/evidencias/subir', { method: 'POST', body: formData });
            const result = await response.json();
            if (result.status === 'success') {
                mostrarExito(result.message);
                setTimeout(() => { window.location.href = '/evidencias/listar'; }, 1500);
            } else {
                mostrarError(result.message);
                btnSubmit.disabled = false;
                btnSubmit.innerHTML = 'Registrar Evidencias';
            }
        } catch (error) {
            mostrarError('Error de red: ' + error.message);
            btnSubmit.disabled = false;
            btnSubmit.innerHTML = 'Registrar Evidencias';
        }
    };

    window.actualizarEvidenciasFetch = async function(event) {
        event.preventDefault();
        if (btnSubmit.disabled) return;
        const idEvidencia = document.getElementById('idEvidencia').value;
        const existeResp = await fetch(`/api/evidencias/validar/${idEvidencia}`);
        const existeData = await existeResp.json();
        if (!existeData.existe) return mostrarError('Evidencia no valida');
        if (!validarEtapas()) return mostrarError('Seleccione la etapa para la imagen');
        const formData = generarFormDataLimpio();
        
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Procesando...';
        try {
            const response = await fetch(`/api/evidencias/actualizar/${idEvidencia}`, { method: 'POST', body: formData });
            const result = await response.json();
            if (result.status === 'success') {
                mostrarExito(result.message);
                setTimeout(() => { window.location.href = '/evidencias/listar'; }, 1500);
            } else {
                mostrarError(result.message);
                btnSubmit.disabled = false;
                btnSubmit.innerHTML = 'Modificar Evidencia';
            }
        } catch (error) {
            mostrarError('Error de red: ' + error.message);
            btnSubmit.disabled = false;
            btnSubmit.innerHTML = 'Modificar Evidencia';
        }
    };

    window.eliminarEvidenciaJS = function(id_evidencia) {
        Swal.fire({
            title: '¿Desactivar registro?',
            text: 'Se aplicara borrado logico',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Desactivar',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                window.location.href = `/evidencias/eliminar/${id_evidencia}`;
            }
        });
    };

    function mostrarExito(msj) { Swal.fire({ icon: 'success', title: 'Exito', text: msj, timer: 2000, showConfirmButton: false }); }
    function mostrarError(msj) { Swal.fire({ icon: 'error', title: 'Error', text: msj }); }
});