/**
 * publicaciones.js - Validaciones y selector visual de informes vinculables.
 * El selector conserva el campo informe_avance_obra_id_informe para el POST existente.
 */

const publicationReportSelectorState = {
    reportIndex: [],
    reports: [],
    committedSelectedId: '',
    draftSelectedId: '',
    loaded: false,
    loading: false,
    commitPending: false
};

const REPORT_STAGES = [
    { key: 'antes', label: 'ANTES', badgeClass: 'publication-stage-badge--before' },
    { key: 'durante', label: 'DURANTE', badgeClass: 'publication-stage-badge--during' },
    { key: 'despues', label: 'DESPUÉS', badgeClass: 'publication-stage-badge--after' }
];

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
        initializePublicacionValidation();
        initializeInformeSelector();
    });
} else {
    initializePublicacionValidation();
    initializeInformeSelector();
}

function initializePublicacionValidation() {
    const formPublicacion = document.querySelector('form[action*="publicacion"]');

    if (!formPublicacion || formPublicacion.dataset.publicationValidationBound === 'true') return;

    const inputTitulo = formPublicacion.querySelector('input[name="titulo_publicacion"]');
    const inputResponsable = formPublicacion.querySelector('input[name="nombre_responsable"]');
    const selectTipo = formPublicacion.querySelector('select[name="tipo_publicacion"]');
    const inputFecha = formPublicacion.querySelector('input[name="fecha_publicacion"]');
    const inputInforme = formPublicacion.querySelector('input[name="informe_avance_obra_id_informe"]');

    if (inputInforme) {
        inputInforme.addEventListener('change', validateInformeSelection);
    }

    if (inputTitulo) {
        inputTitulo.addEventListener('input', validateTitulo);
    }

    if (inputResponsable) {
        inputResponsable.addEventListener('input', validateResponsable);
    }

    if (selectTipo) {
        selectTipo.addEventListener('change', validateTipo);
    }

    if (inputFecha) {
        inputFecha.addEventListener('change', validateFecha);
    }

    formPublicacion.addEventListener('submit', function (event) {
        if (!validateInformeSelection()) {
            event.preventDefault();
            event.stopImmediatePropagation();
            mostrarError('Complete todos los campos correctamente antes de guardar.');

            const modalElement = document.getElementById('modalSeleccionInforme');
            if (modalElement && typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                bootstrap.Modal.getOrCreateInstance(modalElement).show();
            }
        }
    });

    formPublicacion.dataset.publicationValidationBound = 'true';
}

const REGEX_TITULO = /^[a-zA-Z0-9\sÁÉÍÓÚáéíóúñÑ.,-]{5,150}$/;
const REGEX_RESPONSABLE = /^[a-zA-Z\sÁÉÍÓÚáéíóúñÑ]{3,45}$/;

function validateTitulo() {
    const input = this;
    const valor = input.value.trim();

    if (valor.length === 0) {
        setInvalid(input, 'El título es obligatorio.');
        return false;
    }

    if (valor.length < 5) {
        setInvalid(input, 'El título debe tener al menos 5 caracteres.');
        return false;
    }

    if (valor.length > 150) {
        setInvalid(input, 'El título no puede exceder 150 caracteres.');
        return false;
    }

    if (!REGEX_TITULO.test(valor)) {
        setInvalid(input, 'El título contiene caracteres inválidos.');
        return false;
    }

    setValid(input);
    return true;
}

function validateResponsable() {
    const input = this;
    const valor = input.value.trim();

    if (valor.length === 0) {
        setInvalid(input, 'El nombre del responsable es obligatorio.');
        return false;
    }

    if (valor.length < 3) {
        setInvalid(input, 'El nombre debe tener al menos 3 caracteres.');
        return false;
    }

    if (valor.length > 45) {
        setInvalid(input, 'El nombre no puede exceder 45 caracteres.');
        return false;
    }

    if (!REGEX_RESPONSABLE.test(valor)) {
        setInvalid(input, 'El nombre solo debe contener letras y espacios.');
        return false;
    }

    setValid(input);
    return true;
}

function validateTipo() {
    const select = this;
    const valor = select.value;

    if (!valor || valor === '') {
        setInvalid(select, 'Debe seleccionar un tipo de publicación.');
        return false;
    }

    setValid(select);
    return true;
}

