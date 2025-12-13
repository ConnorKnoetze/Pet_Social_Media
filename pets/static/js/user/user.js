document.addEventListener('DOMContentLoaded', () => {
    const followBtnEl = document.getElementById('userFollowButton');
    let currentUserId = null;
    let inflight = null;

    function clear() {
        if(followBtnEl) {
          followBtnEl.style.display = 'none';
          followBtnEl.disabled = false;
          followBtnEl.textContent = 'Follow';
          if (followBtnEl.__followHandler) {
            followBtnEl.removeEventListener('click', followBtnEl.__followHandler);
            delete followBtnEl.__followHandler;
          }
        }
    }

    async function doThisFollow(id) {
        if (!id) return;
        try {
          const res = await fetch(`/follow/${encodeURIComponent(id)}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: '{}' // server doesn't require body but keep JSON to satisfy some setups
          });
          if (!res.ok) {
            if (res.status === 401) {
              // not authenticated -> go to register/login
              window.location.href = '/register';
              return;
            }
            throw new Error(`Follow failed: ${res.status}`);
          }
          if (followBtnEl) {
            followBtnEl.textContent = 'Following';
            followBtnEl.disabled = true;
          }
        } catch (err) {
          console.error('Follow request failed', err);
        }
    }

    function renderFollowButton(u) {
        if (followBtnEl) {
            const id = u.id ?? '';
            if (id) {
                if (u.id !== u.session_user_id) {
                    followBtnEl.style.display = 'inline-block';
                    followBtnEl.disabled = false;
                    if (u.following) {
                        followBtnEl.textContent = 'Following';
                    } else followBtnEl.textContent = 'Follow';
                    if (followBtnEl.__followHandler) followBtnEl.removeEventListener('click', followBtnEl.__followHandler);
                    followBtnEl.__followHandler = (e) => {
                        e.preventDefault();
                        doThisFollow(id);
                    };
                    followBtnEl.addEventListener('click', followBtnEl.__followHandler);
                }
                } else {
                if (followBtnEl.__followHandler) { followBtnEl.removeEventListener('click', followBtnEl.__followHandler); delete followBtnEl.__followHandler; }
                followBtnEl.style.display = 'none';
                followBtnEl.removeAttribute('href');
           }
        }
    }
    async function loadThisUser(id) {
        console.log('Loading user for follow button:', id);
        const uid = String(id || '');
        if (!uid || uid === currentUserId) return;
        currentUserId = uid;
        clear();
        if (inflight) try { await inflight; } catch {}
        inflight = fetch(`/api/user/${uid}`)
          .then(r => r.ok ? r.json() : Promise.reject(r.status))
          .then(data => {
            if (String(data.id) !== currentUserId) return;
            renderFollowButton(data);
          })
          .catch(err => {
            console.error('User load failed', err);
            clear();
          })
          .finally(() => { inflight = null; });
    }

    window.setActivePostUser = loadThisUser;
    window.setActivePostUserSource = 'profile';

    // -- Auto-init if server rendered the user id on the button --
    try {
      const initId = followBtnEl && followBtnEl.dataset && followBtnEl.dataset.userId;
      if (initId) {
        // call asynchronously to avoid blocking current handler
        setTimeout(() => { loadThisUser(initId); }, 0);
      }
    } catch (e) { /* ignore */ }
});