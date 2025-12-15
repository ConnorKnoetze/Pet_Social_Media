// javascript
document.addEventListener('DOMContentLoaded', () => {
    const followBtnEl = document.getElementById('userFollowButton');
    // try several common selectors for the followers count element
    const followersEl = document.getElementById('followers')
      || document.getElementById('userFollowers')
      || document.getElementById('userFollowersCount')
      || document.querySelector('[data-user-followers]');
    let currentUserId = null;
    let inflight = null;
    let currentUserData = null;

    function clear() {
        // DO NOT redeclare currentUserData (no "let" here)
        currentUserData = null;
        if (followBtnEl) {
          followBtnEl.style.display = 'none';
          followBtnEl.disabled = false;
          followBtnEl.textContent = 'Follow';
          if (followBtnEl.__followHandler) {
            followBtnEl.removeEventListener('click', followBtnEl.__followHandler);
            delete followBtnEl.__followHandler;
          }
        }
    }

    async function fetchUserData(id) {
        try {
            const r = await fetch(`/api/user/${encodeURIComponent(id)}`);
            if (!r.ok) return null;
            return await r.json();
        } catch (e) {
            console.error('fetchUserData failed', e);
            return null;
        }
    }

    function updateFollowersCountFromResp(dataOrCount) {
        if (!followersEl) return;
        let count = null;
        if (dataOrCount == null) return;
        if (typeof dataOrCount === 'number') count = dataOrCount;
        else if (typeof dataOrCount === 'object') {
            if (dataOrCount.followers_count != null) count = dataOrCount.followers_count;
            else if (dataOrCount.delta != null && currentUserData && typeof currentUserData.followers_count === 'number') {
                count = currentUserData.followers_count + dataOrCount.delta;
            }
        }
        if (count == null) return;
        followersEl.textContent = `Followers: ${count}`;
        if (currentUserData) currentUserData.followers_count = count;
    }

    async function doThisFollow(id) {
        if (!id || !followBtnEl) return;
        followBtnEl.disabled = true;
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
            // if server didn't include followers_count, fetch the user object as fallback
            if (data.followers_count == null) {
                const fresh = await fetchUserData(id);
                if (fresh && fresh.followers_count != null) data.followers_count = fresh.followers_count;
                else console.warn('follow response missing followers_count and fetchUserData failed');
            }
            updateFollowersCountFromResp(data);
            if (currentUserData) {
                currentUserData.following = true;
                currentUserData.followers_count = data.followers_count ?? currentUserData.followers_count;
            }
            const renderArg = Object.assign({}, currentUserData || {}, { id, following: true, followers_count: data.followers_count });
            renderUnfollowButton(renderArg);
        } catch (err) {
            console.error('Follow request failed', err);
        } finally {
            if (followBtnEl) followBtnEl.disabled = false;
        }
    }

    function renderFollowButton(u) {
        currentUserData = u;
        if (followBtnEl) {
            const id = u.id ?? '';
            if (id) {
                if (u.id !== u.session_user_id) {
                    followBtnEl.style.display = 'inline-block';
                    followBtnEl.disabled = false;
                    followBtnEl.textContent = u.following ? 'Following' : 'Follow';
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

    async function doThisUnfollow(id) {
        if (!id || !followBtnEl) return;
        followBtnEl.disabled = true;
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
            if (data.followers_count == null) {
                const fresh = await fetchUserData(id);
                if (fresh && fresh.followers_count != null) data.followers_count = fresh.followers_count;
                else console.warn('unfollow response missing followers_count and fetchUserData failed');
            }
            updateFollowersCountFromResp(data);
            if (currentUserData) {
                currentUserData.following = false;
                currentUserData.followers_count = data.followers_count ?? currentUserData.followers_count;
            }
            const renderArg = Object.assign({}, currentUserData || {}, { id, following: false, followers_count: data.followers_count });
            renderFollowButton(renderArg);
        } catch (err) {
            console.error('Unfollow request failed', err);
        } finally {
            if (followBtnEl) followBtnEl.disabled = false;
        }
    }

    function renderUnfollowButton(u) {
        currentUserData = u;
        if (followBtnEl) {
            const id = u.id ?? '';
            if (id) {
                if (u.id !== u.session_user_id) {
                    followBtnEl.style.display = 'inline-block';
                    followBtnEl.disabled = false;
                    followBtnEl.textContent = u.following ? 'Following' : 'Follow';
                    if (followBtnEl.__followHandler) followBtnEl.removeEventListener('click', followBtnEl.__followHandler);
                    followBtnEl.__followHandler = (e) => {
                        e.preventDefault();
                        doThisUnfollow(id);
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

    function renderEditProfileButton(u) {
        if (followBtnEl) {
            followBtnEl.style.display = 'inline-block';
            followBtnEl.disabled = false;
            followBtnEl.textContent = 'Edit Profile';
            followBtnEl.removeAttribute('href');
            if (followBtnEl.__followHandler) {
                followBtnEl.removeEventListener('click', followBtnEl.__followHandler);
                delete followBtnEl.__followHandler;
            }
            followBtnEl.__followHandler = (e) => {
                e.preventDefault();
                window.location.href = `/${u.id}/settings`;
            };
            followBtnEl.addEventListener('click', followBtnEl.__followHandler);
        }
    }

    async function loadThisUser(id) {
        const uid = String(id || '');
        if (!uid || uid === currentUserId) return;
        currentUserId = uid;
        clear();
        if (inflight) try { await inflight; } catch {}
        inflight = fetch(`/api/user/${uid}`)
          .then(r => r.ok ? r.json() : Promise.reject(r.status))
          .then(data => {
            if (String(data.id) !== currentUserId) return;
            if (data.id !== data.session_user_id) {
                if (data.following) {
                    renderUnfollowButton(data);
                } else renderFollowButton(data);
            }
            else renderEditProfileButton(data);
            // ensure followers count shown on initial load
            updateFollowersCountFromResp(data);
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