function validateFecha() {
    const input = this;
    const valor = input.value;

    if (!valor) {
        setInvalid(input, 'La fecha es obligatoria.');
        return false;
    }

    setValid(input);
    return true;
}

function validateInforme() {
    if (this && this.matches && this.matches('input[name="informe_avance_obra_id_informe"]')) {
        return validateInformeSelection();
    }

    const select = this;
    const valor = select ? select.value : '';

    if (!valor || valor === '') {
        setInvalid(select, 'Debe seleccionar un informe válido.');
        return false;
    }

    setValid(select);
    return true;
}

function validateInformeSelection() {
    const input = document.getElementById('informe_avance_obra_id_informe');
    const wrapper = document.getElementById('publicationReportField');

    if (!input || !wrapper) return true;

    const isValid = Boolean(String(input.value || '').trim() && input.value !== '0');
    wrapper.classList.toggle('is-invalid', !isValid);

    return isValid;
}

function setValid(element) {
    if (!element) return;

    element.classList.remove('is-invalid');
    element.classList.add('is-valid');
    const feedback = element.parentNode && element.parentNode.parentNode
        ? element.parentNode.parentNode.querySelector('.invalid-feedback')
        : null;
    if (feedback) feedback.remove();
}

function setInvalid(element, message) {
    if (!element) return;

    element.classList.remove('is-valid');
    element.classList.add('is-invalid');

    const wrapper = element.parentNode && element.parentNode.parentNode
        ? element.parentNode.parentNode
        : element.parentNode;
    if (!wrapper) return;

    let feedback = wrapper.querySelector('.invalid-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        wrapper.appendChild(feedback);
    }
    feedback.textContent = message;
}

function initializeInformeSelector() {
    const modalElement = document.getElementById('modalSeleccionInforme');
    const hiddenInput = document.getElementById('informe_avance_obra_id_informe');

    if (!modalElement || !hiddenInput || modalElement.dataset.selectorInitialized === 'true') return;

    publicationReportSelectorState.reportIndex = readReportIndex();
    publicationReportSelectorState.committedSelectedId = normalizeId(hiddenInput.value);
    publicationReportSelectorState.draftSelectedId = publicationReportSelectorState.committedSelectedId;

    const searchInput = document.getElementById('buscarInforme');
    const typeFilter = document.getElementById('filtroTipoInforme');
    const confirmButton = document.getElementById('btnConfirmarInforme');
    const trigger = document.getElementById('abrirSelectorInforme');

    populateTypeFilter();

    modalElement.addEventListener('show.bs.modal', function () {
        publicationReportSelectorState.draftSelectedId = publicationReportSelectorState.committedSelectedId;
        publicationReportSelectorState.commitPending = false;
        updateSelectedCards();

        if (!publicationReportSelectorState.loaded && !publicationReportSelectorState.loading) {
            cargarDetallesInformes();
        } else {
            renderReportCards();
            applyReportFilters();
        }
    });

    modalElement.addEventListener('shown.bs.modal', function () {
        if (searchInput) searchInput.focus();
    });

    modalElement.addEventListener('hidden.bs.modal', function () {
        if (!publicationReportSelectorState.commitPending) {
            publicationReportSelectorState.draftSelectedId = publicationReportSelectorState.committedSelectedId;
            updateSelectedCards();
        }
        publicationReportSelectorState.commitPending = false;
        if (trigger) trigger.focus();
    });

    if (searchInput) {
        searchInput.addEventListener('input', applyReportFilters);
    }

    if (typeFilter) {
        typeFilter.addEventListener('change', applyReportFilters);
    }

    if (confirmButton) {
        confirmButton.addEventListener('click', confirmarInformeSeleccionado);
    }

    modalElement.dataset.selectorInitialized = 'true';
    updateCommittedReportSummary();
    updateSelectionCounter();
}

function readReportIndex() {
    const script = document.getElementById('indiceInformesPublicacion');
    if (!script) return [];

    try {
        const parsed = JSON.parse(script.textContent || '[]');
        return Array.isArray(parsed) ? parsed : [];
    } catch (error) {
        console.error('No se pudo leer el índice de informes:', error);
        return [];
    }
}

