// javascript
(function() {
  const LINES = 1;

  function applyClamp(el) {
    el.classList.add('clamped');
  }

  function removeClamp(el) {
    el.classList.remove('clamped');
  }

  function setEngagementHidden(el, hide) {
    const wrapper = el.closest('.post-wrapper');
    const metrics = wrapper ? wrapper.querySelector('.engagement-metrics') : null;
    if (metrics) metrics.style.display = hide ? 'none' : '';
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
      setEngagementHidden(el, expanded);
    });
    el.insertAdjacentElement('afterend', btn);
  }

  function removeToggle(el) {
    const next = el.nextElementSibling;
    if (next && next.classList.contains('see-more-btn')) next.remove();
    el.classList.remove('expanded');
    setEngagementHidden(el, false);
  }

  function needsClampSingleLine(el) {
    return el.scrollWidth > el.clientWidth + 1;
  }

  function processBio(el) {
    if (!el) return;
    if (!el.isConnected || el.offsetParent === null || el.getBoundingClientRect().width === 0 || el.clientWidth === 0) {
      scheduleProcess(el);
      return;
    }

    el.classList.remove('clamped', 'expanded');
    setEngagementHidden(el, false);

    const fullHeight = el.scrollHeight;
    const fullWidth = el.scrollWidth;

    applyClamp(el);

    const clampedRect = el.getBoundingClientRect();
    const clampedHeight = clampedRect.height || el.offsetHeight;

    let isTruncated = false;
    if (LINES === 1) {
      isTruncated = needsClampSingleLine(el);
    } else {
      isTruncated = fullHeight > clampedHeight + 1;
    }

    if (!isTruncated) {
      removeClamp(el);
      removeToggle(el);
      return;
    }

    createToggle(el);
  }

  function scheduleProcess(el) {
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        requestAnimationFrame(() => processBio(el));
      });
    });
  }

  function attachMediaReadyHooks(el) {
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
      if (media.readyState < 1) {
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
      const hooked = attachMediaReadyHooks(el);
      scheduleProcess(el);
      if (!el.isConnected) {
        setTimeout(() => scheduleProcess(el), 200);
      }
    });
  }

  document.addEventListener('DOMContentLoaded', () => initCaptions(document));
  window.initCaptions = initCaptions;
})();