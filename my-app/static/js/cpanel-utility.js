(function () {
  'use strict';

  function initUtilityMenu() {
    var stage = document.getElementById('corner-topbar');
    if (!stage) return;

    var triggers = {
      notifications: document.getElementById('btn-notificaciones'),
      profile: document.getElementById('btn-mi-perfil')
    };
    var panels = {
      notifications: document.getElementById('notif-dropdown'),
      profile: document.getElementById('profile-dropdown')
    };
    var closeButtons = stage.querySelectorAll('[data-utility-close]');
    var lastTrigger = null;

    function isOpen(name) {
      return panels[name] && !panels[name].hasAttribute('hidden');
    }

    function setPanel(name, open) {
      var panel = panels[name];
      var trigger = triggers[name];
      if (!panel || !trigger) return;

      if (open) {
        panel.removeAttribute('hidden');
        panel.classList.add('show');
        trigger.setAttribute('aria-expanded', 'true');
      } else {
        panel.setAttribute('hidden', '');
        panel.classList.remove('show');
        trigger.setAttribute('aria-expanded', 'false');
      }
    }

    function closePanels(restoreFocus) {
      setPanel('notifications', false);
      setPanel('profile', false);
      if (restoreFocus && lastTrigger) lastTrigger.focus();
    }

    function togglePanel(name) {
      var shouldOpen = !isOpen(name);
      closePanels(false);
      if (shouldOpen) {
        setPanel(name, true);
        lastTrigger = triggers[name];
      }
    }

    Object.keys(triggers).forEach(function (name) {
      var trigger = triggers[name];
      if (!trigger) return;
      trigger.addEventListener('click', function () {
        togglePanel(name);
      });
    });

    closeButtons.forEach(function (button) {
      button.addEventListener('click', function () {
        closePanels(true);
      });
    });

    stage.addEventListener('click', function (event) {
      var configAction = event.target.closest('[data-utility-action="config"]');
      if (configAction) {
        closePanels(false);
        return;
      }

      if (event.target.closest('[data-utility-close]')) return;
      if (event.target.closest('[data-utility-panel]')) return;
    });

    document.addEventListener('click', function (event) {
      if (!stage.contains(event.target) && (isOpen('notifications') || isOpen('profile'))) {
        closePanels(true);
      }
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && (isOpen('notifications') || isOpen('profile'))) {
        event.preventDefault();
        closePanels(true);
      }
    });

    window.cpanelUtility = {
      close: function () {
        closePanels(false);
      }
    };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initUtilityMenu);
  } else {
    initUtilityMenu();
  }
})();