function populateTypeFilter() {
    const typeFilter = document.getElementById('filtroTipoInforme');
    if (!typeFilter) return;

    const types = [...new Set(publicationReportSelectorState.reportIndex
        .map(item => item.tipo_informe || item.nombre_proyecto)
        .filter(Boolean)
        .map(normalizeText))]
        .sort((a, b) => a.localeCompare(b, 'es'));

    types.forEach(type => {
        const source = publicationReportSelectorState.reportIndex.find(item => normalizeText(item.tipo_informe || item.nombre_proyecto) === type);
        const option = document.createElement('option');
        option.value = source ? String(source.tipo_informe || source.nombre_proyecto) : type;
        option.textContent = source ? String(source.tipo_informe || source.nombre_proyecto) : type;
        typeFilter.appendChild(option);
    });
}

async function cargarDetallesInformes() {
    const statusElement = document.getElementById('estadoCargaInformes');
    const listElement = document.getElementById('listaInformesPublicacion');

    if (!listElement) return;

    publicationReportSelectorState.loading = true;
    setLoadingStatus(statusElement, 'Cargando informes y evidencias...');
    listElement.innerHTML = `
        <div class="col-12 publication-list-state">
            <span class="spinner-border text-success" role="status" aria-hidden="true"></span>
            <span class="visually-hidden">Cargando informes...</span>
            <p>Consultando los detalles registrados...</p>
        </div>
    `;

    if (publicationReportSelectorState.reportIndex.length === 0) {
        publicationReportSelectorState.reports = [];
        publicationReportSelectorState.loaded = true;
        publicationReportSelectorState.loading = false;
        setLoadingStatus(statusElement, '');
        renderReportCards();
        return;
    }

    try {
        const response = await fetchWithTimeout('/api/informes/detalles', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ids: publicationReportSelectorState.reportIndex.map(item => getReportId(item))
            })
        }, 15000);

        if (response.status === 401) {
            throw new Error('Sesión expirada. Recargue la página e intente de nuevo.');
        }

        const payload = await response.json().catch(() => ({}));

        if (!response.ok || payload.status !== 'success' || !Array.isArray(payload.data)) {
            throw new Error(payload.message || 'No se pudo cargar el detalle de los informes.');
        }

        const reportMap = new Map();
        payload.data.forEach(report => {
            reportMap.set(normalizeId(getReportId(report)), report);
        });

        publicationReportSelectorState.reports = publicationReportSelectorState.reportIndex.map(item => {
            const id = normalizeId(getReportId(item));
            const source = reportMap.get(id);
            if (!source) {
                return {
                    ...item,
                    id_informe: id || getReportId(item),
                    tipo_informe: item.tipo_informe || item.nombre_proyecto || 'Informe de avance',
                    error: true,
                    errorMessage: 'No se pudo cargar el detalle de este informe.'
                };
            }
            return normalizeReport(source);
        });

        publicationReportSelectorState.loaded = true;
        publicationReportSelectorState.loading = false;
        const failedCount = publicationReportSelectorState.reports.filter(report => report.error).length;
        setLoadingStatus(
            statusElement,
            failedCount
                ? `${publicationReportSelectorState.reports.length - failedCount} informe(s) cargado(s); ${failedCount} no disponible(s).`
                : ''
        );
        renderReportCards();
        applyReportFilters();
    } catch (error) {
        publicationReportSelectorState.loading = false;
        setLoadingStatus(statusElement, '');

        const errorReports = publicationReportSelectorState.reportIndex.map(item => ({
            ...item,
            id_informe: getReportId(item),
            tipo_informe: item.tipo_informe || item.nombre_proyecto || 'Informe de avance',
            error: true,
            errorMessage: error.message || 'No se pudo cargar el detalle de los informes.'
        }));

        publicationReportSelectorState.reports = errorReports;
        renderReportCards();
        applyReportFilters();
    }
}

async function reintentarCargaInforme(id) {
    await cargarDetallesInformes();
}

function fetchWithTimeout(url, options, timeoutMs) {
    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);

    return fetch(url, { ...options, signal: controller.signal })
        .finally(() => window.clearTimeout(timeoutId));
}

async function mapWithConcurrency(items, limit, mapper) {
    const results = new Array(items.length);
    let nextIndex = 0;

    async function worker() {
        while (nextIndex < items.length) {
            const currentIndex = nextIndex;
            nextIndex += 1;

            try {
                results[currentIndex] = {
                    status: 'fulfilled',
                    value: await mapper(items[currentIndex], currentIndex)
                };
            } catch (error) {
                results[currentIndex] = { status: 'rejected', reason: error };
            }
        }
    }

    const workers = Array.from({ length: Math.min(limit, items.length) }, worker);
    await Promise.all(workers);
    return results;
}

