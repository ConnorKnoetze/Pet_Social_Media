document.addEventListener('DOMContentLoaded', () => {
  const video = document.querySelector('.video');
  if (!video) return;

  (function preventIOSZoom() {
    let lastTouchEnd = 0;
    document.addEventListener('touchend', (e) => {
      const now = Date.now();
      if (now - lastTouchEnd <= 300) e.preventDefault();
      lastTouchEnd = now;
    }, { passive: false });
    document.addEventListener('gesturestart', e => e.preventDefault());
    document.addEventListener('gesturechange', e => e.preventDefault());
    document.addEventListener('gestureend', e => e.preventDefault());
  })();

  video.style.cursor = 'pointer';
  video.style.touchAction = 'manipulation';

  const NORMAL_RATE = 1;
  const FAST_RATE = 2;
  const HOLD_THRESHOLD = 350; // slightly higher for reliability
  const DOUBLE_TAP_THRESHOLD = 300;
  video.playbackRate = NORMAL_RATE;

  let hold = false;
  let holdTimer = null;
  let lastTapTime = 0;

  function startHoldTimer() {
    hold = false;
    clearTimeout(holdTimer);
    holdTimer = setTimeout(() => {
      hold = true;
      if (video.paused) video.play();
      video.playbackRate = FAST_RATE;
    }, HOLD_THRESHOLD);
  }

  function restartVideo() {
    video.currentTime = 0;
    if (video.paused) video.play();
  }

  function handleTap() {
    const now = Date.now();
    if (now - lastTapTime < DOUBLE_TAP_THRESHOLD) {
      lastTapTime = 0;
      restartVideo();
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
      handleTap();
    }
  }

  function cancelHold() {
    clearTimeout(holdTimer);
    if (hold) video.playbackRate = NORMAL_RATE;
    // Do NOT treat as a tap
  }

  video.addEventListener('pause', () => video.classList.add('paused'));
  video.addEventListener('play', () => video.classList.remove('paused'));

  video.addEventListener('pointerdown', startHoldTimer);
  video.addEventListener('pointerup', endPointer);
  video.addEventListener('pointercancel', cancelHold);
  video.addEventListener('pointerleave', cancelHold);

  video.addEventListener('dblclick', (e) => {
    e.preventDefault();
    restartVideo();
  });
});