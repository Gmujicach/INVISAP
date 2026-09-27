/* Bootstrap is provided by base_cpanel.html; this page has no module bundler. */
(function () {
  'use strict';

  function initGravedad() {
    const root = document.querySelector('.gravedad-container');
    if (!root) return;
    const el = (id) => document.getElementById(id);
    const form = el('formGravedad');
    const modalElement = el('modalGravedad');
    const detailsElement = el('modalDetallesGravedad');
    const recordsElement = el('registrosGravedad');
    const saveButton = el('btnGuardarGravedad');
    const refreshButton = el('btnActualizarGravedad');
    const state = { records: [], loading: false, saving: false, error: '', loadVersion: 0, detailVersion: 0 };
    const pendingDeactivations = new Set();
    let modalTrigger = null;
    const LEVELS = {
      low: { label: 'Baja', api: 'Bajo', className: 'gravedad-low', icon: 'bi-shield-check' },
      high: { label: 'Alta', api: 'Alto', className: 'gravedad-high', icon: 'bi-exclamation-triangle' }
    };

    function node(tag, className, text) {
      const element = document.createElement(tag);
      if (className) element.className = className;
      if (text !== undefined) element.textContent = String(text);
      return element;
    }

    function icon(name) {
      const element = node('i', `bi ${name}`);
      element.setAttribute('aria-hidden', 'true');
      return element;
    }

    function levelFor(record) {
      const label = String(record.nivel_gravedad || '').trim();
      if (['bajo', 'baja'].includes(label.toLowerCase())) return LEVELS.low;
      if (['alto', 'alta'].includes(label.toLowerCase())) return LEVELS.high;
      return { label: label || 'Sin nivel', className: 'gravedad-neutral', icon: 'bi-question-circle' };
    }

    function percent(record) {
      const value = record.criticidad;
      return value !== null && value !== undefined && String(value).trim() !== '' && Number.isFinite(Number(value))
        ? Number(value) : null;
    }

    function formatPercent(record) {
      const value = percent(record);
      return value === null ? 'N/A' : `${value}%`;
    }

    function statusLabel(record) { return Number(record.estado) === 1 ? 'Activo' : 'Inactivo'; }

    function levelLabel(record) {
      const level = levelFor(record);
      const label = node('span', `gravedad-level ${level.className}`);
      const symbol = node('span', 'gravedad-level-icon');
      symbol.append(icon(level.icon));
      label.append(symbol, node('span', '', level.label));
      return label;
    }

    function statusBadge(record) {
      return node('span', `badge gravedad-state${Number(record.estado) === 1 ? ' gravedad-state-active' : ''}`, statusLabel(record));
    }

    function meter(record) {
      const wrapper = node('div', levelFor(record).className);
      wrapper.append(node('span', 'gravedad-meter-value', formatPercent(record)));
      const value = percent(record);
      if (value !== null) {
        const progress = node('div', 'progress gravedad-meter');
        progress.setAttribute('aria-hidden', 'true');
        const bar = node('div', 'progress-bar');
        bar.style.width = `${Math.max(0, Math.min(100, value))}%`;
        progress.append(bar);
        wrapper.append(progress);
      }
      return wrapper;
    }

    function actions(record) {
      const wrapper = node('div', 'gravedad-actions btn-acciones');
      [
        ['details', 'Ver detalles', 'bi-eye', 'btn-accion-ver'],
        ['edit', 'Editar', 'bi-pencil-square', 'btn-accion-editar'],
        ['deactivate', 'Desactivar', 'bi-power', 'btn-accion-neutro']
      ].forEach(([action, title, symbol, variante]) => {
        const button = node('button', 'btn btn-sm btn-accion gravedad-action ' + variante);
        button.type = 'button';
        button.dataset.action = action;
        button.dataset.id = String(record.id_gravedad);
        button.title = title;
        button.setAttribute('aria-label', `${title} nivel ${levelFor(record).label}, ID ${record.id_gravedad}`);
        button.disabled = pendingDeactivations.has(String(record.id_gravedad));
        button.append(icon(symbol));
        wrapper.append(button);
      });
      return wrapper;
    }

    function tableRow(record) {
      const row = node('tr');
      const id = node('span', 'gravedad-id', record.id_gravedad);
      [id, levelLabel(record), meter(record), statusBadge(record), actions(record)].forEach(content => {
        const cell = node('td');
        cell.append(content);
        row.append(cell);
      });
      return row;
    }

    function mobileRecord(record) {
      const card = node('article', 'card gravedad-mobile-record');
      card.setAttribute('role', 'listitem');
      const header = node('div', 'd-flex flex-wrap align-items-center justify-content-between gap-2');
      header.append(levelLabel(record), node('span', 'gravedad-mobile-meta', `${statusLabel(record)} · ID ${record.id_gravedad}`));
      const value = node('div', 'd-flex align-items-center justify-content-between gap-2 gravedad-mobile-criticidad');
      value.append(node('span', 'gravedad-help', 'Criticidad'), node('strong', levelFor(record).className, formatPercent(record)));
      const footer = node('div', 'd-flex align-items-center justify-content-between gap-2');
      footer.append(node('span', 'gravedad-mobile-meta', 'Acciones'), actions(record));
      card.append(header, value, footer);
      return card;
    }

    function showAlert(message, type = 'danger', inForm = false) {
      const target = el(inForm ? 'mensajeFeedback' : 'mensajePaginaGravedad');
      target.className = `alert alert-${type}`;
      target.textContent = message;
    }

    function hideAlert(inForm = false) {
      const target = el(inForm ? 'mensajeFeedback' : 'mensajePaginaGravedad');
      target.className = 'alert d-none';
      target.textContent = '';
    }

    function render() {
      const query = el('buscarGravedad').value.trim().toLocaleLowerCase('es');
      const filtered = state.records.filter(record => [record.id_gravedad, record.nivel_gravedad, levelFor(record).label, formatPercent(record), statusLabel(record)].join(' ').toLocaleLowerCase('es').includes(query));
      el('contadorRegistros').textContent = `(${state.records.length})`;
      el('contadorRegistros').setAttribute('aria-label', `${state.records.length} registros`);
      el('resumenGravedad').textContent = state.loading ? 'Cargando registros…' : state.error ? 'No se pudo actualizar el listado.' : `Mostrando ${filtered.length} de ${state.records.length} ${state.records.length === 1 ? 'registro' : 'registros'}`;
      refreshButton.disabled = state.loading;
      recordsElement.setAttribute('aria-busy', String(state.loading));
      const status = el('estadoListadoGravedad');
      status.replaceChildren();
      status.hidden = !state.loading && !state.error && filtered.length > 0;
      recordsElement.hidden = !status.hidden;
      if (state.loading) {
        const spinner = node('span', 'spinner-border spinner-border-sm me-2');
        spinner.setAttribute('aria-hidden', 'true');
        status.append(spinner, document.createTextNode('Cargando niveles…'));
      } else if (state.error) {
        status.append(node('p', 'mb-3', state.error));
        const retry = node('button', 'btn gravedad-secondary', 'Reintentar');
        retry.type = 'button';
        retry.addEventListener('click', loadRecords);
        status.append(retry);
      } else if (!filtered.length) {
        status.append(node('p', 'mb-0', state.records.length ? 'No se encontraron coincidencias.' : 'No hay niveles de gravedad registrados.'));
      }
      const rows = document.createDocumentFragment();
      const cards = document.createDocumentFragment();
      if (!state.loading && !state.error) filtered.forEach(record => { rows.append(tableRow(record)); cards.append(mobileRecord(record)); });
      el('cuerpoTabla').replaceChildren(rows);
      el('tarjetasGravedad').replaceChildren(cards);
    }

    async function request(url, options = {}) {
      const response = await fetch(url, options);
      const isJson = (response.headers.get('content-type') || '').includes('application/json');
      if (!isJson) throw new Error('Respuesta inesperada del servidor. Comprueba tu sesión e inténtalo de nuevo.');
      const data = await response.json();
      if (!response.ok) throw new Error(data?.message || 'No se pudo completar la solicitud.');
      return data;
    }

    async function loadRecords() {
      const version = ++state.loadVersion;
      state.loading = true;
      state.error = '';
      render();
      try {
        const data = await request('/api/gravedad/listar');
        if (!Array.isArray(data) || data.some(record => !record || typeof record !== 'object' || record.id_gravedad == null)) throw new Error('El servidor devolvió un listado no válido.');
        if (version === state.loadVersion) state.records = data;
      } catch (error) {
        if (version === state.loadVersion) state.error = 'No se pudieron cargar los niveles. Comprueba tu conexión o sesión e inténtalo de nuevo.';
        console.error('Error al cargar gravedades:', error);
      } finally {
        if (version === state.loadVersion) { state.loading = false; render(); }
      }
    }

    function updateFormLevel() {
      const input = el('criticidad');
      const badge = el('riesgoBadge');
      const valid = input.value.trim() !== '' && input.checkValidity();
      const level = valid ? (Number(input.value) <= 50 ? LEVELS.low : LEVELS.high) : null;
      badge.className = level ? `badge gravedad-state ${level.className}` : 'badge gravedad-state';
      badge.textContent = level ? level.label : 'Sin datos';
    }

    function openModal(element, trigger) {
      modalTrigger = trigger;
      window.bootstrap.Modal.getOrCreateInstance(element).show();
    }

    function resetForm() {
      form.reset();
      el('id_gravedad').value = '';
      el('modalTitle').textContent = 'Nuevo Nivel de Gravedad';
      el('textoBotonGuardar').textContent = 'Registrar';
      form.classList.remove('was-validated');
      hideAlert(true);
      updateFormLevel();
    }

    async function showRecord(id, editing, trigger) {
      if (state.saving) return;
      const version = ++state.detailVersion;
      trigger.disabled = true;
      hideAlert();
      try {
        const record = await request(`/api/gravedad/obtener/${encodeURIComponent(id)}`);
        if (version !== state.detailVersion) return;
        if (!record || record.id_gravedad == null) throw new Error('No se encontró el registro.');
        if (editing) {
          resetForm();
          el('modalTitle').textContent = 'Editar Nivel de Gravedad';
          el('id_gravedad').value = record.id_gravedad;
          el('criticidad').value = record.criticidad ?? '';
          el('estado').checked = Number(record.estado) === 1;
          el('textoBotonGuardar').textContent = 'Actualizar';
          updateFormLevel();
          openModal(modalElement, trigger);
        } else {
          const list = el('detallesGravedadList');
          list.replaceChildren();
          [['ID', record.id_gravedad], ['Nivel de Gravedad', levelFor(record).label], ['Criticidad', formatPercent(record)], ['Estado', statusLabel(record)]].forEach(([title, value]) => {
            list.append(node('dt', 'col-sm-4', title), node('dd', 'col-sm-8', value));
          });
          openModal(detailsElement, trigger);
        }
      } catch (error) {
        if (version === state.detailVersion) showAlert(error.message || 'Error al obtener el nivel.');
      } finally { trigger.disabled = false; }
    }

    async function deactivate(id) {
      if (pendingDeactivations.has(id)) return;
      if (!window.confirm('¿Está seguro de desactivar este nivel de gravedad? No se eliminará físicamente.')) return;
      pendingDeactivations.add(id);
      hideAlert();
      render();
      try {
        const data = await request(`/api/gravedad/eliminar/${encodeURIComponent(id)}`, { method: 'DELETE' });
        if (!data?.success) throw new Error(data?.message || 'No se pudo desactivar el nivel.');
        showAlert(data.message || 'Nivel desactivado correctamente.', 'success');
        await loadRecords();
      } catch (error) { showAlert(error.message || 'Error de conexión.'); }
      finally { pendingDeactivations.delete(id); render(); refreshButton.focus(); }
    }

    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      if (state.saving) return;
      if (!form.checkValidity()) {
        form.classList.add('was-validated');
        form.querySelector(':invalid')?.focus();
        return;
      }
      const id = el('id_gravedad').value;
      const value = Number(el('criticidad').value);
      const payload = { nivel_gravedad: value <= 50 ? LEVELS.low.api : LEVELS.high.api, criticidad: value, estado: el('estado').checked ? 1 : 0 };
      state.saving = true;
      saveButton.disabled = true;
      el('camposGravedad').disabled = true;
      el('spinnerGuardarGravedad').hidden = false;
      el('textoBotonGuardar').textContent = 'Guardando…';
      form.setAttribute('aria-busy', 'true');
      hideAlert(true);
      try {
        const data = await request(id ? `/api/gravedad/actualizar/${encodeURIComponent(id)}` : '/api/gravedad/registrar', {
          method: id ? 'PUT' : 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
        });
        if (!data?.success) throw new Error(data?.message || 'No se pudo guardar el nivel.');
        state.saving = false;
        window.bootstrap.Modal.getOrCreateInstance(modalElement).hide();
        showAlert(data.message || 'Nivel guardado correctamente.', 'success');
        await loadRecords();
      } catch (error) { showAlert(error.message || 'Error de conexión.', 'danger', true); }
      finally {
        state.saving = false;
        saveButton.disabled = false;
        el('camposGravedad').disabled = false;
        el('spinnerGuardarGravedad').hidden = true;
        el('textoBotonGuardar').textContent = id ? 'Actualizar' : 'Registrar';
        form.removeAttribute('aria-busy');
      }
    });

    el('btnNuevoGravedad').addEventListener('click', function () {
      if (state.saving) return;
      ++state.detailVersion;
      resetForm();
      openModal(modalElement, this);
    });
    el('buscarGravedad').addEventListener('input', render);
    refreshButton.addEventListener('click', loadRecords);
    el('criticidad').addEventListener('input', updateFormLevel);
    modalElement.addEventListener('shown.bs.modal', () => el('criticidad').focus());
    modalElement.addEventListener('hide.bs.modal', event => { if (state.saving) event.preventDefault(); });
    [modalElement, detailsElement].forEach(modal => modal.addEventListener('hidden.bs.modal', () => {
      (modalTrigger?.isConnected ? modalTrigger : refreshButton).focus();
    }));
    recordsElement.addEventListener('click', event => {
      const button = event.target.closest('button[data-action]');
      if (!button || button.disabled) return;
      const id = button.dataset.id;
      if (button.dataset.action === 'deactivate') deactivate(id);
      else showRecord(id, button.dataset.action === 'edit', button);
    });
    loadRecords();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initGravedad);
  else initGravedad();
})();
