document.addEventListener('DOMContentLoaded', function () {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const imagePreviewContainer = document.getElementById('imagePreview');
    const formEvidencias = document.getElementById('formEvidencias') || document.getElementById('formEvidenciasUpdate');
    const btnSubmit = document.getElementById('btnSubir') || document.getElementById('btnModificar');
    
    let selectedFiles = [];
    let isEditMode = formEvidencias && formEvidencias.id === 'formEvidenciasUpdate';

    // --- Inicialización para modo edición ---
    if (isEditMode && window.evidenciaData) {
        // En modo edición, el botón de submit se habilita si ya hay 3-5 imágenes existentes
        // El usuario debe seleccionar nuevas imágenes para reemplazar las antiguas.
        const existingUrls = window.evidenciaData.url_archivos.split(',');
        if (existingUrls.length >= 3 && existingUrls.length <= 5) {
            btnSubmit.disabled = false;
            if (dropZone) dropZone.style.borderColor = '#08b324'; // Verde
        } else {
            btnSubmit.disabled = true;
            if (dropZone) dropZone.style.borderColor = '#dc3545'; // Rojo
        }
        // No pre-cargamos selectedFiles con las URLs antiguas, ya que el usuario subirá nuevas.
        // La previsualización inicial se hace directamente en el HTML con Jinja.
    }

    // --- Lógica de Drag and Drop y Selección de Archivos ---
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

    function handleFiles(files) {
        selectedFiles = Array.from(files);
        updatePreviews();
        validateFileCount();
    }

    // Función para construir la URL estática (simula url_for('static') de Flask)
    function getStaticUrl(relativePath) {
        // Asume que 'static/' es la base para archivos estáticos.
        // La URL almacenada en DB ya es relativa a 'static/'.
        return `/${relativePath}`; 
    }

    function updatePreviews() {
        imagePreviewContainer.innerHTML = ''; // Limpiar previsualizaciones existentes
        
        // Mostrar previsualizaciones de los archivos seleccionados
        selectedFiles.forEach((file, index) => {
            const reader = new FileReader();
            reader.onload = function (e) {
                const previewCard = `
                    <div class="preview-card-container">
                        <div class="preview-card">
                            <img src="${e.target.result}" alt="${file.name}" title="${file.name}">
                        </div>
                        <select class="form-select form-select-sm mt-2" name="etapa-foto-${index}" required>
                            <option value="" disabled selected>Etapa...</option>
                            <option value="antes">Antes</option>
                            <option value="durante">Durante</option>
                            <option value="despues">Después</option>
                        </select>
                    </div>
                `;
                imagePreviewContainer.innerHTML += previewCard;
            };
            reader.readAsDataURL(file);
        });

        // En modo edición, si no se han seleccionado nuevos archivos,
        // y hay imágenes existentes, se muestran las existentes.
        // Esto ya se maneja en el HTML con Jinja, pero si se borran y no se suben nuevas,
        // esta lógica podría ser útil para mostrar un mensaje.
        // Por ahora, la lógica es que si se seleccionan nuevos archivos, reemplazan la vista de los antiguos.
        if (isEditMode && selectedFiles.length === 0 && window.evidenciaData && window.evidenciaData.url_archivos) {
            const existingUrls = window.evidenciaData.url_archivos.split(',');
            existingUrls.forEach(url => {
                const previewCard = `
                    <div class="preview-card">
                        <img src="${getStaticUrl(url)}" alt="Evidencia existente" title="Evidencia existente">
                    </div>
                `;
                imagePreviewContainer.innerHTML += previewCard;
            });
        }
    }

    function validateFileCount() {
        const count = selectedFiles.length;
        if (count >= 3 && count <= 5) {
            btnSubmit.disabled = false;
            if (dropZone) dropZone.style.borderColor = '#08b324'; // Verde
        } else {
            btnSubmit.disabled = true;
            if (dropZone) dropZone.style.borderColor = '#dc3545'; // Rojo
            if (count > 0) {
                if (typeof createToast === 'function') {
                    createToast('Debe seleccionar entre 3 y 5 imágenes.', 'error');
                } else {
                    alert('Debe seleccionar entre 3 y 5 imágenes.');
                }
            }
        }
    }

    // --- Lógica de Envío Asíncrono (Fetch/AJAX) para Registro ---
    async function registrarEvidenciasFetch(event) {
        event.preventDefault();
        if (btnSubmit.disabled) return;

        const formData = new FormData(formEvidencias);
        selectedFiles.forEach(file => formData.append('fotos', file, file.name));

        try {
            const response = await fetch('/api/evidencias/subir', { // URL para registro
                method: 'POST',
                body: formData
            });
            const result = await response.json();

            if (result.status === 'success') {
                if (typeof createToast === 'function') createToast(result.message, 'success');
                window.location.href = '/evidencias/listar';
            } else {
                if (typeof createToast === 'function') createToast('Error: ' + result.message, 'error');
                else alert('Error: ' + result.message);
            }
        } catch (error) {
            console.error('Error al subir evidencias:', error);
            if (typeof createToast === 'function') createToast('Error de conexión con el servidor.', 'error');
            else alert('Error de conexión con el servidor.');
        }
    }

    // --- Lógica de Envío Asíncrono (Fetch/AJAX) para Actualización ---
    async function actualizarEvidenciasFetch(event) {
        event.preventDefault();
        if (btnSubmit.disabled) return;

        const idEvidencia = document.getElementById('idEvidencia').value;
        const formData = new FormData(formEvidencias);
        selectedFiles.forEach(file => formData.append('fotos', file));

        try {
            const response = await fetch(`/api/evidencias/actualizar/${idEvidencia}`, { // URL para actualización
                method: 'POST',
                body: formData
            });
            const result = await response.json();

            if (result.status === 'success') {
                if (typeof createToast === 'function') createToast(result.message, 'success');
                window.location.href = '/evidencias/listar';
            } else {
                if (typeof createToast === 'function') createToast('Error: ' + result.message, 'error');
                else alert('Error: ' + result.message);
            }
        } catch (error) {
            console.error('Error al actualizar evidencias:', error);
            if (typeof createToast === 'function') createToast('Error de conexión con el servidor.', 'error');
            else alert('Error de conexión con el servidor.');
        }
    }

    // --- Borrado Lógico con Confirmación (SweetAlert2) ---
    // Esta función debe ser global para ser llamada desde el HTML de lista_evidencias.html
    window.eliminarEvidenciaJS = function(id_evidencia) {
        Swal.fire({
            title: '¿Estás seguro?',
            text: "La evidencia será desactivada (borrado lógico) y no aparecerá en el listado activo.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545', // Rojo de Bootstrap para peligro
            cancelButtonColor: '#6c757d',  // Gris de Bootstrap para cancelar
            confirmButtonText: 'Sí, desactivar',
            cancelButtonText: 'Cancelar',
            reverseButtons: true
        }).then((result) => {
            if (result.isConfirmed) {
                window.location.href = `/evidencias/eliminar/${id_evidencia}`;
            }
        });
    };

    // --- Asignar manejadores de submit ---
    if (formEvidencias) {
        if (isEditMode) {
            formEvidencias.addEventListener('submit', actualizarEvidenciasFetch);
        } else {
            formEvidencias.addEventListener('submit', registrarEvidenciasFetch);
        }
    }
});