function normalizeReport(report) {
    const evidencias = Array.isArray(report.evidencias) ? report.evidencias : [];
    const porcentaje = Number.parseInt(report.porcentaje_avance, 10);

    return {
        ...report,
        id_informe: getReportId(report),
        tipo_informe: report.tipo_informe || report.nombre_proyecto || 'Informe de avance',
        poblacion_beneficiada: report.poblacion_beneficiada || 'Población no especificada',
        observaciones: report.observaciones || 'Sin observaciones registradas.',
        estado: report.estado || 'Sin estado',
        porcentaje_avance: Number.isFinite(porcentaje) ? Math.max(0, Math.min(100, porcentaje)) : 0,
        evidencias
    };
}

function renderReportCards() {
    const listElement = document.getElementById('listaInformesPublicacion');
    const emptyState = document.getElementById('estadoListaInformes');
    if (!listElement) return;

    if (publicationReportSelectorState.reports.length === 0) {
        listElement.innerHTML = '';
        if (emptyState) {
            emptyState.classList.remove('d-none');
            emptyState.querySelector('p').textContent = 'No hay informes registrados disponibles para vincular.';
        }
        updateSelectionCounter();
        updateConfirmButton();
        return;
    }

    listElement.innerHTML = publicationReportSelectorState.reports.map(renderReportCard).join('');
    bindReportCards();
    updateSelectedCards();
    updateSelectionCounter();
    updateConfirmButton();

    if (emptyState) emptyState.classList.add('d-none');
}

function renderReportCard(report) {
    const id = getReportId(report);
    const type = report.tipo_informe || 'Informe de avance';
    const title = report.poblacion_beneficiada || `Informe de avance #${id}`;
    const description = report.observaciones || 'Sin observaciones registradas.';
    const status = formatStatus(report.estado);
    const statusClass = getStatusClass(report.estado);
    const progress = Number.isFinite(Number(report.porcentaje_avance)) ? Number(report.porcentaje_avance) : 0;
    const searchData = normalizeText([id, type, title, description, report.gerente_nombre || '', report.fecha || ''].join(' '));
    const typeClass = getTypeClass(type);

    if (report.error) {
        return `
            <div class="col-12 col-md-6 col-xl-4" role="listitem">
                <article class="publication-report-card publication-report-card--error h-100" data-id="${escapeHtml(id)}" aria-disabled="true">
                    <div class="d-flex align-items-start gap-2">
                        <i class="bi bi-exclamation-triangle-fill fs-5" aria-hidden="true"></i>
                        <div>
                            <h3 class="publication-report-title">Informe #${escapeHtml(id)} · ${escapeHtml(type)}</h3>
                            <p>${escapeHtml(report.errorMessage || 'No se pudo cargar el detalle de este informe.')}</p>
                            <button type="button" class="btn btn-sm btn-outline-success mt-2" onclick="reintentarCargaInforme('${escapeHtml(id)}')">
                                <i class="bi bi-arrow-clockwise me-1"></i> Reintentar
                            </button>
                        </div>
                    </div>
                </article>
            </div>
        `;
    }

    return `
        <div class="col-12 col-md-6 col-xl-4" role="listitem">
            <article class="publication-report-card h-100"
                     data-id="${escapeHtml(id)}"
                     data-type="${escapeHtml(type)}"
                     data-search="${escapeHtml(searchData)}"
                     role="button"
                     tabindex="0"
                     aria-pressed="false"
                     aria-label="Seleccionar informe ${escapeHtml(id)}">
                <span class="publication-report-card__check" aria-hidden="true"><i class="bi bi-check-lg"></i></span>
                <div class="publication-report-card__top">
                    <div class="publication-report-meta-line">
                        <span class="publication-report-number">#${escapeHtml(id)}</span>
                        <span class="publication-report-type ${typeClass}">${escapeHtml(type)}</span>
                    </div>
                    <h3 class="publication-report-title" title="${escapeHtml(title)}">${escapeHtml(title)}</h3>
                    <div class="publication-report-facts">
                        <span class="publication-report-fact" title="Fecha del informe">
                            <i class="bi bi-calendar3" aria-hidden="true"></i>
                            <span>${escapeHtml(formatReportDate(report.fecha))}</span>
                        </span>
                        <span class="publication-report-fact publication-report-status ${statusClass}" title="Estado del informe">
                            <span class="publication-status-dot" aria-hidden="true"></span>
                            <span>${escapeHtml(status)}</span>
                        </span>
                    </div>
                    <p class="publication-report-description" title="${escapeHtml(description)}">${escapeHtml(description)}</p>
                    <div class="progress publication-progress" role="progressbar" aria-label="Avance del informe ${escapeHtml(id)}" aria-valuenow="${progress}" aria-valuemin="0" aria-valuemax="100">
                        <div class="progress-bar" style="width: ${progress}%"></div>
                    </div>
                    <div class="publication-report-progress-row">
                        <span>Avance de obra</span>
                        <strong>${progress}%</strong>
                    </div>
                </div>
                <div class="publication-evidence-strip" aria-label="Evidencias fotográficas del informe ${escapeHtml(id)}">
                    ${REPORT_STAGES.map(stage => renderEvidenceThumb(report, stage)).join('')}
                </div>
            </article>
        </div>
    `;
}

