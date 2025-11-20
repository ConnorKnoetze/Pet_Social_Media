(function () {
  const BREAKPOINT = 1300;
  const content = document.getElementById('contentPanel');
  const panels = {
    userPanel: document.getElementById('userPanel'),
    commentsPanel: document.getElementById('commentsPanel'),
    contentPanel: content
  };
  let lastMobile = null;

  function isMobile() { return window.innerWidth <= BREAKPOINT; }
  function isActive(id) { return panels[id] && panels[id].classList.contains('active'); }
  function isHidden(id) { return panels[id].classList.contains('hidden'); }

  function mobileActivate(id) {
    Object.keys(panels).forEach(pid => {
      const p = panels[pid];
      if (pid === id) {
        p.classList.add('active');
        p.classList.remove('hidden');
        p.setAttribute('aria-hidden','false');
      } else if (pid !== 'contentPanel') {
        p.classList.remove('active');
        p.classList.add('hidden');
        p.setAttribute('aria-hidden','true');
      }
    });
    // Blur removed: no class toggling
  }

  function wideSet(id, show) {
    const p = panels[id];
    if (!p || id === 'contentPanel') return;
    p.classList.toggle('hidden', !show);
    p.setAttribute('aria-hidden', String(!show));
    document.querySelectorAll('[data-panel="'+id+'"]').forEach(b => {
      b.setAttribute('aria-expanded', String(show));
    });
  }

  function init() {
    const mobile = isMobile();
    if (mobile === lastMobile) return;
    lastMobile = mobile;
    if (mobile) {
      Object.keys(panels).forEach(pid => {
        panels[pid].classList.remove('hidden','active');
        panels[pid].setAttribute('aria-hidden', pid === 'contentPanel' ? 'false' : 'true');
      });
      mobileActivate('contentPanel');
    } else {
      content.classList.remove('active','hidden');
      content.setAttribute('aria-hidden','false');
      ['userPanel','commentsPanel'].forEach(pid => {
        panels[pid].classList.remove('active');
        panels[pid].classList.add('hidden');
        panels[pid].setAttribute('aria-hidden','true');
      });
    }
  }

  document.addEventListener('click', e => {
    const btn = e.target.closest('button[data-panel]');
    if (!btn) return;
    const panelId = btn.dataset.panel;
    const action = btn.dataset.action || 'toggle';

    if (isMobile()) {
      if (panelId === 'contentPanel') { mobileActivate('contentPanel'); return; }
      if ((action === 'toggle' || action === 'hide') && isActive(panelId)) {
        mobileActivate('contentPanel');
      } else if (action === 'hide') {
        mobileActivate('contentPanel');
      } else {
        mobileActivate(panelId);
      }
      return;
    }

    if (panelId === 'contentPanel') return;
    if (action === 'toggle') {
      wideSet(panelId, isHidden(panelId));
    } else if (action === 'show') {
      wideSet(panelId, true);
    } else if (action === 'hide') {
      wideSet(panelId, false);
    }
  });

  window.addEventListener('resize', init);
  init();
})();