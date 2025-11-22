document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('shortfeed');
  if (!container) return;

  let offset = container.querySelectorAll('.short-card').length;
  let loading = false;
  let hasMore = true;
  let batchSize = 16;
  const PREFETCH_THRESHOLD = 3;
  let activePostId = null;

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
    art.innerHTML = `
      <h2>${escapeHtml(post.caption)}</h2>
      <small>${escapeHtml(post.created_at)}</small>
      ${mediaMarkup(post)}
    `;
    container.appendChild(art);
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
      } else {
        if (!vid.paused) vid.pause();
      }
    });
  }, { threshold: [0.6] });

  // Active post & comments observer
  const activeObserver = new IntersectionObserver(entries => {
    // Pick the entry with highest intersectionRatio that isIntersecting
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
        if (window.setActivePostComments) {
          window.setActivePostComments(postId);
        }
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
    });
    const trigger = cards[cards.length - PREFETCH_THRESHOLD];
    if (trigger) prefetchObserver.observe(trigger);

    // Ensure initial active if none
    if (!activePostId) {
      const first = cards[0];
      if (first) {
        activePostId = first.dataset.id;
        if (window.setActivePostComments) window.setActivePostComments(activePostId);
      }
    }
  }

  container.addEventListener('scroll', () => {
    if (!hasMore || loading) return;
    const nearBottom = container.scrollTop + container.clientHeight >= container.scrollHeight - 200;
    if (nearBottom) loadBatch();
  });

  attachObservers();
});