function renderEvidenceThumb(report, stage) {
    const evidences = getEvidenceGroups(report)[stage.key] || [];
    const evidence = evidences[0];
    const safeUrl = evidence ? getSafeImageUrl(evidence.url_archivos) : '';
    const moreCount = Math.max(0, evidences.length - 1);
    const alt = evidence && evidence.fotos
        ? evidence.fotos
        : `Sin evidencia ${stage.label.toLowerCase()}`;

    return `
        <div class="publication-evidence-thumb ${safeUrl ? '' : 'is-empty'}" title="${escapeHtml(`${stage.label}: ${evidences.length} evidencia(s)`)}">
            ${safeUrl
                ? `<img src="${escapeHtml(safeUrl)}" alt="${escapeHtml(alt)}" loading="lazy" decoding="async">`
                : '<i class="bi bi-image-alt" aria-hidden="true"></i>'}
            <span class="publication-stage-badge ${stage.badgeClass}">${stage.label}</span>
            ${moreCount > 0 ? `<span class="publication-thumb-more">+${moreCount}</span>` : ''}
        </div>
    `;
}

function bindReportCards() {
    document.querySelectorAll('#listaInformesPublicacion .publication-report-card:not(.publication-report-card--error)').forEach(card => {
        card.addEventListener('click', function () {
            selectReportCard(this.dataset.id);
        });

        card.addEventListener('keydown', function (event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                selectReportCard(this.dataset.id);
            }
        });
    });
}

function selectReportCard(id) {
    const report = publicationReportSelectorState.reports.find(item => getReportId(item) === normalizeId(id) && !item.error);
    if (!report) return;

    const normalizedId = normalizeId(id);
    if (publicationReportSelectorState.draftSelectedId === normalizedId) {
        publicationReportSelectorState.draftSelectedId = '';
    } else {
        publicationReportSelectorState.draftSelectedId = normalizedId;
    }
    updateSelectedCards();
    updateSelectionCounter();
    updateConfirmButton();
}

function updateSelectedCards() {
    document.querySelectorAll('#listaInformesPublicacion .publication-report-card').forEach(card => {
        const selected = normalizeId(card.dataset.id) === publicationReportSelectorState.draftSelectedId;
        card.classList.toggle('is-selected', selected);
        card.setAttribute('aria-pressed', selected ? 'true' : 'false');
    });
}

function applyReportFilters() {
    const queryInput = document.getElementById('buscarInforme');
    const typeFilter = document.getElementById('filtroTipoInforme');
    const query = normalizeText(queryInput ? queryInput.value : '');
    const selectedType = normalizeText(typeFilter ? typeFilter.value : 'all');
    let visibleCount = 0;

    document.querySelectorAll('#listaInformesPublicacion .publication-report-card').forEach(card => {
        const matchesQuery = !query || normalizeText(card.dataset.search || '').includes(query);
        const matchesType = selectedType === 'all' || normalizeText(card.dataset.type || '') === selectedType;
        const isVisible = matchesQuery && matchesType;
        card.closest('[role="listitem"]').classList.toggle('d-none', !isVisible);
        if (isVisible) visibleCount += 1;
    });

    const emptyState = document.getElementById('estadoListaInformes');
    if (emptyState && publicationReportSelectorState.reports.length > 0) {
        emptyState.classList.toggle('d-none', visibleCount > 0);
        emptyState.querySelector('p').textContent = visibleCount > 0
            ? ''
            : 'No hay informes que coincidan con la búsqueda o el filtro seleccionado.';
    }

    updateSelectionCounter(visibleCount);
}

