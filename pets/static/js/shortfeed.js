document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('shortfeed');
  if (!container) return;

  // Start after the initial batch rendered by the server
  let offset = container.querySelectorAll('.short-card').length;
  let loading = false;
  let hasMore = true;
  let batchSize = 16; // fallback; real value returned by API
  const PREFETCH_THRESHOLD = 3;

  async function loadBatch() {
    if (loading || !hasMore) return;
    loading = true;
    try {
      const res = await fetch(`/api/feed?offset=${offset}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      batchSize = data.batch_size || batchSize;
      hasMore = data.has_more;
      // Append posts
      data.posts.forEach(addCard);
      offset = data.next_offset; // advance after successful append

      // Re-attach observers to newest set
      attachObservers();

      if (!hasMore) {
        // Optional: sentinel or message
        console.debug('No more posts.');
      }
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
      return `
        <video
          autoplay
          loop
          muted
          playsinline
          controlslist="nodownload nofullscreen noplaybackrate"
          disablepictureinpicture
        >
          <source src="${escapeHtml(p.media_path)}" type="video/mp4">
        </video>`;
    }
    return `<img src="${escapeHtml(p.media_path)}" alt="Post image">`;
  }

  function escapeHtml(str = '') {
    return str.replace(/[&<>"']/g, c => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    }[c]));
  }

  // Auto play/pause videos when sufficiently in view
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

  // Prefetch next batch a few cards before end
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
    // Observe last batch for play/pause
    cards.slice(-batchSize).forEach(c => playObserver.observe(c));

    // Prefetch trigger: card that is PREFETCH_THRESHOLD from the end
    const trigger = cards[cards.length - PREFETCH_THRESHOLD];
    if (trigger) prefetchObserver.observe(trigger);
  }

  // Fallback: if user scrolls near bottom and intersection not fired
  container.addEventListener('scroll', () => {
    if (!hasMore || loading) return;
    const nearBottom = container.scrollTop + container.clientHeight >= container.scrollHeight - 200;
    if (nearBottom) loadBatch();
  });

  // Initial observers (do not load immediately; server already gave first batch)
  attachObservers();
});