// Language: JavaScript
document.addEventListener('DOMContentLoaded', () => {
  const nameEl = document.getElementById('username');
  const userNameLinkEl = document.getElementById('usernameLink');
  const avatarEl = document.getElementById('userAvatar');
  const avatarLinkEl = document.getElementById('userAvatarLink');
  const followersEl = document.getElementById('followers');
  const bioEl = document.getElementById('bio');
  const postCountEl = document.getElementById('postCount');
  const followBtnEl = document.getElementById('followButton');
  const thumbsEl = document.getElementById('userThumbnails');
  let currentUserId = null;
  let currentUserData = null; // track the loaded user's data
  let inflight = null;

  function clear() {
    currentUserData = null;
    if (nameEl) nameEl.textContent = '';
    if (avatarEl) avatarEl.src = '';
    if (followersEl) followersEl.textContent = '';
    if (bioEl) bioEl.textContent = '';
    if (postCountEl) postCountEl.textContent = '';
    if (followBtnEl) {
      followBtnEl.style.display = 'none';
      followBtnEl.disabled = false;
      followBtnEl.textContent = 'Follow';
      if (followBtnEl.__followHandler) {
        followBtnEl.removeEventListener('click', followBtnEl.__followHandler);
        delete followBtnEl.__followHandler;
      }
    }
    if (thumbsEl) thumbsEl.innerHTML = '';
  }

  function renderThumb(t) {
    const wrap = document.createElement('div');
    wrap.className = 'thumb' + (t.media_type === 'video' ? ' video' : '');
    wrap.dataset.postId = t.id;

    const link = document.createElement('a');
    link.href = `/post/${encodeURIComponent(String(t.id))}`;
    link.className = 'thumb-link';
    link.setAttribute('aria-label', `View post ${t.id}`);
    link.addEventListener('click', (e) => {
      e.preventDefault();
      window.location.href = `/post/${encodeURIComponent(String(t.id))}`;
    });

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

  async function doFollow(id) {
    if (!id) return;
    try {
      const res = await fetch(`/follow/${encodeURIComponent(id)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: '{}'
      });
      if (!res.ok) {
        if (res.status === 401) { window.location.href = '/register'; return; }
        throw new Error(`Follow failed: ${res.status}`);
      }
      const data = await res.json();
      // update UI and local state
      if (followersEl) followersEl.textContent = `Followers: ${data.followers_count ?? 0}`;
      if (followBtnEl) {
        followBtnEl.textContent = 'Following';
        followBtnEl.disabled = false; // keep enabled for toggle
      }
      if (currentUserData) currentUserData.following = true;
    } catch (err) {
      console.error('Follow request failed', err);
    }
  }

  async function doUnfollow(id) {
    if (!id) return;
    try {
      const res = await fetch(`/unfollow/${encodeURIComponent(id)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: '{}'
      });
      if (!res.ok) {
        if (res.status === 401) { window.location.href = '/register'; return; }
        throw new Error(`Unfollow failed: ${res.status}`);
      }
      const data = await res.json();
      // update UI and local state
      if (followersEl) followersEl.textContent = `Followers: ${data.followers_count ?? 0}`;
      if (followBtnEl) {
        followBtnEl.textContent = 'Follow';
        followBtnEl.disabled = false;
      }
      if (currentUserData) currentUserData.following = false;
    } catch (err) {
      console.error('Unfollow request failed', err);
    }
  }

  function renderUser(u) {
    currentUserData = u;
    if (!u) return clear();
    if (userNameLinkEl) userNameLinkEl.href = `/user/${u.username || ''}`;
    if (nameEl) nameEl.textContent = u.username || 'Unknown';
    if (avatarLinkEl) avatarLinkEl.href = `/user/${u.username || ''}`;
    if (avatarEl) {
      avatarEl.src = u.profile_picture_path || '';
      avatarEl.alt = (u.username || 'User') + ' avatar';
    }
    if (followersEl) followersEl.textContent = `Followers: ${u.followers_count ?? 0}`;
    if (bioEl) bioEl.textContent = u.bio || '';
    if (postCountEl) postCountEl.textContent = `Posts: ${u.posts_count ?? 0}`;

    if (followBtnEl) {
      const id = u.id ?? '';
      if (id && u.id !== u.session_user_id) {
        followBtnEl.style.display = 'inline-block';
        followBtnEl.disabled = false;
        followBtnEl.textContent = u.following ? 'Following' : 'Follow';
        if (followBtnEl.__followHandler) followBtnEl.removeEventListener('click', followBtnEl.__followHandler);
        followBtnEl.__followHandler = (e) => {
          e.preventDefault();
          const targetId = currentUserData?.id || id;
          if (!currentUserData?.following) {
            doFollow(targetId);
          } else {
            doUnfollow(targetId);
          }
        };
        followBtnEl.addEventListener('click', followBtnEl.__followHandler);
      } else {
        if (followBtnEl.__followHandler) {
          followBtnEl.removeEventListener('click', followBtnEl.__followHandler);
          delete followBtnEl.__followHandler;
        }
        followBtnEl.style.display = 'none';
        followBtnEl.removeAttribute('href');
      }
    }

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

  window.setActivePostUser = window.setActivePostUser || loadUser;
});