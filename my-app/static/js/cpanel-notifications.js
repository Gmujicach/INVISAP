(function () {
  'use strict';

  window.__cpanelUtilityNotifications = true;

  function initCpanelNotifications() {
    var badge = document.getElementById('notif-badge');
    var countLabel = document.getElementById('notif-count-label');
    var summary = document.getElementById('notif-summary');
    var lista = document.getElementById('notif-lista');
    var status = document.getElementById('notif-status');
    var errorState = document.getElementById('notif-error');
    var emptyState = document.getElementById('notif-empty');
    var retryButton = document.getElementById('notif-reintentar');
    var markAllButton = document.getElementById('notif-marcar-todas');
    var deleteAllButton = document.getElementById('notif-eliminar-todas');

    if (!lista) return;

    var monthNames = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
    var actionLabels = {
      crear: 'Creación',
      create: 'Creación',
      editar: 'Actualización',
      edit: 'Actualización',
      actualizar: 'Actualización',
      update: 'Actualización',
      eliminar: 'Eliminación',
      delete: 'Eliminación',
      revisar: 'Revisión',
      revisión: 'Revisión'
    };

    function escapeHtml(value) {
      var div = document.createElement('div');
      div.textContent = value == null ? '' : String(value);
      return div.innerHTML;
    }

    function parseDate(value) {
      if (!value) return null;
      var normalized = String(value).replace(' ', 'T');
      var parsed = new Date(normalized);
      return isNaN(parsed.getTime()) ? null : parsed;
    }

    function formatDateTime(value) {
      var date = parseDate(value);
      if (!date) return value || 'Fecha no disponible';

      var hours = date.getHours();
      var period = hours >= 12 ? 'PM' : 'AM';
      var hour12 = hours % 12 || 12;
      var day = String(date.getDate()).padStart(2, '0');
      var minutes = String(date.getMinutes()).padStart(2, '0');
      return day + ' ' + monthNames[date.getMonth()] + ' ' + date.getFullYear() + ' · ' +
        String(hour12).padStart(2, '0') + ':' + minutes + ' ' + period;
    }

    function relativeTime(value) {
      var date = parseDate(value);
      if (!date) return '';
      var difference = Math.max(0, (Date.now() - date.getTime()) / 1000);
      if (difference < 60) return 'hace un momento';
      if (difference < 3600) return 'hace ' + Math.floor(difference / 60) + ' min';
      if (difference < 86400) return 'hace ' + Math.floor(difference / 3600) + ' h';
      return 'hace ' + Math.floor(difference / 86400) + ' d';
    }

    function getTechnicalRoute(notification) {
      var candidates = [notification.mensaje, notification.enlace];
      for (var i = 0; i < candidates.length; i += 1) {
        var candidate = String(candidates[i] || '').trim();
        var match = candidate.match(/\b(GET|POST|PUT|PATCH|DELETE)\s+\/(?:[^\s]+)/i);
        if (match) return match[0];
      }
      return notification.enlace || 'Sin ruta asociada';
    }

    function normalizeTitle(notification) {
      var raw = String(notification.titulo || '').trim();
      var moduleName = String(notification.modulo || '').trim();
      var actor = String(notification.creado_por || '').trim();

      if (/\blogout\b/i.test(raw)) {
        return 'Cierre de sesión' + (actor ? ' — ' + actor : '');
      }
      if (/\blogin\b/i.test(raw)) {
        return 'Inicio de sesión' + (actor ? ' — ' + actor : '');
      }

      var actionMatch = raw.match(/^\s*([^:]+):\s*(.+)\s*$/);
      if (actionMatch) {
        var action = actionMatch[1].trim().toLowerCase();
        var subject = actionMatch[2].trim();
        var normalizedAction = actionLabels[action];
        if (normalizedAction) {
          return normalizedAction + (subject ? ' — ' + subject : '');
        }
      }

      return raw || moduleName || 'Nueva notificación';
    }

    function getPriority(notification, normalizedTitle) {
      var text = (normalizedTitle + ' ' + (notification.mensaje || '')).toLowerCase();
      if (/solicitud|revisi|pendiente|venc/.test(text)) return { label: 'Requiere atención', className: '' };
      if (/login|logout|sesión/.test(text)) return { label: 'Actividad', className: 'low' };
      return { label: 'Actualización', className: 'medium' };
    }

    function iconForModule(moduleName) {
      var module = String(moduleName || '').toLowerCase();
      if (module.indexOf('solicitud') !== -1) return 'card-checklist';
      if (module.indexOf('obra') !== -1) return 'house-gear';
      if (module.indexOf('usuario') !== -1 || module.indexOf('empleado') !== -1) return 'people-fill';
      if (module.indexOf('respaldo') !== -1) return 'download';
      if (module.indexOf('login') !== -1 || module.indexOf('seguridad') !== -1) return 'person-check-fill';
      return 'bell';
    }

    function iconClassForModule(moduleName) {
      var module = String(moduleName || '').toLowerCase();
      if (module.indexOf('obra') !== -1 || module.indexOf('evidencia') !== -1) return 'info';
      if (module.indexOf('login') !== -1 || module.indexOf('seguridad') !== -1) return 'auth';
      return '';
    }

    function friendlyDescription(notification) {
      var raw = String(notification.titulo || '').trim();
      var moduleName = String(notification.modulo || '').trim();
      var actionMatch = raw.match(/^\s*([^:]+):\s*(.+)\s*$/);
      var action = actionMatch ? actionMatch[1].trim().toLowerCase() : '';
      var subject = actionMatch ? actionMatch[2].trim() : moduleName;
      var normalized = String(actionLabels[action] || '').trim();
      var verb = '';
      if (normalized.indexOf('Creación') !== -1) verb = 'registró';
      else if (normalized.indexOf('Actualización') !== -1) verb = 'actualizó';
      else if (normalized.indexOf('Eliminación') !== -1) verb = 'eliminó';
      else if (normalized.indexOf('Revisión') !== -1) verb = 'revisó';
      else verb = 'actualizó';

      var noun = subject || moduleName || 'registro';
      var capitalized = noun.charAt(0).toUpperCase() + noun.slice(1);
      var singular = /s$/i.test(capitalized) ? capitalized.slice(0, -1) : capitalized;
      var article = '';
      if (verb === 'registró') article = 'una nueva ' + singular;
      else if (verb === 'actualizó') article = 'una ' + singular;
      else if (verb === 'eliminó') article = 'un ' + singular;
      else if (verb === 'revisó') article = 'una ' + singular;
      else article = singular;

      return 'Se ' + verb + ' ' + article;
    }

    function detailId(notificationId) {
      return 'notif-detalle-' + String(notificationId).replace(/[^a-zA-Z0-9_-]/g, '-');
    }

    function updateStatus(message, isError) {
      if (!status) return;
      status.textContent = message;
      status.classList.toggle('is-error', Boolean(isError));
    }

    function updateBadge(number) {
      var pending = Math.max(0, Number(number) || 0);
      if (badge) {
        badge.textContent = pending;
        badge.classList.toggle('d-none', pending === 0);
      }
      if (countLabel) countLabel.textContent = pending;
      if (summary) {
        summary.textContent = pending === 0
          ? 'No tienes notificaciones pendientes'
          : pending + ' notificaciones pendientes';
      }

      var trigger = document.getElementById('btn-notificaciones');
      if (trigger) {
        trigger.setAttribute('aria-label', pending === 0
          ? 'Abrir notificaciones'
          : 'Abrir notificaciones, ' + pending + ' pendientes');
      }
    }

    function showEmptyState() {
      lista.hidden = true;
      if (emptyState) emptyState.hidden = false;
      if (errorState) errorState.hidden = true;
    }

    function showErrorState() {
      lista.hidden = true;
      if (emptyState) emptyState.hidden = true;
      if (errorState) errorState.hidden = false;
      updateStatus('No se pudieron actualizar las notificaciones', true);
    }

    function showListState() {
      lista.hidden = false;
      if (emptyState) emptyState.hidden = true;
      if (errorState) errorState.hidden = true;
    }

    function renderEmptyMessage() {
      lista.innerHTML = '<li class="notification-empty"><i class="bi bi-check2-circle" aria-hidden="true"></i><strong>Todo al día</strong><span>No tienes notificaciones pendientes.</span></li>';
      showEmptyState();
    }

    function renderNotifications(notifications) {
      if (!notifications.length) {
        renderEmptyMessage();
        return;
      }

      var markup = notifications.map(function (notification) {
        var id = notification.id_notificacion;
        var normalizedTitle = normalizeTitle(notification);
        var priority = getPriority(notification, normalizedTitle);
        var detail = detailId(id);
        var unreadClass = Number(notification.leida) === 1 ? ' is-read' : ' notif-no-leida';
        var iconClass = iconClassForModule(notification.modulo);
        var message = notification.mensaje || 'Actualización registrada en el sistema.';
        var moduleName = notification.modulo || 'General';
        var formattedDate = formatDateTime(notification.fecha);
        var friendly = friendlyDescription(notification);

        return '<li class="list-group-item notification-item' + unreadClass + '" data-id="' + escapeHtml(id) + '" data-unread="' + (Number(notification.leida) === 1 ? 'false' : 'true') + '">' +
          '<span class="notification-icon ' + iconClass + '"><i class="bi bi-' + iconForModule(notification.modulo) + '" aria-hidden="true"></i></span>' +
          '<div class="notification-main">' +
            '<div class="notification-title">' + escapeHtml(normalizedTitle) + '</div>' +
            '<div class="notification-preview">' + escapeHtml(friendly) + '</div>' +
            '<div class="notification-message">' + escapeHtml(message) + '</div>' +
            '<div class="notification-meta">' +
              '<span class="notification-priority ' + priority.className + '">' + escapeHtml(priority.label) + '</span>' +
              '<time class="notification-date" datetime="' + escapeHtml(notification.fecha || '') + '">' + escapeHtml(formattedDate) + '</time>' +
            '</div>' +
            '<button type="button" class="notification-detail" data-notification-detail="true" aria-expanded="false" aria-controls="' + detail + '">' +
              '<i class="bi bi-info-circle" aria-hidden="true"></i><span>Ver detalles</span>' +
            '</button>' +
            '<div class="notification-details" id="' + detail + '" hidden>' +
              '<div class="notification-detail-row"><strong>Descripción:</strong> ' + escapeHtml(friendly) + '</div>' +
              '<div class="notification-detail-row"><strong>Módulo:</strong> ' + escapeHtml(moduleName) + '</div>' +
              '<div class="notification-detail-row"><strong>Fecha:</strong> ' + escapeHtml(formattedDate) + '</div>' +
            '</div>' +
          '</div>' +
          '<button type="button" class="notification-delete notif-eliminar" data-id="' + escapeHtml(id) + '" aria-label="Eliminar notificación: ' + escapeHtml(normalizedTitle) + '"><i class="bi bi-x-lg" aria-hidden="true"></i></button>' +
        '</li>';
      }).join('');

      lista.innerHTML = markup;
      showListState();
    }

    function markAsRead(id, item) {
      fetch('/notificaciones/marcar-leida/' + encodeURIComponent(id), { method: 'POST' })
        .then(function (response) {
          if (!response.ok) throw new Error('No se pudo marcar la notificación');
          return response.json();
        })
        .then(function (data) {
          if (data.status !== 'success') throw new Error('No se pudo marcar la notificación');
          updateBadge(data.no_leidas || 0);
          if (item) {
            item.dataset.unread = 'false';
            item.classList.remove('notif-no-leida');
            item.classList.add('is-read');
          }
          updateStatus('Notificación marcada como leída');
        })
        .catch(function () {
          updateStatus('No se pudo marcar la notificación', true);
        });
    }

    function deleteNotification(id, item) {
      fetch('/notificaciones/eliminar/' + encodeURIComponent(id), { method: 'POST' })
        .then(function (response) {
          if (!response.ok) throw new Error('No se pudo eliminar la notificación');
          return response.json();
        })
        .then(function (data) {
          if (data.status !== 'success') throw new Error('No se pudo eliminar la notificación');
          updateBadge(data.no_leidas || 0);
          if (item) item.remove();
          if (!lista.querySelector('.notification-item')) renderEmptyMessage();
          updateStatus('Notificación eliminada');
        })
        .catch(function () {
          updateStatus('No se pudo eliminar la notificación', true);
        });
    }

    function loadNotifications() {
      lista.setAttribute('aria-busy', 'true');
      updateStatus('Actualizando notificaciones…');
      fetch('/notificaciones/lista')
        .then(function (response) {
          if (!response.ok) throw new Error('No se pudieron cargar las notificaciones');
          return response.json();
        })
        .then(function (data) {
          if (data.status !== 'success') throw new Error('No se pudieron cargar las notificaciones');
          updateBadge(data.no_leidas || 0);
          renderNotifications(data.notificaciones || []);
          updateStatus(data.notificaciones && data.notificaciones.length ? 'Actualizado ' + relativeTime(data.notificaciones[0].fecha) : 'Todo al día');
        })
        .catch(function () {
          showErrorState();
        })
        .finally(function () {
          lista.setAttribute('aria-busy', 'false');
        });
    }

    lista.addEventListener('click', function (event) {
      var detailButton = event.target.closest('[data-notification-detail]');
      if (detailButton) {
        event.stopPropagation();
        var detail = document.getElementById(detailButton.getAttribute('aria-controls'));
        if (!detail) return;
        var willOpen = detail.hasAttribute('hidden');
        if (willOpen) detail.removeAttribute('hidden');
        else detail.setAttribute('hidden', '');
        detailButton.setAttribute('aria-expanded', String(willOpen));
        var label = detailButton.querySelector('span');
        if (label) label.textContent = willOpen ? 'Ocultar detalles' : 'Ver detalles';
        updateStatus(willOpen ? 'Detalles técnicos visibles' : 'Detalles técnicos ocultos');
        return;
      }

      if (event.target.closest('.notification-details')) return;

      var deleteButton = event.target.closest('.notif-eliminar');
      if (deleteButton) {
        event.stopPropagation();
        deleteNotification(deleteButton.dataset.id, deleteButton.closest('.notification-item'));
        return;
      }

      var item = event.target.closest('.notification-item');
      if (item && item.dataset.unread === 'true') markAsRead(item.dataset.id, item);
    });

    if (markAllButton) {
      markAllButton.addEventListener('click', function (event) {
        event.stopPropagation();
        markAllButton.disabled = true;
        fetch('/notificaciones/marcar-todas', { method: 'POST' })
          .then(function (response) {
            if (!response.ok) throw new Error('No se pudieron marcar todas');
            return response.json();
          })
          .then(function (data) {
            if (data.status !== 'success') throw new Error('No se pudieron marcar todas');
            updateBadge(data.no_leidas || 0);
            loadNotifications();
            updateStatus('Notificaciones marcadas como leídas');
          })
          .catch(function () {
            updateStatus('No se pudieron marcar todas las notificaciones', true);
          })
          .finally(function () {
            markAllButton.disabled = false;
          });
      });
    }

    if (deleteAllButton) {
      deleteAllButton.addEventListener('click', function (event) {
        event.stopPropagation();
        if (!window.confirm('¿Eliminar todas las notificaciones?')) return;
        deleteAllButton.disabled = true;
        fetch('/notificaciones/eliminar-todas', { method: 'POST' })
          .then(function (response) {
            if (!response.ok) throw new Error('No se pudieron eliminar todas');
            return response.json();
          })
          .then(function (data) {
            if (data.status !== 'success') throw new Error('No se pudieron eliminar todas');
            updateBadge(data.no_leidas || 0);
            loadNotifications();
            updateStatus('Todas las notificaciones fueron eliminadas');
          })
          .catch(function () {
            updateStatus('No se pudieron eliminar todas las notificaciones', true);
          })
          .finally(function () {
            deleteAllButton.disabled = false;
          });
      });
    }

    if (retryButton) retryButton.addEventListener('click', loadNotifications);

    loadNotifications();
    window.setInterval(loadNotifications, 30000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCpanelNotifications);
  } else {
    initCpanelNotifications();
  }
})();
