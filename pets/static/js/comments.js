document.addEventListener('DOMContentLoaded', () => {
  const listEl = document.getElementById('commentsList');
  let currentPostId = null;
  let inflight = null;

  function renderLoading() {
    if (!listEl) return;
    listEl.innerHTML = '<li class="empty">Loading...</li>';
  }
  function renderEmpty() {
    listEl.innerHTML = '<li class="empty">No comments.</li>';
  }
  function renderComments(comments) {
    if (!comments.length) return renderEmpty();
    listEl.innerHTML = comments.map(c => {
      const author = c.author || 'Anonymous';
      const text = c.text || c.comment_string || '';
      const created = c.created_at || '';
      return `<li><strong>${escapeHtml(author)}</strong>: ${escapeHtml(text)}<small>${escapeHtml(created)}</small></li>`;
    }).join('');
  }
  function escapeHtml(str='') {
    return str.replace(/[&<>"']/g, ch => ({
      '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
    }[ch]));
  }

  async function loadComments(postId) {
    const pid = String(postId || '');
    if (!pid || pid === currentPostId) return;
    currentPostId = pid;
    renderLoading();
    if (inflight) try { await inflight; } catch {}
    inflight = fetch(`/api/comments/${pid}`)
      .then(r => r.ok ? r.json() : Promise.reject(r.status))
      .then(data => {
        console.log('Comments response', data);
        if (String(data.post_id) !== currentPostId) return;
        renderComments(data.comments || []);
      })
      .catch(err => {
        console.error('Comments load failed', err);
        if (currentPostId === pid)
          listEl.innerHTML = '<li class="empty">Failed to load.</li>';
      })
      .finally(() => { inflight = null; });
  }

  window.setActivePostComments = loadComments;
});