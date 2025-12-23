
document.addEventListener('DOMContentLoaded', () => {
  const cards = document.querySelectorAll('.short-card');

  async function sendLike(postId) {
    if (!postId) return;
    try {
      await fetch(`/api/posts/${encodeURIComponent(postId)}/like`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
    } catch (err) {
      console.error('Like request failed', err);
    }
  }

  // Prevent iOS double-tap zoom
  (function preventIOSZoom() {
    let lastTouchEnd = 0;
    document.addEventListener('touchend', (e) => {
      const now = Date.now();
      if (now - lastTouchEnd <= 300) e.preventDefault();
      lastTouchEnd = now;
    }, { passive: false });
    ['gesturestart','gesturechange','gestureend'].forEach(ev =>
      document.addEventListener(ev, e => e.preventDefault())
    );
  })();

  const DOUBLE_TAP_THRESHOLD = 300;

  cards.forEach(card => {
    const video = card.querySelector('video');
    if (video) return; // video behavior handled elsewhere

    const img = card.querySelector('img');
    if (!img) return;

    img.style.cursor = 'pointer';
    img.style.touchAction = 'manipulation';
    let lastTapTime = 0;

    function likePost() {
      const pid = card.dataset.id || card.getAttribute('data-id');
      createHeartBurst(card);
      sendLike(pid);
    }

    function handleTapForImage() {
      const now = Date.now();
      if (now - lastTapTime < DOUBLE_TAP_THRESHOLD) {
        lastTapTime = 0;
        likePost();
      } else {
        lastTapTime = now;
      }
    }

    img.addEventListener('pointerup', handleTapForImage);
    img.addEventListener('dblclick', e => {
      e.preventDefault();
      likePost();
    });
  });
});