function updateSelectionCounter() {
    const counter = document.querySelector('#contadorInformes span');
    if (!counter) return;

    counter.textContent = publicationReportSelectorState.draftSelectedId
        ? '1 seleccionado'
        : '0 seleccionados';
}

function updateConfirmButton() {
    const confirmButton = document.getElementById('btnConfirmarInforme');
    if (!confirmButton) return;

    const canConfirm = Boolean(publicationReportSelectorState.draftSelectedId)
        && publicationReportSelectorState.reports.some(item => getReportId(item) === publicationReportSelectorState.draftSelectedId && !item.error);
    confirmButton.disabled = !canConfirm;
}

function confirmarInformeSeleccionado() {
    const selectedId = publicationReportSelectorState.draftSelectedId;
    const report = publicationReportSelectorState.reports.find(item => getReportId(item) === selectedId && !item.error);
    const hiddenInput = document.getElementById('informe_avance_obra_id_informe');
    const modalElement = document.getElementById('modalSeleccionInforme');

    if (!report || !hiddenInput) return;

    hiddenInput.value = selectedId;
    hiddenInput.dispatchEvent(new Event('change', { bubbles: true }));
    publicationReportSelectorState.committedSelectedId = selectedId;
    publicationReportSelectorState.draftSelectedId = selectedId;
    publicationReportSelectorState.commitPending = true;
    updateCommittedReportSummary();

    if (modalElement && typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        bootstrap.Modal.getOrCreateInstance(modalElement).hide();
    }
}

function updateCommittedReportSummary() {
    const titleElement = document.getElementById('informeSeleccionadoTitulo');
    const metaElement = document.getElementById('informeSeleccionadoMeta');
    const trigger = document.getElementById('abrirSelectorInforme');
    const selectedId = publicationReportSelectorState.committedSelectedId;
    const report = publicationReportSelectorState.reports.find(item => getReportId(item) === selectedId && !item.error);

    if (!titleElement || !metaElement) return;

    if (!report) {
        titleElement.textContent = 'Seleccione un informe de avance';
        metaElement.textContent = 'Revise tipo, descripción y evidencias antes de vincularlo';
        if (trigger) trigger.classList.remove('is-selected');
        return;
    }

    const evidenceCount = Array.isArray(report.evidencias) ? report.evidencias.length : 0;
    titleElement.textContent = `Informe #${selectedId} · ${report.tipo_informe || 'Informe de avance'}`;
    metaElement.textContent = `${formatStatus(report.estado)} · ${report.porcentaje_avance || 0}% de avance · ${evidenceCount} evidencia${evidenceCount === 1 ? '' : 's'}`;
    if (trigger) trigger.classList.add('is-selected');
}

function setLoadingStatus(element, message) {
    if (!element) return;
    element.textContent = message;
    element.classList.toggle('d-none', !message);
}

function getEvidenceGroups(report) {
    const groups = { antes: [], durante: [], despues: [] };
    const evidencias = Array.isArray(report.evidencias) ? report.evidencias : [];

    evidencias.forEach(evidence => {
        const stage = normalizeStage(evidence.etapa);
        if (groups[stage]) groups[stage].push(evidence);
    });

    return groups;
}

function normalizeStage(stage) {
    const value = normalizeText(stage);
    if (value === 'despues') return 'despues';
    if (value === 'durante') return 'durante';
    return 'antes';
}

function getSafeImageUrl(path) {
    if (!path) return '';
    const value = String(path).trim();

    if (/^https?:\/\//i.test(value)) return value;
    if (value.includes('..') || value.includes('\0') || value.includes('%00')) return '';

    const cleanPath = value.replace(/^\/+/, '').replace(/^static\//, '');
    if (!/^[a-zA-Z0-9_\-./]+$/.test(cleanPath)) return '';

    return `/static/${cleanPath}`;
}

function getReportId(report) {
    return normalizeId(report && (report.id_informe ?? report.id));
}

function normalizeId(value) {
    return value === null || value === undefined ? '' : String(value).trim();
}

function normalizeText(value) {
    return String(value || '')
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .toLowerCase()
        .trim();
}

function formatReportDate(value) {
    if (!value) return 'Sin fecha';

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);

    return date.toLocaleDateString('es-VE', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
    }).replace('.', '');
}

