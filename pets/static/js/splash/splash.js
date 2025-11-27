document.addEventListener('DOMContentLoaded', function () {
  const SPLASH_KEY = 'splash_shown_v1';
  const AUTO_HIDE_MS = 3200;
  const PROGRESS_UPDATE_MS = 40;

  const splash = document.getElementById('splash');
  const progress = document.getElementById('splash-progress');

  if (!splash) return;

  function hideSplash() {
    splash.classList.add('hidden');
    setTimeout(() => {
      if (splash && splash.parentNode) splash.parentNode.removeChild(splash);
    }, 420);
  }

  if (localStorage.getItem(SPLASH_KEY)) {
    // Already shown before
    if (splash && splash.parentNode) splash.parentNode.removeChild(splash);
    return;
  }

  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReduced) {
    setTimeout(() => {
      localStorage.setItem(SPLASH_KEY, '1');
      hideSplash();
    }, 600);
    return;
  }

  let elapsed = 0;
  const ticks = AUTO_HIDE_MS / PROGRESS_UPDATE_MS;
  const step = 100 / ticks;
  const timer = setInterval(() => {
    elapsed += PROGRESS_UPDATE_MS;
    const cur = parseFloat(progress.style.width) || 0;
    progress.style.width = Math.min(100, cur + step) + '%';
    if (elapsed >= AUTO_HIDE_MS) {
      clearInterval(timer);
      localStorage.setItem(SPLASH_KEY, '1');
      hideSplash();
    }
  }, PROGRESS_UPDATE_MS);

  document.addEventListener('keydown', function onKey(e) {
    if (e.key === 'Escape') {
      clearInterval(timer);
      localStorage.setItem(SPLASH_KEY, '1');
      hideSplash();
      document.removeEventListener('keydown', onKey);
    }
  });
});