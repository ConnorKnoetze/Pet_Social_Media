// javascript
// Cleaned version with ONE mobile close handler

(function() {
  const MOBILE_QUERY = '(max-width:520px)';
  let mobileCloseBtn = null;

  function isMobileView() {
    return window.matchMedia(MOBILE_QUERY).matches;
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

  function showOverlay(id) {
    const p = document.getElementById(id);
    if (!p) return;

    if (isMobileView()) {
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
      p.classList.remove('hidden');
      p.classList.add('active');
      p.setAttribute('aria-hidden', 'false');
    }
  }

  // -----------------------------
  // ONE unified mobile close handler
  // -----------------------------
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
    mobileCloseBtn.innerText = '×';

    // ❗ All close logic here only
    mobileCloseBtn.addEventListener('click', mobileCloseHandler);

    leftButtons.insertBefore(mobileCloseBtn, leftButtons.firstChild);
    return mobileCloseBtn;
  }

  function toggleMobileClose(show) {
    const btn = ensureMobileCloseBtn();
    if (!btn) return;
    btn.classList.toggle('show', show);
  }

  // -----------------------------
  // Unified mobileActivate
  // -----------------------------
  window.mobileActivate = function(id) {
    const panel = document.getElementById(id);
    if (!panel) return;

    // If it's already open → close
    if (panel.classList.contains('active')) {
      hideOverlay(id);
      if (isMobileView()) mobileCloseHandler();
      return;
    }

    // Otherwise open
    if (isMobileView()) {
      showOverlay(id);
    } else {
      panel.classList.toggle('active');
      panel.classList.toggle('hidden');
      panel.setAttribute(
        'aria-hidden',
        panel.classList.contains('hidden') ? 'true' : 'false'
      );
    }
  };

  // Attach generic [data-panel] listener
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

  // Resize cleanup
  window.addEventListener('resize', () => {
    if (!isMobileView()) toggleMobileClose(false);
  });

  document.addEventListener('DOMContentLoaded', ensureMobileCloseBtn);
})();

(function themeInit() {
  const root = document.documentElement;
  const KEY = 'themePreference'; // values: 'light' | 'dark' | 'system'
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
    // Order: system -> dark -> light -> system
    if (current === 'system') return 'dark';
    if (current === 'dark') return 'light';
    return 'system';
  }

  function init() {
    apply(loadPref());
  }

  // React to OS theme changes while in system mode
  mq.addEventListener('change', () => {
    if (loadPref() === 'system') apply('system');
  });

  init();
})();