function formatStatus(value) {
    return String(value || 'Sin estado').replace('En Ejecucion', 'En Ejecución');
}

function getStatusClass(status) {
    const normalized = normalizeText(status);
    if (normalized === 'aprobado') return 'publication-report-status--success';
    if (normalized === 'culminado') return 'publication-report-status--info';
    if (normalized === 'paralizado') return 'publication-report-status--danger';
    return 'publication-report-status--warning';
}

function getTypeClass(type) {
    const normalized = normalizeText(type);
    if (normalized.includes('mayor') || normalized.includes('inspeccion')) return 'publication-report-type--info';
    if (normalized.includes('menor')) return 'publication-report-type--warning';
    return '';
}

function escapeHtml(value) {
    if (value === null || value === undefined) return '';
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

async function handlePublicacionSubmit(event) {
    event.preventDefault();

    const form = event.target;
    const btnSubmit = form.querySelector('button[type="submit"]');

    const inputTitulo = form.querySelector('input[name="titulo_publicacion"]');
    const inputResponsable = form.querySelector('input[name="nombre_responsable"]');
    const selectTipo = form.querySelector('select[name="tipo_publicacion"]');
    const inputFecha = form.querySelector('input[name="fecha_publicacion"]');
    const inputInforme = form.querySelector('input[name="informe_avance_obra_id_informe"]');

    const validTitulo = inputTitulo ? validateTitulo.call(inputTitulo) : true;
    const validResponsable = inputResponsable ? validateResponsable.call(inputResponsable) : true;
    const validTipo = selectTipo ? validateTipo.call(selectTipo) : true;
    const validFecha = inputFecha ? validateFecha.call(inputFecha) : true;
    const validInforme = inputInforme ? validateInformeSelection() : true;

    if (!validTitulo || !validResponsable || !validTipo || !validFecha || !validInforme) {
        mostrarError('Complete todos los campos correctamente antes de guardar.');
        return;
    }

    btnSubmit.disabled = true;
    btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Guardando...';

    try {
        const formData = new FormData(form);
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData
        });

        if (response.redirected) {
            window.location.href = response.url;
            return;
        }

        const result = await response.json().catch(() => ({}));

        if (result.status === 'success' || response.ok) {
            mostrarExito('Publicación guardada exitosamente.');
            form.reset();
            form.querySelectorAll('.is-valid, .is-invalid').forEach(el => {
                el.classList.remove('is-valid', 'is-invalid');
            });
            setTimeout(() => {
                if (document.getElementById('contenedorFormulario')) {
                    const collapse = bootstrap.Collapse.getOrCreateInstance(document.getElementById('contenedorFormulario'));
                    collapse.hide();
                }
                location.reload();
            }, 1500);
        } else {
            throw new Error(result.message || 'Error al guardar la publicación.');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarError(error.message || 'Error de conexión con el servidor.');
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = btnSubmit.innerHTML.replace(/<span class="spinner-border[^>]*>.*?<\/span>/, '');
    }
}

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

async function eliminarPublicacionAjax(id_publicacion) {
    if (typeof Swal !== 'undefined') {
        const result = await Swal.fire({
            title: '¿Estás seguro?',
            text: 'La publicación será desactivada (borrado lógico).',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Sí, desactivar',
            cancelButtonText: 'Cancelar',
            reverseButtons: true
        });

        if (!result.isConfirmed) return;
    } else {
        if (!confirm('¿Estás seguro de desactivar esta publicación?')) return;
    }

    try {
        const response = await fetch(`/api/publicaciones/eliminar/${id_publicacion}`, {
            method: 'DELETE'
        });

        const result = await response.json().catch(() => ({}));

        if (response.ok || result.status === 'success') {
            mostrarExito('Publicación desactivada exitosamente.');
            const row = document.querySelector(`tr[data-id="${id_publicacion}"]`);
            if (row) row.remove();
            else location.reload();
        } else {
            throw new Error(result.message || 'Error al desactivar la publicación.');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarError(error.message || 'Error de conexión.');
    }
}
