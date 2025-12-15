(function () {
  const sizes = [
    [320, 568], [375, 667], [390, 844], [393, 852], [414, 896],
    [360, 640], [412, 915], [667, 375], [896, 414],
    [768, 1024], [1024, 768], [800, 1280],
    [1366, 768], [1440, 900], [1536, 864], [1600, 900],
    [1920, 1080], [2560, 1440], [3440, 1440], [3840, 2160]
  ];

  function pickSize(w, h) {
    // Find the smallest size that covers viewport; fallback to largest
    const target = sizes
      .filter(([sw, sh]) => sw >= w && sh >= h)
      .sort((a, b) => (a[0] * a[1]) - (b[0] * b[1]))[0] || sizes[sizes.length - 1];
    return target;
  }

  function applyBackground() {
    const vw = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
    const vh = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);

    // Account for DPR to avoid blurry backgrounds on high-DPI
    const w = Math.round(vw * window.devicePixelRatio);
    const h = Math.round(vh * window.devicePixelRatio);

    const [tw, th] = pickSize(w, h);

    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = prefersDark ? 'dark' : 'light';

    // Paths: `static/images/backgrounds/{theme}/{width}/...png`
    const url = `/static/images/backgrounds/${theme}/${tw}/${theme}_back_${tw}x${th}.png`;

    // Use CSS variable so your stylesheets can reference it
    document.documentElement.style.setProperty('--app-bg-image', `url("${url}")`);
    document.body.style.backgroundImage = `var(--app-bg-image)`;
    document.body.style.backgroundSize = 'cover';
    document.body.style.backgroundPosition = 'center';
    document.body.style.backgroundRepeat = 'no-repeat';
  }

  // Initial apply and updates
  applyBackground();
  window.addEventListener('resize', debounce(applyBackground, 150));
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyBackground);

  function debounce(fn, ms) {
    let t; return function () { clearTimeout(t); t = setTimeout(fn, ms); };
  }
})();