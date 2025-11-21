document.addEventListener('DOMContentLoaded', () => {
  const video = document.querySelector('.video');
  if (!video) return;
  video.style.cursor = 'pointer';

  const NORMAL_RATE = 1;
  const FAST_RATE = 2;
  const HOLD_THRESHOLD = 250; // ms needed to count as hold
  video.playbackRate = NORMAL_RATE;

  let hold = false;
  let holdTimer = null;

  // Restart on double-click
  video.addEventListener('dblclick', () => {
    video.currentTime = 0;
    if (video.paused) video.play();
  });

  // Darken when paused
  video.addEventListener('pause', () => video.classList.add('paused'));
  video.addEventListener('play', () => video.classList.remove('paused'));

  video.addEventListener('pointerdown', () => {
    hold = false;
    clearTimeout(holdTimer);
    holdTimer = setTimeout(() => {
      hold = true;
      if (video.paused) video.play();
      video.playbackRate = FAST_RATE;
    }, HOLD_THRESHOLD);
  });

  function endPointer() {
    clearTimeout(holdTimer);
    if (!hold) {
      // Simple click: toggle play/pause
      video.paused ? video.play() : video.pause();
    } else {
      // Held: restore normal rate
      video.playbackRate = NORMAL_RATE;
    }
  }

  video.addEventListener('pointerup', endPointer);
});