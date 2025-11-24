document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('shortfeed');
  if (!container) return;

  let offset = container.querySelectorAll('.short-card').length;
  let loading = false;
  let hasMore = true;
  let batchSize = 16;
  const PREFETCH_THRESHOLD = 3;
  let activePostId = null;

  const DOUBLE_TAP_THRESHOLD = 300;

  function sendLike(postId) {
    if (!postId) return;
    fetch(`/api/posts/${encodeURIComponent(postId)}/like`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: '{}'
    }).catch(err => console.error('Like failed', err));
  }

  function createHeartBurst(card) {
    const heart = document.createElement('div');
    heart.textContent = '❤';
    Object.assign(heart.style, {
      position: 'absolute',
      left: '50%',
      top: '50%',
      transform: 'translate(-50%,-50%) scale(0.3)',
      fontSize: '4rem',
      color: 'rgba(255,80,120,0.95)',
      pointerEvents: 'none',
      transition: 'transform 420ms cubic-bezier(.2,.9,.3,1), opacity 420ms',
      opacity: '1',
      zIndex: 40,
      textShadow: '0 6px 20px rgba(0,0,0,0.35)'
    });
    if (getComputedStyle(card).position === 'static') {
      card.style.position = 'relative';
    }
    card.appendChild(heart);
    requestAnimationFrame(() => { heart.style.transform = 'translate(-50%,-60%) scale(1)'; });
    setTimeout(() => { heart.style.opacity = '0'; heart.style.transform = 'translate(-50%,-80%) scale(1.2)'; }, 420);
    setTimeout(() => heart.remove(), 900);
  }

  function initLikeForCard(card) {
    if (!card || card.dataset.likeInit) return;
    const video = card.querySelector('video');
    const img = !video ? card.querySelector('img') : null;
    const media = video || img;
    if (!media) return;

    media.style.cursor = 'pointer';
    media.style.touchAction = 'manipulation';
    let lastTapTime = 0;

    function likePost() {
      const pid = card.dataset.id;
      createHeartBurst(card);
      sendLike(pid);
    }

    function handleImageTap() {
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
      video.addEventListener('dblclick', e => { e.preventDefault(); likePost(); });
    } else if (img) {
      img.addEventListener('pointerup', handleImageTap);
      img.addEventListener('dblclick', e => { e.preventDefault(); likePost(); });
    }

    card.dataset.likeInit = '1';
  }


  function timeago(iso) {
    if (!iso) return '';
    const dt = new Date(iso);
    if (isNaN(dt)) return '';
    const now = new Date();
    let diffSec = (now - dt) / 1000;
    if (diffSec < 60) return 'Just now';
    const mins = diffSec / 60;
    if (mins < 60) return `${Math.floor(mins)}m`;
    const hrs = mins / 60;
    if (hrs < 24) return `${Math.floor(hrs)}h`;
    const days = hrs / 24;
    if (days < 7) return `${Math.floor(days)}d`;
    const d = dt.getDate().toString().padStart(2,'0');
    const m = (dt.getMonth()+1).toString().padStart(2,'0');
    const y = dt.getFullYear().toString().slice(-2);
    return `${d}/${m}/${y}`;
  }

  async function loadBatch() {
    if (loading || !hasMore) return;
    loading = true;
    try {
      const res = await fetch(`/api/feed?offset=${offset}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      batchSize = data.batch_size || batchSize;
      hasMore = data.has_more;
      data.posts.forEach(addCard);
      offset = data.next_offset;
      attachObservers();
    } catch (err) {
      console.error('Load batch failed:', err);
    } finally {
      loading = false;
    }
  }

  function addCard(post) {
    const art = document.createElement('article');
    art.className = 'post short-card';
    art.dataset.id = post.id;
    art.dataset.userId = post.user_id || 0;
    art.innerHTML = `
      <div class="post-wrapper">
        ${mediaMarkup(post)}
        <div class="post-info">
          <p class="bio">${escapeHtml(post.caption)}</p>
          <small class="created-at">Posted: ${escapeHtml(timeago(post.created_at))}</small>
        </div>
      </div>
    `;
    container.appendChild(art);
    initLikeForCard(art); // initialize like handlers for new card
  }

  function mediaMarkup(p) {
    if (p.media_type === 'video') {
      return `<video autoplay loop muted playsinline controlslist="nodownload nofullscreen noplaybackrate" disablepictureinpicture>
        <source src="${escapeHtml(p.media_path)}" type="video/mp4">
      </video>`;
    }
    return `<img src="${escapeHtml(p.media_path)}" alt="Post image">`;
  }

  function escapeHtml(str='') {
    return str.replace(/[&<>"']/g, ch => ({
      '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
    }[ch]));
  }

  const playObserver = new IntersectionObserver(entries => {
    entries.forEach(e => {
      const vid = e.target.querySelector('video');
      if (!vid) return;
      if (e.isIntersecting) {
        if (vid.paused) vid.play().catch(()=>{});
      } else if (!vid.paused) {
        vid.pause();
      }
    });
  }, { threshold: [0.6] });

  const activeObserver = new IntersectionObserver(entries => {
    let best = null;
    entries.forEach(e => {
      if (e.isIntersecting) {
        if (!best || e.intersectionRatio > best.intersectionRatio) best = e;
      }
    });
    if (best) {
      const postId = best.target.dataset.id;
      if (postId && postId !== activePostId) {
        activePostId = postId;
        if (window.setActivePostComments) window.setActivePostComments(postId);
        const userId = best.target.dataset.userId;
        if (userId && window.setActivePostUser) window.setActivePostUser(userId);
      }
    }
  }, { threshold: [0.6] });

  const prefetchObserver = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        prefetchObserver.unobserve(e.target);
        loadBatch();
      }
    });
  }, { threshold: [0.1] });

  function attachObservers() {
    const cards = [...container.querySelectorAll('.short-card')];
    cards.slice(-batchSize).forEach(c => {
      playObserver.observe(c);
      activeObserver.observe(c);
      initLikeForCard(c); // ensure existing/new cards are wired
    });
    const trigger = cards[cards.length - PREFETCH_THRESHOLD];
    if (trigger) prefetchObserver.observe(trigger);

    if (!activePostId) {
      const first = cards[0];
      if (first) {
        activePostId = first.dataset.id;
        if (window.setActivePostComments) window.setActivePostComments(activePostId);
        if (window.setActivePostUser && first.dataset.userId) {
          window.setActivePostUser(first.dataset.userId);
        }
      }
    }
  }

  container.addEventListener('scroll', () => {
    if (!hasMore || loading) return;
    const nearBottom = container.scrollTop + container.clientHeight >= container.scrollHeight - 200;
    if (nearBottom) loadBatch();
  });

  container.querySelectorAll('.short-card').forEach(card => {
    if (!card.dataset.userId) {
      card.dataset.userId = card.getAttribute('data-user-id') || '0';
    }
    initLikeForCard(card); // initialize for server-rendered cards
  });

  attachObservers();

  function currentCard() {
    return container.querySelector(`.short-card[data-id="${activePostId}"]`);
  }

  function scrollFeed(direction) {
    const cards = [...container.querySelectorAll('.short-card')];
    if (!cards.length) return;
    let idx = cards.indexOf(currentCard());
    if (idx < 0) idx = 0;
    if (direction === 'up') {
      idx = Math.max(0, idx - 1);
    } else {
      idx = Math.min(cards.length - 1, idx + 1);
      if (idx === cards.length - 1 && hasMore && !loading) {
        loadBatch();
      }
    }
    cards[idx].scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  const DOUBLE_UP_THRESHOLD = 280;
  let upClickTimer = null;

  document.addEventListener('click', e => {
    const btn = e.target.closest('[data-scroll]');
    if (!btn) return;
    const dir = btn.getAttribute('data-scroll');

    if (dir === 'up') {
      if (upClickTimer) {
        clearTimeout(upClickTimer);
        upClickTimer = null;
        container.scrollTo({ top: 0, behavior: 'smooth' });
        return;
      }
      upClickTimer = setTimeout(() => {
        scrollFeed('up');
        upClickTimer = null;
      }, DOUBLE_UP_THRESHOLD);
      return;
    }

    scrollFeed(dir === 'up' ? 'up' : 'down');
  }, { passive: true });
});