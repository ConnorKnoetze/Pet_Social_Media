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

  // Prevent iOS double-tap zoom (once)
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
    const img = !video ? card.querySelector('img') : null;
    const media = video || img;
    if (!media) return;

    media.style.cursor = 'pointer';
    media.style.touchAction = 'manipulation';
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

    if (video) {
      const NORMAL_RATE = 1;
      const FAST_RATE = 2;
      const HOLD_THRESHOLD = 350;
      video.playbackRate = NORMAL_RATE;

      let hold = false;
      let holdTimer = null;

      function startHoldTimer() {
        hold = false;
        clearTimeout(holdTimer);
        holdTimer = setTimeout(() => {
          hold = true;
          if (video.paused) video.play();
          video.playbackRate = FAST_RATE;
        }, HOLD_THRESHOLD);
      }

      function handleTapVideo() {
        const now = Date.now();
        if (now - lastTapTime < DOUBLE_TAP_THRESHOLD) {
          lastTapTime = 0;
          likePost();
        } else {
          video.paused ? video.play() : video.pause();
          lastTapTime = now;
        }
      }

      function endPointer() {
        clearTimeout(holdTimer);
        if (hold) {
          video.playbackRate = NORMAL_RATE;
        } else {
          handleTapVideo();
        }
      }

      function cancelHold() {
        clearTimeout(holdTimer);
        if (hold) video.playbackRate = NORMAL_RATE;
      }

      video.addEventListener('pause', () => video.classList.add('paused'));
      video.addEventListener('play', () => video.classList.remove('paused'));

      video.addEventListener('pointerdown', startHoldTimer);
      video.addEventListener('pointerup', endPointer);
      video.addEventListener('pointercancel', cancelHold);
      video.addEventListener('pointerleave', cancelHold);

      video.addEventListener('dblclick', e => {
        e.preventDefault();
        likePost();
      });
    } else if (img) {
      // Image: only double-tap / dblclick like
      img.addEventListener('pointerup', () => handleTapForImage());
      img.addEventListener('dblclick', e => {
        e.preventDefault();
        likePost();
      });
    }
  });
});