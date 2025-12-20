document.addEventListener('DOMContentLoaded', () => {
  const listEl = document.getElementById('commentsList');
  let currentPostId = null;
  let inflight = null;
  const form = document.getElementById('commentForm');
  const textarea = document.getElementById('commentText');
  const submitBtn = document.getElementById('commentSubmit');
  const statusEl = document.getElementById('commentStatus');

  function timeago(iso) {
    if (!iso) return '';
    const dt = new Date(iso);
    if (isNaN(dt)) return '';
    const now = new Date();
    const diffSec = (now - dt) / 1000;
    if (diffSec < 60) return 'Just now';
    const mins = diffSec / 60; if (mins < 60) return `${Math.floor(mins)}m`;
    const hrs = mins / 60; if (hrs < 24) return `${Math.floor(hrs)}h`;
    const days = hrs / 24; if (days < 7) return `${Math.floor(days)}d`;
    const d = dt.getDate().toString().padStart(2,'0');
    const m = (dt.getMonth()+1).toString().padStart(2,'0');
    const y = dt.getFullYear().toString().slice(-2);
    return `${d}/${m}/${y}`;
  }

  function escapeHtml(str='') {
    return str.replace(/[&<>"']/g, ch => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[ch]));
  }

  function renderSkeleton(count=4) {
    if (!listEl) return;
    listEl.setAttribute('aria-busy','true');
    listEl.innerHTML = Array.from({length: count}).map(() => (
      `<li class="comment-skel">
        <div class="skel-avatar"></div>
        <div>
          <div class="skel-line" style="width:60%"></div>
          <div class="skel-line"></div>
          <div class="skel-line" style="width:40%"></div>
        </div>
        <div class="skel-like"></div>
      </li>`
    )).join('');
  }

  function renderEmpty(msg='No comments.') {
    listEl.setAttribute('aria-busy','false');
    listEl.innerHTML = `<li class="comment-item empty">${escapeHtml(msg)}</li>`;
  }

  function avatarMarkup(username, profilePath) {
    if (profilePath) {
      return `<div class="comment-avatar"><a href="user/${username}"><img src="${escapeHtml(profilePath)}" alt="${escapeHtml(username)} avatar"></a></div>`;
    }
    const letter = (username||'?').charAt(0).toUpperCase();
    return `<div class="comment-avatar" aria-hidden="true">${escapeHtml(letter)}</div>`;
  }

  function buildCommentHTML(c) {
    const author = c.author || 'Anonymous';
    const text = c.text || c.comment_string || '';
    const created = c.created_at || '';
    const profile = c.profile_picture_path || '';
    const likes = typeof c.likes === 'number' ? c.likes : 0;
    // include data-comment-id if available
    const commentIdAttr = c.id ? `data-comment-id="${escapeHtml(String(c.id))}"` : '';
    return `<li class="comment-item" data-user-id="${escapeHtml(String(c.user_id||''))}" ${commentIdAttr}>
        ${avatarMarkup(author, profile)}
        <div class="comment-body">
          <div class="comment-author">${escapeHtml(author)}</div>
          <p class="comment-text">${escapeHtml(text)}</p>
          <div class="comment-meta"><time datetime="${escapeHtml(created)}">${escapeHtml(timeago(created))}</time><span class="comment-likes" aria-label="${likes} likes">${likes}❤</span></div>
        </div>
        <div class="comment-actions">
          <button class="comment-like" type="button" aria-label="Like comment">Like</button>
        </div>
      </li>`;
  }

  function renderComments(comments) {
    if (!comments.length) return renderEmpty();
    listEl.setAttribute('aria-busy','false');
    listEl.innerHTML = comments.map(buildCommentHTML).join('');
  }

  async function loadComments(postId) {
    const pid = String(postId || '');
    if (!pid || pid === currentPostId) return;
    currentPostId = pid;
    renderSkeleton();
    if (inflight) try { await inflight; } catch {}
    inflight = fetch(`/api/comments/${pid}`)
      .then(r => r.ok ? r.json() : Promise.reject(r.status))
      .then(data => {
        if (String(data.post_id) !== currentPostId) return; // stale
        renderComments(data.comments || []);
      })
      .catch(err => {
        console.error('Comments load failed', err);
        if (currentPostId === pid) renderEmpty('Failed to load.');
      })
      .finally(() => { inflight = null; });
  }


  // Like handler: send POST to backend to add like to comment
  listEl.addEventListener('click', async e => {
    const btn = e.target.closest('.comment-like');
    if (!btn) return;
    const item = btn.closest('.comment-item');
    if (!item) return;
    const likesEl = item.querySelector('.comment-likes');
    if (!likesEl) return;

    const commentId = item.dataset && item.dataset.commentId;
    const postId = currentPostId;
    if (!postId) {
      console.error('Cannot like comment: no active post selected');
      return;
    }
    if (!commentId) {
      // Server response may not include comment id - log and do optimistic local update
      console.warn('Comment id missing; performing optimistic local like');
      let num = parseInt(likesEl.textContent) || 0;
      num += 1;
      likesEl.textContent = `${num}❤`;
      btn.disabled = true;
      btn.textContent = 'Liked';
      return;
    }

    // optimistic UI
    const originalText = btn.textContent;
    const originalDisabled = btn.disabled;
    let originalCount = parseInt(likesEl.textContent) || 0;
    const newCount = originalCount + 1;
    likesEl.textContent = `${newCount}❤`;
    btn.disabled = true;
    btn.textContent = 'Liked';

    try {
      const res = await fetch(`/api/post/${encodeURIComponent(postId)}/comment/${encodeURIComponent(commentId)}`, {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
        body: JSON.stringify({}) // backend ignores body
      });

      if (!res.ok) {
        // try to read server error message
        const errBody = await res.json().catch(()=>null);
        const msg = errBody && errBody.error ? errBody.error : `HTTP ${res.status}`;
        throw new Error(msg);
      }

      // success: server doesn't return new like count currently; keep optimistic or adjust if server provides data
      const data = await res.json().catch(()=>null);
      if (data && typeof data.likes === 'number') {
        likesEl.textContent = `${data.likes}❤`;
      }
    } catch (err) {
      console.error('Failed to like comment', err);
      // revert optimistic UI
      likesEl.textContent = `${originalCount}❤`;
      btn.disabled = originalDisabled;
      btn.textContent = originalText;
    }
  });

  function setStatus(msg='', type='info') {
    if (!statusEl) return;
    statusEl.textContent = msg;
    statusEl.dataset.type = type;
  }

  form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!currentPostId) {
      setStatus('Select a post first', 'warn');
      return;
    }
    const text = (textarea?.value || '').trim();
    if (!text) {
      setStatus('Cannot post empty comment', 'error');
      return;
    }
    if (text.length > 500) {
      setStatus('Too long (500 max)', 'error');
      return;
    }
    submitBtn.disabled = true;
    setStatus('Posting...');
    try {
      const res = await fetch(`/api/comments/${currentPostId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      if (!res.ok) {
        const err = await res.json().catch(()=>({error:'Failed'}));
        throw new Error(err.error || `HTTP ${res.status}`);
      }
      const data = await res.json();
      const c = data.comment;
      // Prepend new comment
      if (listEl.querySelector('.empty')) listEl.innerHTML = '';
      listEl.insertAdjacentHTML('afterbegin', buildCommentHTML(c));
      textarea.value = '';
      setStatus('Posted', 'success');

      // Update comments counter on the post card
      const card = document.querySelector(`.short-card[data-id="${currentPostId}"]`);
      if (card) {
        const commentCounter = card.querySelector('.engagement-item:nth-child(2)');
        if (commentCounter) {
          let count = parseInt(commentCounter.textContent) || 0;
          commentCounter.textContent = `💬 ${count + 1}`;
        }
      }
    } catch (err) {
      console.error(err);
      setStatus(err.message || 'Failed', 'error');
    } finally {
      submitBtn.disabled = false;
    }
  });

  window.setActivePostComments = loadComments;
});