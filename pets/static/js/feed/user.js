document.addEventListener('DOMContentLoaded', () => {
  const nameEl = document.getElementById('username');
  const userNameLinkEl = document.getElementById('usernameLink');
  const avatarEl = document.getElementById('userAvatar');
  const avatarLinkEl = document.getElementById('userAvatarLink');
  const followersEl = document.getElementById('followers');
  const bioEl = document.getElementById('bio');
  const postCountEl = document.getElementById('postCount');
  const thumbsEl = document.getElementById('userThumbnails');
  let currentUserId = null;
  let inflight = null;

  function clear() {
    if (nameEl) nameEl.textContent = '';
    if (avatarEl) avatarEl.src = '';
    if (followersEl) followersEl.textContent = '';
    if (bioEl) bioEl.textContent = '';
    if (postCountEl) postCountEl.textContent = '';
    if (thumbsEl) thumbsEl.innerHTML = '';
  }

  function escapeHtml(str='') {
    return str.replace(/[&<>"']/g, ch => ({
      '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
    }[ch]));
  }

  function renderThumb(t) {
    const wrap = document.createElement('div');
    wrap.className = 'thumb' + (t.media_type === 'video' ? ' video' : '');
    wrap.dataset.postId = t.id;
    if (t.media_type === 'video') {
      wrap.innerHTML = `<video muted playsinline preload="metadata">
         <source src="${escapeHtml(t.media_path)}" type="video/mp4">
       </video>`;
     } else {
      wrap.innerHTML = `<img src="${escapeHtml(t.media_path)}" alt="Post thumbnail">`;
    }
    wrap.addEventListener('click', () => {
      // Optional: scroll to that post if present in feed
      const target = document.querySelector(`.short-card[data-id="${t.id}"]`);
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    return wrap;
  }

  function renderUser(u) {
    if (!u) return clear();
    if (userNameLinkEl) {
      userNameLinkEl.href = `/user/${u.username || ''}`;
    }
    if (nameEl) nameEl.textContent = u.username || 'Unknown';
    if (avatarLinkEl) {
        avatarLinkEl.href = `/user/${u.username || ''}`;
    }
    if (avatarEl) {
      avatarEl.src = u.profile_picture_path || '';
      avatarEl.alt = (u.username || 'User') + ' avatar';
    }
    if (followersEl) followersEl.textContent = `Followers: ${u.followers_count ?? 0}`;
    if (bioEl) bioEl.textContent = u.bio || '';
    if (postCountEl) postCountEl.textContent = `Posts: ${u.posts_count ?? 0}`;
    if (thumbsEl) {
      const thumbs = (u.posts_thumbnails || []).map(renderThumb);
      thumbsEl.innerHTML = '';
      thumbs.forEach(el => thumbsEl.appendChild(el));
    }
  }

  async function loadUser(id) {
    const uid = String(id || '');
    if (!uid || uid === currentUserId) return;
    currentUserId = uid;
    clear();
    if (inflight) try { await inflight; } catch {}
    inflight = fetch(`/api/user/${uid}`)
      .then(r => r.ok ? r.json() : Promise.reject(r.status))
      .then(data => {
        if (String(data.id) !== currentUserId) return;
        renderUser(data);
      })
      .catch(err => {
        console.error('User load failed', err);
        clear();
      })
      .finally(() => { inflight = null; });
  }

  window.setActivePostUser = loadUser;
});