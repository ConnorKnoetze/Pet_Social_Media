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

  const link = document.createElement('a');
  link.href = `post/${encodeURIComponent(String(t.id))}`;
  link.className = 'thumb-link';
  link.setAttribute('aria-label', `View post ${t.id}`);

  if (t.media_type === 'video') {
    const video = document.createElement('video');
    video.muted = true;
    video.playsInline = true;
    video.preload = 'metadata';
    const src = document.createElement('source');
    src.src = t.media_path || '';
    src.type = 'video/mp4';
    video.appendChild(src);
    link.appendChild(video);
  } else {
    const img = document.createElement('img');
    img.src = t.media_path || '';
    img.alt = 'Post thumbnail';
    link.appendChild(img);
  }

  wrap.appendChild(link);

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