(function() {
  const LINES = 1;

  function applyClamp(el) {
    el.classList.add('clamped');
  }

  function removeClamp(el) {
    el.classList.remove('clamped');
  }

  function createToggle(el) {
    if (el.nextElementSibling && el.nextElementSibling.classList.contains('see-more-btn')) return;
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'see-more-btn';
    btn.textContent = 'See more';
    btn.addEventListener('click', () => {
      const expanded = el.classList.toggle('expanded');
      btn.textContent = expanded ? 'See less' : 'See more';
    });
    el.insertAdjacentElement('afterend', btn);
  }

  function removeToggle(el) {
    const next = el.nextElementSibling;
    if (next && next.classList.contains('see-more-btn')) next.remove();
    el.classList.remove('expanded');
  }

  function needsClampSingleLine(el) {
    // Ensure layout applied; clientWidth is layout-dependent
    // Add a tiny tolerance for sub-pixel differences
    return el.scrollWidth > el.clientWidth + 1;
  }

  function processBio(el) {
    if (!el) return;

    // If element not attached to DOM yet, retry later
    if (!el.isConnected) {
      scheduleProcess(el);
      return;
    }

    // If element hidden (not in layout) skip — caller can re-run later.
    if (el.offsetParent === null) {
      scheduleProcess(el);
      return;
    }

    // If layout hasn't settled and width is zero, wait a frame or two
    if (el.getBoundingClientRect().width === 0 || el.clientWidth === 0) {
      scheduleProcess(el);
      return;
    }

    // Reset any previous clamp/expanded state to measure full content size
    el.classList.remove('clamped', 'expanded');

    // Force layout and measure full size
    const fullHeight = el.scrollHeight;
    const fullWidth = el.scrollWidth;

    // Apply clamp
    applyClamp(el);

    // Force layout after clamp
    const clampedRect = el.getBoundingClientRect();
    const clampedHeight = clampedRect.height || el.offsetHeight;

    // Decide if clamp is needed:
    let isTruncated = false;
    if (LINES === 1) {
      // For single-line clamps, width overflow is the most reliable indicator
      isTruncated = needsClampSingleLine(el);
    } else {
      // For multi-line use height comparison
      isTruncated = fullHeight > clampedHeight + 1;
    }

    if (!isTruncated) {
      // Not truncated: remove clamp and any toggle
      removeClamp(el);
      removeToggle(el);
      return;
    }

    // Text is truncated — ensure toggle exists (leave clamped)
    createToggle(el);
  }

  function scheduleProcess(el) {
    // Allow multiple frames for the browser to apply styles/layout when nodes are injected.
    // Use a small chain of RAFs to give the browser time to layout media/fonts.
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        requestAnimationFrame(() => processBio(el));
      });
    });
  }

  function attachMediaReadyHooks(el) {
    // Find media for the containing post, if any
    const post = el.closest('.short-card, .post, article');
    if (!post) return false;
    const media = post.querySelector('img, video');
    if (!media) return false;

    if (media.tagName.toLowerCase() === 'img') {
      if (!media.complete || media.naturalWidth === 0) {
        media.addEventListener('load', () => scheduleProcess(el), { once: true });
        media.addEventListener('error', () => scheduleProcess(el), { once: true });
        return true;
      }
    } else if (media.tagName.toLowerCase() === 'video') {
      // If metadata isn't loaded yet, wait for it
      if (media.readyState < 1) { // HAVE_METADATA
        media.addEventListener('loadedmetadata', () => scheduleProcess(el), { once: true });
        media.addEventListener('loadeddata', () => scheduleProcess(el), { once: true });
        media.addEventListener('error', () => scheduleProcess(el), { once: true });
        return true;
      }
    }
    return false;
  }

  function initCaptions(root = document) {
    const list = (root.querySelectorAll ? root.querySelectorAll('.bio') : []);
    list.forEach(el => {
      // If media is present and not ready, attach hooks so we re-run after it loads.
      const hooked = attachMediaReadyHooks(el);
      // Always schedule an initial measurement; media hooks will re-run when needed.
      scheduleProcess(el);
      // As an extra safety for dynamically inserted nodes that may not be connected yet:
      if (!el.isConnected) {
        // Small timeout fallback in case media events don't fire
        setTimeout(() => scheduleProcess(el), 200);
      }
    });
  }

  document.addEventListener('DOMContentLoaded', () => initCaptions(document));
  // expose for callers who inject posts via API to re-run on new nodes:
  window.initCaptions = initCaptions;
})();