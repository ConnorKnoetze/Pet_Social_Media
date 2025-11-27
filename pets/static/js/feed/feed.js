(function() {
  const MOBILE_QUERY = '(max-width:520px)';
  const OVERLAY_QUERY = '(max-width:1300px)'; // panels overlay at this width in CSS
  let mobileCloseBtn = null;

  function isMobileView() {
    return window.matchMedia(MOBILE_QUERY).matches;
  }
  function isOverlayView() {
    return window.matchMedia(OVERLAY_QUERY).matches;
  }

  function showContentPanel() {
    const cp = document.getElementById('contentPanel');
    if (!cp) return;
    cp.classList.remove('hidden');
    cp.classList.add('active');
    cp.setAttribute('aria-hidden', 'false');
  }

  function hideOverlay(id) {
    const p = document.getElementById(id);
    if (!p) return;
    p.classList.remove('active');
    p.classList.add('hidden');
    p.setAttribute('aria-hidden', 'true');
  }

  // Only used when we want exclusivity
  function hideOtherOverlays(exceptId) {
    ['userPanel', 'commentsPanel'].forEach(id => {
      if (id !== exceptId) hideOverlay(id);
    });
  }

  function showOverlay(id) {
    const p = document.getElementById(id);
    if (!p) return;

    // Close the other panel only on smaller/overlay screens
    if (isOverlayView()) {
      hideOtherOverlays(id);
    }

    if (isMobileView()) {
      // Mobile: show panel and hide content
      p.classList.remove('hidden');
      p.classList.add('active');
      p.setAttribute('aria-hidden', 'false');

      const cp = document.getElementById('contentPanel');
      if (cp) {
        cp.classList.add('hidden');
        cp.setAttribute('aria-hidden', 'true');
      }

      toggleMobileClose(true);
    } else {
      // Tablet/desktop: do not force-hide content; just show this panel
      p.classList.remove('hidden');
      p.classList.add('active');
      p.setAttribute('aria-hidden', 'false');
    }
  }

  function mobileCloseHandler() {
    hideOverlay('userPanel');
    hideOverlay('commentsPanel');
    showContentPanel();
    toggleMobileClose(false);
  }

  function ensureMobileCloseBtn() {
    if (mobileCloseBtn) return mobileCloseBtn;
    const leftButtons = document.querySelector('.left-buttons');
    if (!leftButtons) return null;

    mobileCloseBtn = document.createElement('button');
    mobileCloseBtn.id = 'mobileCloseBtn';
    mobileCloseBtn.className = 'side-btn';
    mobileCloseBtn.type = 'button';
    mobileCloseBtn.setAttribute('aria-label', 'Close overlays');
    mobileCloseBtn.innerHTML = '<img class="button_image" src="/static/images/assets/close.png" alt="Close" />';
    mobileCloseBtn.addEventListener('click', mobileCloseHandler);

    leftButtons.insertBefore(mobileCloseBtn, leftButtons.firstChild);
    return mobileCloseBtn;
  }

  function toggleMobileClose(show) {
    const btn = ensureMobileCloseBtn();
    if (!btn) return;
    btn.classList.toggle('show', show);
  }

  // Toggle handler
  window.mobileActivate = function(id) {
    const panel = document.getElementById(id);
    if (!panel) return;

    if (panel.classList.contains('active')) {
      hideOverlay(id);
      if (isMobileView()) mobileCloseHandler();
      return;
    }

    showOverlay(id);
  };

  document.addEventListener('click', e => {
    const btn = e.target.closest('[data-panel]');
    if (!btn) return;

    const panelId = btn.getAttribute('data-panel');
    const action = btn.getAttribute('data-action') || 'toggle';

    if (action === 'toggle') return mobileActivate(panelId);
    if (action === 'show') return showOverlay(panelId);
    if (action === 'hide') {
      hideOverlay(panelId);
      if (isMobileView()) mobileCloseHandler();
    }
  }, { passive: true });

  window.addEventListener('resize', () => {
    if (!isMobileView()) toggleMobileClose(false);
  });

  document.addEventListener('DOMContentLoaded', ensureMobileCloseBtn);
})();

(function themeInit() {
  const root = document.documentElement;
  const KEY = 'themePreference';
  const mq = window.matchMedia('(prefers-color-scheme: dark)');

  function systemTheme() {
    return mq.matches ? 'dark' : 'light';
  }

  function apply(theme) {
    const finalTheme = theme === 'system' ? systemTheme() : theme;
    root.setAttribute('data-theme', finalTheme);
  }

  function loadPref() {
    return localStorage.getItem(KEY) || 'system';
  }

  function cyclePref(current) {
    if (current === 'system') return 'dark';
    if (current === 'dark') return 'light';
    return 'system';
  }

  function init() {
    apply(loadPref());
  }

  mq.addEventListener('change', () => {
    if (loadPref() === 'system') apply('system');
  });

  init();
})();