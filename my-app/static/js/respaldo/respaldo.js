/*
 * JS Módulo de Respaldo y Restauración
 * Modos: Exportar / Importar
 * Lista automática desde la tabla respaldo_bd
 */

function inicializarModuloRespaldo() {
    const dropZone = document.getElementById('dropZoneImportar');
    const inputImportar = document.getElementById('archivoRespaldo');
    const btnEliminar = document.getElementById('btnConfirmarEliminarRespaldo');

    if (dropZone && inputImportar) {
        dropZone.addEventListener('click', () => inputImportar.click());
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = 'var(--respaldo-verde)';
            dropZone.style.backgroundColor = 'rgba(82, 183, 120, 0.12)';
        });
        dropZone.addEventListener('dragleave', () => {
            dropZone.style.borderColor = '';
            dropZone.style.backgroundColor = '';
        });
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = '';
            dropZone.style.backgroundColor = '';
            if (e.dataTransfer.files.length) {
                inputImportar.files = e.dataTransfer.files;
                mostrarNombreArchivo(e.dataTransfer.files[0].name);
            }
        });
        inputImportar.addEventListener('change', function () {
            if (this.files.length) {
                mostrarNombreArchivo(this.files[0].name);
            }
        });
    }

    const formExportar = document.getElementById('formExportarRespaldo');
    if (formExportar) {
        formExportar.addEventListener('submit', function (e) {
            e.preventDefault();
            exportarRespaldo();
        });
    }

    const formImportar = document.getElementById('formImportarRespaldo');
    if (formImportar) {
        formImportar.addEventListener('submit', function (e) {
            e.preventDefault();
            importarRespaldo();
        });
    }

    if (btnEliminar) {
        btnEliminar.addEventListener('click', function () {
            const id = document.getElementById('inputIdEliminar').value;
            if (id) {
                eliminarRespaldo(id);
                const modalEl = document.getElementById('modalEliminarRespaldo');
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();
            }
        });
    }

    recargarTabla();
}

window.exportarRespaldo = function () {
    const btn = document.getElementById('btnExportar');
    const textoOriginal = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generando...';

    const form = document.getElementById('formExportarRespaldo');
    const formData = new FormData(form);

    fetch('/respaldo/exportar', {
        method: 'POST',
        body: formData
    })
    .then(resp => resp.json())
    .then(result => {
        if (result.status === 'success') {
            mostrarAlerta('success', result.message);
            setTimeout(() => {
                recargarTabla();
                const modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('modalExportarRespaldo'));
                if (modal) modal.hide();
                form.reset();
            }, 600);
        } else {
            mostrarAlerta('error', result.message || 'Error al generar respaldo');
        }
    })
    .catch(() => mostrarAlerta('error', 'Error de conexión con el servidor.'))
    .finally(() => {
        btn.disabled = false;
        btn.innerHTML = textoOriginal;
    });
};

window.importarRespaldo = function () {
    const input = document.getElementById('archivoRespaldo');
    if (!input || !input.files.length) {
        mostrarAlerta('warning', 'Seleccione un archivo .sql para importar');
        return;
    }
    const btn = document.getElementById('btnImportar');
    const textoOriginal = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Importando...';

    const form = document.getElementById('formImportarRespaldo');
    const formData = new FormData(form);

    fetch('/respaldo/importar', {
        method: 'POST',
        body: formData
    })
    .then(resp => resp.json())
    .then(result => {
        if (result.status === 'success') {
            mostrarAlerta('success', result.message);
            setTimeout(() => {
                recargarTabla();
                const modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('modalImportarRespaldo'));
                if (modal) modal.hide();
                form.reset();
                setTextoArchivo('');
            }, 1200);
        } else {
            mostrarAlerta('error', result.message || 'Error al importar respaldo');
        }
    })
    .catch(() => mostrarAlerta('error', 'Error de conexión con el servidor.'))
    .finally(() => {
        btn.disabled = false;
        btn.innerHTML = textoOriginal;
    });
};

window.eliminarRespaldo = function (id) {
    fetch(`/respaldo/eliminar/${id}`, { method: 'DELETE' })
        .then(resp => resp.json())
        .then(result => {
            if (result.status === 'success') {
                mostrarAlerta('success', result.message);
                recargarTabla();
            } else {
                mostrarAlerta('error', result.message || 'Error al eliminar respaldo');
            }
        })
        .catch(() => mostrarAlerta('error', 'Error de conexión con el servidor.'));
};

function setTextoArchivo(nombre) {
    const span = document.getElementById('nombreArchivoImportar');
    if (span) span.textContent = nombre;
}

function mostrarNombreArchivo(nombre) {
    setTextoArchivo(nombre);
}

function recargarTabla() {
    fetch('/respaldo/api/listar-json')
        .then(resp => {
            if (!resp.ok) throw new Error('No autorizado');
            return resp.json();
        })
        .then(data => {
            const respaldos = data.respaldos || [];
            const tbody = document.getElementById('tbodyRespaldos');
            const contador = document.getElementById('contadorRespaldos');
            if (!tbody) return;

            tbody.innerHTML = '';
            if (contador) contador.textContent = respaldos.length;

            if (!respaldos.length) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center text-muted py-5">
                            <i class="bx bx-folder-open bx-lg mb-2"></i><br>
                            No hay respaldos registrados en el sistema.
                        </td>
                    </tr>`;
                return;
            }

            respaldos.forEach((r, index) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="fw-bold">${index + 1}</td>
                    <td><i class="bx bx-data me-1 text-respaldo-verde"></i>${r.nombre_archivo}</td>
                    <td>${r.fecha_respaldo ? new Date(r.fecha_respaldo).toLocaleString('es-VE') : 'N/A'}</td>
                    <td><span class="badge-tamano">${r.tamano_formateado}</span></td>
                    <td>${r.descripcion || '-'}</td>
                    <td class="text-center">
                        <a href="/respaldo/descargar/${encodeURIComponent(r.nombre_archivo)}" class="btn btn-outline-success btn-sm me-1" title="Descargar"><i class="bx bx-download"></i></a>
                        <button class="btn btn-outline-danger btn-sm btn-eliminar-respaldo" data-id="${r.id_respaldo}" title="Eliminar">
                            <i class="bx bx-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });

            document.querySelectorAll('.btn-eliminar-respaldo').forEach(btn => {
                btn.addEventListener('click', function () {
                    const id = this.getAttribute('data-id');
                    document.getElementById('inputIdEliminar').value = id;
                    const modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('modalEliminarRespaldo'));
                    modal.show();
                });
            });
        })
        .catch(() => {
            mostrarAlerta('error', 'Error al recargar lista de respaldos');
        });
}

function mostrarAlerta(tipo, mensaje) {
    const iconos = { success: 'bx-check-circle', error: 'bx-x-circle', warning: 'bx-error', info: 'bx-info-circle' };
    const colores = { success: 'bg-success', error: 'bg-danger', warning: 'bg-warning text-dark', info: 'bg-info' };

    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }

    const toastId = 'toast-' + Date.now();
    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center text-white ${colores[tipo] || 'bg-secondary'} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body"><i class="bx ${iconos[tipo] || 'bx-info-circle'} me-2"></i>${mensaje}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    const el = document.getElementById(toastId);
    const toast = new bootstrap.Toast(el, { autohide: true, delay: 3000 });
    toast.show();
}

document.addEventListener('DOMContentLoaded', function () {
    if (typeof inicializarModuloRespaldo === 'function') {
        inicializarModuloRespaldo();
    }
});
