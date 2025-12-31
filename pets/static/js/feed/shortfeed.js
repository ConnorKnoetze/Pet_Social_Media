document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('shortfeed');
  if (!container) return;

  let offset = container.querySelectorAll('.short-card').length;
  let loading = false;
  let hasMore = true;
  let batchSize = 16;
  const PREFETCH_THRESHOLD = 3;
  let activePostId = null;

  const DOUBLE_TAP_THRESHOLD = 150;
  const userPausedVideos = new WeakSet();
  const FLASH_MS = 800;

  function initLikeForCard(card) {
    if (!card || card.dataset.likeInit) return;
    const video = card.querySelector('video');
    const img = !video ? card.querySelector('img') : null;
    const media = video || img;
    if (!media) return;

    media.style.cursor = 'pointer';
    media.style.touchAction = 'manipulation';
    let lastTapTime = 0;
    let likeInProgress = false;

    function likePost() {
      if (likeInProgress) return;
      likeInProgress = true;
      const pid = card.dataset.id;
      createHeartBurst(card);
      sendLike(pid);
      setTimeout(() => { likeInProgress = false; }, DOUBLE_TAP_THRESHOLD);
    }

    if (video) {
      const pauseBtn = card.querySelector('.video-pause-button');
      let playBtn = card.querySelector('.video-play-button');
      if (!playBtn) {
        playBtn = document.createElement('span');
        playBtn.className = 'video-play-button';
        const icon = document.createElement('img');
        icon.src = '/static/images/assets/play-buttton.png';
        icon.alt = 'play-button';
        playBtn.appendChild(icon);
        (card.querySelector('.post-wrapper') || card).appendChild(playBtn);
      }

      function flashOverlay(btn) {
        if (!btn) return;
        btn.style.opacity = '1';
        btn.style.visibility = 'visible';
        btn.style.pointerEvents = 'none';
        clearTimeout(btn.__hideTimer);
        btn.__hideTimer = setTimeout(() => {
          btn.style.opacity = '0';
          btn.style.visibility = 'hidden';
        }, FLASH_MS);
      }

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

      async function handleTapVideo() {
        const now = Date.now();
        if (now - lastTapTime < DOUBLE_TAP_THRESHOLD) {
          lastTapTime = 0;
          likePost();
          return;
        }
        try {
          if (video.paused) await video.play(); else video.pause();
        } catch (err) { console.error('Video toggle failed', err); }
        lastTapTime = now;
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

      video.addEventListener('pause', () => {
        video.classList.add('paused');
        userPausedVideos.add(video);
        flashOverlay(pauseBtn);
      });
      video.addEventListener('play', () => {
        video.classList.remove('paused');
        userPausedVideos.delete(video);
        flashOverlay(playBtn);
      });
      video.addEventListener('pointerdown', startHoldTimer);
      video.addEventListener('pointerup', endPointer);
      video.addEventListener('pointercancel', cancelHold);
      video.addEventListener('pointerleave', cancelHold);
    } else if (img) {
      let isProcessing = false;
      let clickTimer = null;

      function handleImageTap() {
        if (isProcessing) return;
        const now = Date.now();
        const isDoubleTap = now - lastTapTime < DOUBLE_TAP_THRESHOLD;
        lastTapTime = now;
        if (isDoubleTap) {
          isProcessing = true;
          likePost();
          setTimeout(() => { isProcessing = false; }, DOUBLE_TAP_THRESHOLD);
        }
      }

      img.addEventListener('pointerup', handleImageTap);
      img.addEventListener('click', () => {
        if (clickTimer) {
          clearTimeout(clickTimer);
          clickTimer = null;
          return;
        }
        clickTimer = setTimeout(() => {
          clickTimer = null;
          const target = img.dataset.href || `/post/${card.dataset.id}`;
          window.location.href = target;
        }, DOUBLE_TAP_THRESHOLD);
      });
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
        <div class="engagement-metrics">
          <span class="engagement-item">❤️ ${escapeHtml(post.likes_count)}</span>
          <span class="engagement-item">💬 ${escapeHtml(post.comments_count)}</span>
        </div>
        <div class="post-info">
          <p class="bio">${escapeHtml(post.caption)}</p>
          <small class="created-at">Posted: ${escapeHtml(timeago(post.created_at))}</small>
        </div>
      </div>
    `;
    container.appendChild(art);
    initLikeForCard(art);
    if (window.initCaptions) window.initCaptions(art);
  }

  function mediaMarkup(p) {
    if (p.media_type === 'video') {
      return `<video autoplay loop muted playsinline controlslist="nodownload nofullscreen noplaybackrate" disablepictureinpicture>
        <source src="${escapeHtml(p.media_path)}" type="video/mp4">
      </video>`;
    }
    // no anchor: use data-href so clicks are handled programmatically
    return `<img class="post-link" data-href="/post/${p.id}" src="${escapeHtml(p.media_path)}" alt="Post image">`;
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
        if (!vid.paused && !vid.ended) return;
        if (!userPausedVideos.has(vid)) {
          vid.play().catch(() => {});
        }
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